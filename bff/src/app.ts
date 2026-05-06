import express, { Request, Response, NextFunction } from 'express';
import { createServer } from 'http';
import cors from 'cors';
import helmet from 'helmet';
import { v4 as uuidv4 } from 'uuid';
import { config } from './config';
import { sessionMiddleware, validateSession, redisClient } from './middleware/session';
import { initializeKeycloakClient, exchangeCodeForTokens } from './auth/keycloak';
import { logger, requestLogger } from './utils/logger';
import apiRouter from './routes/api';
import { initializeWebSocket, getWebSocketHealth, shutdownWebSocket } from './websocket/server';
import { initializePubSub, getPubSubHealth, shutdownPubSub } from './events/pubsub';
import { initializeIngestionHandlers } from './websocket/handlers/ingestion';
import { getCacheMetrics } from './cache/redis-cache';

const app = express();

// Request tracing middleware - must be first
app.use((req: Request, _res: Response, next: NextFunction) => {
  (req as any).trace_id = uuidv4();
  next();
});

// Security middleware
app.use(helmet({
  contentSecurityPolicy: false, // Disable for development, enable in production
}));

// CORS configuration - Allow all localhost ports for micro-frontends
const allowedOrigins = [
  'http://localhost:5100',  // Shell
  'http://localhost:5101',  // Domains UI
  'http://localhost:5102',  // Ingestion UI  
  'http://localhost:5103',  // Search UI
  'http://localhost:5104',  // Admin UI
  ...(config.corsOrigins || [])
];

app.use(cors({
  origin: function(origin, callback) {
    // Allow requests with no origin (like mobile apps or curl requests)
    if (!origin) return callback(null, true);
    
    if (allowedOrigins.indexOf(origin) !== -1 || config.nodeEnv === 'development') {
      callback(null, true);
    } else {
      callback(new Error('Not allowed by CORS'));
    }
  },
  credentials: true,
  methods: ['GET', 'POST', 'PUT', 'DELETE', 'OPTIONS'],
  allowedHeaders: ['Content-Type', 'Authorization', 'X-Trace-Id', 'Cookie'],
  exposedHeaders: ['X-Trace-Id'],
}));

// Body parsing
app.use(express.json());
app.use(express.urlencoded({ extended: true }));

// Session middleware (Redis-backed)
app.use(sessionMiddleware);

// Request logging middleware
app.use(requestLogger);

// Health check endpoint
app.get('/health', async (_req: Request, res: Response) => {
  const redisHealthy = redisClient.status === 'ready' || redisClient.status === 'connecting';
  const pubsubHealth = getPubSubHealth();
  const wsHealth = getWebSocketHealth();
  const cacheMetrics = getCacheMetrics();
  
  res.json({
    service: 'bff',
    status: 'healthy',
    timestamp: new Date().toISOString(),
    redis: redisHealthy ? 'connected' : 'disconnected',
    pubsub: pubsubHealth,
    websocket: wsHealth,
    cache: {
      hitRate: `${cacheMetrics.hitRate}%`,
      hits: cacheMetrics.hits,
      misses: cacheMetrics.misses,
    },
  });
});

// Auth routes
app.get('/auth/login', async (req: Request, res: Response) => {
  const trace_id = (req as any).trace_id || 'unknown';
  try {
    const client = await initializeKeycloakClient();
    const state = uuidv4();

    (req.session as any).oauthState = state;

    const authorizationUrl = client.authorizationUrl({
      scope: 'openid email profile',
      state,
    });

    // Flush the session to Redis BEFORE redirecting.
    // Without save(), the async write may not complete before the browser
    // follows the redirect and the callback arrives with no oauthState.
    req.session.save((err) => {
      if (err) {
        logger.error('Session save failed before login redirect', { trace_id, error: err.message });
        res.status(500).json({ error: 'Session initialization failed' });
        return;
      }
      logger.info('Redirecting to Keycloak', { trace_id, state });
      res.redirect(authorizationUrl);
    });
  } catch (error) {
    logger.error('Login error', { trace_id, error: (error as Error).message });
    res.status(500).json({ error: 'Authentication initialization failed' });
  }
});

app.get('/auth/callback', async (req: Request, res: Response) => {
  const trace_id = (req as any).trace_id || 'unknown';
  
  try {
    const { code, state } = req.query;
    const savedState = (req.session as any).oauthState;
    
    // Verify state to prevent CSRF
    if (!state || state !== savedState) {
      logger.warn('Invalid OAuth state', { trace_id, state, savedState });
      res.status(400).json({ error: 'Invalid state parameter' });
      return;
    }
    
    if (!code || typeof code !== 'string') {
      res.status(400).json({ error: 'Authorization code missing' });
      return;
    }
    
    // Exchange code for tokens
    const tokens = await exchangeCodeForTokens(code);
    
    // Clear state from session
    delete (req.session as any).oauthState;
    
    // Store user session — all fields come from the verified Keycloak token
    (req.session as any).user = {
      id: tokens.userInfo.sub,
      email: tokens.userInfo.email,
      roles: tokens.userInfo.roles,
      accessToken: tokens.accessToken,
      refreshToken: tokens.refreshToken,
    };

    logger.info('User authenticated successfully', {
      trace_id,
      email: tokens.userInfo.email,
      roles: tokens.userInfo.roles,
    });

    // Flush session before redirecting for the same reason as /auth/login
    req.session.save((err) => {
      if (err) {
        logger.error('Session save failed after token exchange', { trace_id, error: err.message });
        res.redirect(`${config.frontendUrl}/auth/callback?error=session_save_failed`);
        return;
      }
      res.redirect(`${config.frontendUrl}/auth/callback?success=true`);
    });
  } catch (error) {
    logger.error('Callback error', { trace_id, error: (error as Error).message });
    res.redirect(`${config.frontendUrl}/auth/callback?error=authentication_failed`);
  }
});

app.get('/auth/logout', async (req: Request, res: Response) => {
  const trace_id = (req as any).trace_id || 'unknown';
  
  try {
    // Destroy session
    req.session.destroy((err) => {
      if (err) {
        logger.error('Session destruction error', { trace_id, error: err.message });
      }
    });
    
    logger.info('User logged out', { trace_id });
    
    // Redirect to Keycloak logout
    const keycloakLogoutUrl = `${config.keycloak.url}/realms/${config.keycloak.realm}/protocol/openid-connect/logout`;
    res.redirect(`${keycloakLogoutUrl}?redirect_uri=${encodeURIComponent(config.frontendUrl)}`);
  } catch (error) {
    logger.error('Logout error', { trace_id, error: (error as Error).message });
    res.status(500).json({ error: 'Logout failed' });
  }
});

app.get('/auth/session', (req: Request, res: Response) => {
  // Dev bypass: return mock session without validating
  if (process.env.BYPASS_AUTH === 'true') {
    res.json({
      authenticated: true,
      user: {
        id: 'dev-user-00000000-0000-0000-0000-000000000000',
        email: 'dev@localhost',
        roles: ['KM_ADMIN'],
      },
    });
    return;
  }

  // Normal flow: validate session first
  validateSession(req, res, () => {
    const user = req.user;
    
    if (!user) {
      res.status(401).json({ error: 'Not authenticated' });
      return;
    }
    
    // Return user info (without tokens - they stay server-side)
    res.json({
      authenticated: true,
      user: {
        id: user.id,
        email: user.email,
        roles: user.roles,
      },
    });
  });
});

// API routes - proxy to Core API with JWT injection
app.use('/api', apiRouter);

// Global error handler
app.use((err: Error, req: Request, res: Response, _next: NextFunction) => {
  const trace_id = (req as any).trace_id || 'unknown';
  
  logger.error('Unhandled error', {
    trace_id,
    error: err.message,
    stack: err.stack,
  });
  
  // Don't leak error details in production
  const message = config.nodeEnv === 'production' 
    ? 'Internal server error' 
    : err.message;
  
  res.status(500).json({ 
    error: message,
    trace_id,
    ...(config.nodeEnv !== 'production' && { stack: err.stack }),
  });
});

// 404 handler
app.use((_req: Request, res: Response) => {
  res.status(404).json({ error: 'Not found' });
});

// Create HTTP server
const httpServer = createServer(app);

// Start server
const PORT = config.port;

httpServer.listen(PORT, async () => {
  logger.info(`BFF server running on port ${PORT}`);
  logger.info(`Environment: ${config.nodeEnv}`);
  
  try {
    // Initialize Keycloak client
    await initializeKeycloakClient();
    logger.info('Keycloak client ready');
    
    // Initialize Redis pub/sub
    await initializePubSub();
    logger.info('Redis pub/sub initialized');
    
    // Initialize WebSocket server
    initializeWebSocket(httpServer);
    logger.info('WebSocket server initialized');
    
    // Initialize ingestion event handlers
    await initializeIngestionHandlers();
    logger.info('Ingestion event handlers initialized');
    
    logger.info('All services initialized successfully');
  } catch (error) {
    logger.error('Failed to initialize services on startup', { error: (error as Error).message });
    // Don't exit - server can still serve health checks
  }
});

// Graceful shutdown
process.on('SIGTERM', async () => {
  logger.info('SIGTERM received, shutting down gracefully...');
  
  // Close HTTP server
  httpServer.close(() => {
    logger.info('HTTP server closed');
  });
  
  // Shutdown WebSocket
  await shutdownWebSocket();
  
  // Shutdown pub/sub
  await shutdownPubSub();
  
  logger.info('Shutdown complete');
  process.exit(0);
});

process.on('SIGINT', async () => {
  logger.info('SIGINT received, shutting down gracefully...');
  
  httpServer.close(() => {
    logger.info('HTTP server closed');
  });
  
  await shutdownWebSocket();
  await shutdownPubSub();
  
  logger.info('Shutdown complete');
  process.exit(0);
});

export default app;
export { httpServer };

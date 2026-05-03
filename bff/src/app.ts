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

// CORS configuration
app.use(cors({
  origin: config.corsOrigins.length > 0 ? config.corsOrigins : true,
  credentials: true,
  methods: ['GET', 'POST', 'PUT', 'DELETE', 'OPTIONS'],
  allowedHeaders: ['Content-Type', 'Authorization', 'X-Trace-Id'],
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
  try {
    const client = await initializeKeycloakClient();
    const state = uuidv4();
    
    // Store state in session for CSRF protection
    (req.session as any).oauthState = state;
    
    const authorizationUrl = client.authorizationUrl({
      scope: 'openid email profile',
      state,
    });
    
    logger.info('Redirecting to Keycloak', { trace_id: (req as any).trace_id, state });
    res.redirect(authorizationUrl);
  } catch (error) {
    logger.error('Login error', { trace_id: (req as any).trace_id, error: (error as Error).message });
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
    
    // Store user session (tokens are server-side, never exposed to browser)
    (req.session as any).user = {
      id: uuidv4(), // Will be replaced with actual user ID from token
      email: 'user@example.com', // Will be extracted from ID token
      roles: ['km-reader'], // Will be extracted from access token
      accessToken: tokens.accessToken,
      refreshToken: tokens.refreshToken,
    };
    
    logger.info('User authenticated successfully', { trace_id });
    
    // Redirect to frontend
    const redirectUrl = config.corsOrigins[0] || 'http://localhost:5173';
    res.redirect(`${redirectUrl}/auth/callback?success=true`);
  } catch (error) {
    logger.error('Callback error', { trace_id, error: (error as Error).message });
    const redirectUrl = config.corsOrigins[0] || 'http://localhost:5173';
    res.redirect(`${redirectUrl}/auth/callback?error=authentication_failed`);
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
    const redirectUrl = config.corsOrigins[0] || 'http://localhost:5173';
    
    res.redirect(`${keycloakLogoutUrl}?redirect_uri=${encodeURIComponent(redirectUrl)}`);
  } catch (error) {
    logger.error('Logout error', { trace_id, error: (error as Error).message });
    res.status(500).json({ error: 'Logout failed' });
  }
});

app.get('/auth/session', validateSession, (req: Request, res: Response) => {
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

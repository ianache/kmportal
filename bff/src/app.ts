import express, { Request, Response, NextFunction } from 'express';
import cors from 'cors';
import helmet from 'helmet';
import { v4 as uuidv4 } from 'uuid';
import { config } from './config';
import { sessionMiddleware, validateSession, redisClient } from './middleware/session';
import { initializeKeycloakClient, exchangeCodeForTokens } from './auth/keycloak';

const app = express();

// Security middleware
app.use(helmet({
  contentSecurityPolicy: false, // Disable for development, enable in production
}));

// CORS configuration
app.use(cors({
  origin: config.corsOrigins.length > 0 ? config.corsOrigins : true,
  credentials: true,
  methods: ['GET', 'POST', 'PUT', 'DELETE', 'OPTIONS'],
  allowedHeaders: ['Content-Type', 'Authorization'],
}));

// Body parsing
app.use(express.json());
app.use(express.urlencoded({ extended: true }));

// Session middleware (Redis-backed)
app.use(sessionMiddleware);

// Health check endpoint
app.get('/health', async (_req: Request, res: Response) => {
  const redisHealthy = redisClient.status === 'ready' || redisClient.status === 'connecting';
  
  res.json({
    service: 'bff',
    status: 'healthy',
    timestamp: new Date().toISOString(),
    redis: redisHealthy ? 'connected' : 'disconnected',
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
    
    console.log(`Redirecting to Keycloak: ${authorizationUrl}`);
    res.redirect(authorizationUrl);
  } catch (error) {
    console.error('Login error:', error);
    res.status(500).json({ error: 'Authentication initialization failed' });
  }
});

app.get('/auth/callback', async (req: Request, res: Response) => {
  try {
    const { code, state } = req.query;
    const savedState = (req.session as any).oauthState;
    
    // Verify state to prevent CSRF
    if (!state || state !== savedState) {
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
    
    console.log('User authenticated successfully');
    
    // Redirect to frontend
    const redirectUrl = config.corsOrigins[0] || 'http://localhost:5173';
    res.redirect(`${redirectUrl}/auth/callback?success=true`);
  } catch (error) {
    console.error('Callback error:', error);
    const redirectUrl = config.corsOrigins[0] || 'http://localhost:5173';
    res.redirect(`${redirectUrl}/auth/callback?error=authentication_failed`);
  }
});

app.get('/auth/logout', async (req: Request, res: Response) => {
  try {
    // Destroy session
    req.session.destroy((err) => {
      if (err) {
        console.error('Session destruction error:', err);
      }
    });
    
    // Redirect to Keycloak logout
    const keycloakLogoutUrl = `${config.keycloak.url}/realms/${config.keycloak.realm}/protocol/openid-connect/logout`;
    const redirectUrl = config.corsOrigins[0] || 'http://localhost:5173';
    
    res.redirect(`${keycloakLogoutUrl}?redirect_uri=${encodeURIComponent(redirectUrl)}`);
  } catch (error) {
    console.error('Logout error:', error);
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

// Protected API routes (will be implemented in Plan 05-02)
app.use('/api', validateSession, (_req: Request, res: Response) => {
  res.json({ message: 'API proxy routes will be implemented in Plan 05-02' });
});

// Global error handler
app.use((err: Error, _req: Request, res: Response, _next: NextFunction) => {
  console.error('Unhandled error:', err);
  
  // Don't leak error details in production
  const message = config.nodeEnv === 'production' 
    ? 'Internal server error' 
    : err.message;
  
  res.status(500).json({ 
    error: message,
    ...(config.nodeEnv !== 'production' && { stack: err.stack }),
  });
});

// 404 handler
app.use((_req: Request, res: Response) => {
  res.status(404).json({ error: 'Not found' });
});

// Start server
const PORT = config.port;

app.listen(PORT, async () => {
  console.log(`BFF server running on port ${PORT}`);
  console.log(`Environment: ${config.nodeEnv}`);
  
  try {
    // Initialize Keycloak client on startup
    await initializeKeycloakClient();
    console.log('Keycloak client ready');
  } catch (error) {
    console.error('Failed to initialize Keycloak client on startup:', error);
    // Don't exit - server can still serve health checks
  }
});

export default app;

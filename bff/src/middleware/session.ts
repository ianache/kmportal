import session from 'express-session';
import { Request, Response, NextFunction } from 'express';
import Redis from 'ioredis';
import RedisStore from 'connect-redis';
import { config } from '../config';

// Initialize Redis client
export const redisClient = new Redis(config.redisUrl);

redisClient.on('error', (err) => {
  console.error('Redis connection error:', err);
});

redisClient.on('connect', () => {
  console.log('Redis connected successfully');
});

// Create Redis store for sessions
const redisStore = new RedisStore({
  client: redisClient,
  prefix: 'bff:session:',
});

// Session middleware configuration
export const sessionMiddleware = session({
  store: redisStore,
  secret: config.session.secret,
  name: 'bff.sid',
  resave: false,
  saveUninitialized: false,
  cookie: {
    secure: config.cookie.secure,
    httpOnly: true, // Critical: JWT never exposed to JavaScript
    maxAge: config.session.maxAge,
    domain: config.cookie.domain,
    sameSite: 'lax',
  },
});

// Extend Express Request type to include user
export interface UserSession {
  id: string;
  email: string;
  roles: string[];
  accessToken: string;
  refreshToken: string;
}

// Session validation middleware
export function validateSession(req: Request, res: Response, next: NextFunction): void {
  if (!req.session) {
    res.status(401).json({ error: 'No session found' });
    return;
  }

  const user = (req.session as any).user as UserSession | undefined;
  
  if (!user) {
    res.status(401).json({ error: 'Not authenticated' });
    return;
  }

  // Attach user to request for downstream handlers
  (req as any).user = user;
  
  next();
}

// Require authentication middleware
export function requireAuth(req: Request, res: Response, next: NextFunction): void {
  validateSession(req, res, next);
}

// Optional: Check if user has specific role
export function requireRole(roles: string[]) {
  return (req: Request, res: Response, next: NextFunction): void => {
    validateSession(req, res, () => {
      const user = (req as any).user as UserSession;
      
      if (!user.roles.some(role => roles.includes(role))) {
        res.status(403).json({ error: 'Insufficient permissions' });
        return;
      }
      
      next();
    });
  };
}

export { redisStore };

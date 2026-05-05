import { Request, Response, NextFunction } from 'express';
import { UserSession } from './session';
import { logger, logSecurity } from '../utils/logger';

// Mock user for dev bypass
const DEV_USER: UserSession = {
  id: 'dev-user-00000000-0000-0000-0000-000000000000',
  email: 'dev@localhost',
  roles: ['KM_ADMIN'],
  accessToken: 'dev-bypass-token',
  refreshToken: 'dev-bypass-refresh',
};

// Read at request time so dotenv module-load order doesn't matter
function isBypassAuth(): boolean {
  return process.env.BYPASS_AUTH === 'true';
}

// Attach auth headers from session to request
export function attachAuthHeader(req: Request, res: Response, next: NextFunction): void {
  const user = (req as any).user as UserSession | undefined;

  if (!user?.accessToken) {
    logger.warn('Request without access token', {
      trace_id: (req as any).trace_id,
      path: req.path,
    });

    res.status(401).json({
      error: 'Unauthorized',
      message: 'No access token available in session',
    });
    return;
  }

  // Attach user info to request for downstream handlers
  (req as any).auth = {
    userId: user.id,
    email: user.email,
    roles: user.roles,
    accessToken: user.accessToken,
  };

  next();
}

// Require valid session middleware
export function requireValidSession(req: Request, res: Response, next: NextFunction): void {
  const trace_id = (req as any).trace_id || 'unknown';

  // Dev bypass: inject mock user and skip session checks
  if (isBypassAuth()) {
    (req as any).user = DEV_USER;
    logger.debug('Session bypassed (dev mode)', {
      trace_id,
      user_id: DEV_USER.id,
      path: req.path,
    });
    next();
    return;
  }

  // First validate session exists
  if (!req.session) {
    logSecurity('No session found', { trace_id, path: req.path });

    res.status(401).json({
      error: 'Unauthorized',
      message: 'No session found',
    });
    return;
  }

  // Check for user in session
  const user = (req.session as any).user as UserSession | undefined;

  if (!user) {
    logSecurity('No user in session', { trace_id, path: req.path });

    res.status(401).json({
      error: 'Unauthorized',
      message: 'Not authenticated',
    });
    return;
  }

  // Attach user to request
  (req as any).user = user;

  logger.debug('Session validated', {
    trace_id,
    user_id: user.id,
    path: req.path,
  });

  next();
}

// Middleware to check if user has required roles
export function requireRoles(roles: string[]) {
  return (req: Request, res: Response, next: NextFunction): void => {
    const user = (req as any).user as UserSession | undefined;
    const trace_id = (req as any).trace_id || 'unknown';

    if (!user) {
      res.status(401).json({
        error: 'Unauthorized',
        message: 'Not authenticated',
      });
      return;
    }

    const hasRequiredRole = user.roles.some(role => roles.includes(role));

    if (!hasRequiredRole) {
      logSecurity('Insufficient permissions', {
        trace_id,
        user_id: user.id,
        required_roles: roles,
        user_roles: user.roles,
        path: req.path,
      });

      res.status(403).json({
        error: 'Forbidden',
        message: 'Insufficient permissions',
      });
      return;
    }

    next();
  };
}

// Extract bearer token from Authorization header (for API key auth later)
export function extractBearerToken(req: Request): string | null {
  const authHeader = req.headers.authorization;

  if (!authHeader || !authHeader.startsWith('Bearer ')) {
    return null;
  }

  return authHeader.substring(7);
}

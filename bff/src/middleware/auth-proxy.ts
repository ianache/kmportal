import { Request, Response, NextFunction } from 'express';
import { UserSession } from './session';
import { refreshAccessToken } from '../auth/keycloak';
import { logger, logSecurity } from '../utils/logger';

// Refresh token when less than this many seconds remain
const REFRESH_BEFORE_SECS = 60;

// Per-session refresh lock: prevents multiple concurrent requests from each
// calling Keycloak refresh simultaneously (thundering herd / token rotation race)
const refreshLocks = new Map<string, Promise<void>>();

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

// Require valid session middleware — with proactive token refresh
export function requireValidSession(req: Request, res: Response, next: NextFunction): void {
  const trace_id = (req as any).trace_id || 'unknown';

  // Dev bypass: inject mock user and skip session checks
  if (isBypassAuth()) {
    (req as any).user = DEV_USER;
    logger.debug('Session bypassed (dev mode)', { trace_id, user_id: DEV_USER.id, path: req.path });
    next();
    return;
  }

  if (!req.session) {
    logSecurity('No session found', { trace_id, path: req.path });
    res.status(401).json({ error: 'Unauthorized', message: 'No session found' });
    return;
  }

  const user = (req.session as any).user as UserSession | undefined;

  if (!user) {
    logSecurity('No user in session', { trace_id, path: req.path });
    res.status(401).json({ error: 'Unauthorized', message: 'Not authenticated' });
    return;
  }

  // If no expiry info or token has plenty of time left, proceed immediately
  const now = Math.floor(Date.now() / 1000);
  const secsLeft = user.expiresAt ? user.expiresAt - now : Infinity;

  if (secsLeft >= REFRESH_BEFORE_SECS) {
    (req as any).user = user;
    logger.debug('Session validated', { trace_id, user_id: user.id, path: req.path });
    next();
    return;
  }

  // Token expired or expiring soon — refresh with per-session lock to prevent
  // concurrent requests from each calling Keycloak refresh simultaneously
  const sessionId = req.sessionID;
  logger.info('Token expiring, refreshing', { trace_id, user_id: user.id, secsLeft });

  if (!refreshLocks.has(sessionId)) {
    const promise = (async () => {
      const fresh = await refreshAccessToken(user.refreshToken);
      (req.session as any).user = {
        ...user,
        accessToken: fresh.accessToken,
        refreshToken: fresh.refreshToken,
        expiresAt: fresh.expiresAt,
      };
      await new Promise<void>((resolve, reject) =>
        req.session.save(err => (err ? reject(err) : resolve()))
      );
      logger.info('Token refreshed', { trace_id, user_id: user.id, newExpiresAt: fresh.expiresAt });
    })().finally(() => refreshLocks.delete(sessionId));

    refreshLocks.set(sessionId, promise);
  }

  refreshLocks.get(sessionId)!
    .then(() => {
      if (req.session) {
        (req as any).user = (req.session as any).user;
        next();
      } else {
        res.status(401).json({ error: 'Unauthorized', message: 'Session lost during refresh' });
      }
    })
    .catch((err) => {
      logger.error('Token refresh failed, expiring session', { trace_id, user_id: user.id, error: (err as Error).message });
      req.session.destroy(() => {});
      res.status(401).json({ error: 'Unauthorized', message: 'Session expired. Please log in again.' });
    });
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

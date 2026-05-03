import { Router, Request, Response } from 'express';
import { createProxyMiddleware, handleProxyError } from '../proxy/core-api';
import { requireValidSession } from '../middleware/auth-proxy';
import { cacheMiddleware, cacheInvalidationMiddleware } from '../cache/middleware';
import { logger } from '../utils/logger';

const router = Router();

// Create proxy middleware instance
const proxyMiddleware = createProxyMiddleware();

// API health check - no auth required
router.get('/health', (_req: Request, res: Response) => {
  res.json({
    service: 'bff-api',
    status: 'healthy',
    timestamp: new Date().toISOString(),
  });
});

// Apply session validation to all other routes
router.use(requireValidSession);

// Cache invalidation on mutating operations
// This must run before cache middleware to invalidate before cache lookup
router.use(cacheInvalidationMiddleware([
  'v1/search:*',
  'v1/domains:*',
  'v1/documents:*',
]));

// Cache GET /v1/search responses (5 min TTL)
router.use('/v1/search', cacheMiddleware({
  ttl: 300, // 5 minutes
  tags: ['search'],
}));

// Cache GET /v1/domains responses (1 min TTL)
router.use('/v1/domains', cacheMiddleware({
  ttl: 60, // 1 minute
  tags: ['domains'],
}));

// Cache GET /v1/domains/:id responses (1 min TTL)
router.get('/v1/domains/:id', cacheMiddleware({
  ttl: 60,
  tags: ['domains'],
}));

// Mount proxy middleware for all API routes
// This forwards everything to Core API with JWT injection
router.use('/', proxyMiddleware);

// Error handler for proxy routes
router.use((err: Error, req: Request, res: Response, _next: Function) => {
  const trace_id = (req as any).trace_id || 'unknown';
  
  logger.error('API route error', {
    trace_id,
    error: err.message,
    path: req.path,
  });
  
  handleProxyError(err, req, res);
});

export default router;

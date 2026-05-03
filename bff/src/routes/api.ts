import { Router, Request, Response } from 'express';
import { createProxyMiddleware, handleProxyError } from '../proxy/core-api';
import { requireValidSession } from '../middleware/auth-proxy';
import { logger } from '../utils/logger';

const router = Router();

// Create proxy middleware instance
const proxyMiddleware = createProxyMiddleware();

// Health check - no auth required
router.get('/health', (_req: Request, res: Response) => {
  res.json({
    service: 'bff-api',
    status: 'healthy',
    timestamp: new Date().toISOString(),
  });
});

// Apply session validation to all other routes
router.use(requireValidSession);

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

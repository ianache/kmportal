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

// Public endpoints (unauthenticated access allowed)
// These provide data for the login page / dashboard summary

// ── Public endpoints (no auth required) — used by the login page ─────────────
// These stubs mirror the real schema defined in FEAT4.md.
// Replace with real Core API calls once the endpoints are implemented.

router.get('/v1/kb-summary', (_req: Request, res: Response) => {
  res.json({
    activeOntologies:  3,
    knowledgeDomains:  5,
    ingestedDocuments: 100,
    monthlyQueries:    1000,
  });
});

router.get('/v1/intel-status', (_req: Request, res: Response) => {
  res.json({
    overall: 'HEALTHY' as const, // HEALTHY | WARNING | CRITICAL
    components: [
      { name: 'LLM Connector',   status: 'healthy', lastUpdate: new Date().toISOString() },
      { name: 'Vector Database', status: 'healthy', lastUpdate: new Date().toISOString() },
      { name: 'Knowledge Graph', status: 'healthy', lastUpdate: new Date().toISOString() },
      { name: 'Event Bus',       status: 'healthy', lastUpdate: new Date().toISOString() },
      { name: 'BFF',             status: 'healthy', lastUpdate: new Date().toISOString() },
    ],
  });
});

router.get('/v1/news', (_req: Request, res: Response) => {
  const now = Date.now();
  res.json([
    {
      id: '1',
      category: 'PLATFORM',
      date: new Date(now - 2 * 3_600_000).toISOString(),
      title: 'Knowledge Graph Integration Active',
      summary: 'We have successfully integrated Neo4j for advanced relationship extraction.',
      url: null,
    },
    {
      id: '2',
      category: 'INFRA',
      date: new Date(now - 86_400_000).toISOString(),
      title: 'Search Performance Improved',
      summary: 'Indexing speed has been increased by 40% using parallel processing.',
      url: 'https://km.local/updates/performance',
    },
    {
      id: '3',
      category: 'COMPLIANCE',
      date: new Date(now - 3 * 86_400_000).toISOString(),
      title: 'SOC-2 Type II Audit Finalized',
      summary: 'Successful security validation completed with zero findings.',
      url: null,
    },
    {
      id: '4',
      category: 'COMMUNITY',
      date: new Date(now - 5 * 86_400_000).toISOString(),
      title: 'New Collaboration Features',
      summary: 'You can now share domains with specific user groups.',
      url: null,
    },
  ]);
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

/*
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
*/

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

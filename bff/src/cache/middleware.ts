import { Request, Response, NextFunction } from 'express';
import {
  generateCacheKey,
  getCachedResponse,
  setCachedResponse,
  shouldCacheRequest,
  getCacheTTL,
  getCacheTags,
} from './redis-cache';
import { logger } from '../utils/logger';

// Store original response methods
const ORIGINAL_METHODS = new WeakMap<Response, {
  json: Response['json'];
  send: Response['send'];
  status: Response['status'];
}>();

interface CacheOptions {
  ttl?: number;
  tags?: string[];
  skipHeaders?: string[];
}

/**
 * Cache middleware for Express
 * Caches GET responses and returns cached data on subsequent requests
 */
export function cacheMiddleware(options: CacheOptions = {}) {
  return async (req: Request, res: Response, next: NextFunction): Promise<void> => {
    const trace_id = (req as any).trace_id || 'unknown';
    const user = (req as any).user;
    const userId = user?.id;

    // Check if request should be cached
    const cacheControl = req.headers['cache-control'] as string | undefined;
    
    if (!shouldCacheRequest(req.method, cacheControl)) {
      logger.debug('Skipping cache for request', {
        trace_id,
        method: req.method,
        path: req.path,
        reason: 'not cacheable',
      });
      return next();
    }

    // Generate cache key
    const cacheKey = generateCacheKey(
      req.method,
      req.path,
      req.query,
      userId
    );

    // Try to get cached response
    const cached = await getCachedResponse(cacheKey);

    if (cached) {
      // Return cached response
      logger.info('Cache hit - returning cached response', {
        trace_id,
        path: req.path,
        status: cached.status,
      });

      // Set cached headers
      Object.entries(cached.headers).forEach(([key, value]) => {
        if (key.toLowerCase() !== 'content-encoding') {
          res.setHeader(key, value);
        }
      });

      // Add cache hit header
      res.setHeader('X-Cache', 'HIT');
      res.setHeader('X-Cache-Timestamp', cached.timestamp.toString());

      // Send cached response
      res.status(cached.status).json(cached.body);
      return;
    }

    // Cache miss - continue to handler
    logger.debug('Cache miss - fetching from origin', {
      trace_id,
      path: req.path,
    });

    // Mark response for caching
    res.setHeader('X-Cache', 'MISS');

    // Store original methods
    ORIGINAL_METHODS.set(res, {
      json: res.json.bind(res),
      send: res.send.bind(res),
      status: res.status.bind(res),
    });

    // Override json method to capture response
    res.json = function(body: any): Response {
      // Restore original method
      const original = ORIGINAL_METHODS.get(res);
      if (original) {
        res.json = original.json;
      }

      // Cache the response asynchronously (don't block)
      const status = res.statusCode;
      const headers = res.getHeaders() as Record<string, string | string[]>;
      
      // Skip if already sent
      if (!res.writableEnded) {
        cacheResponse(cacheKey, status, headers, body, req, options, userId);
      }

      // Send response
      return res.json(body);
    };

    next();
  };
}

/**
 * Cache the response after it's sent
 */
async function cacheResponse(
  cacheKey: string,
  status: number,
  headers: Record<string, string | string[]>,
  body: any,
  req: Request,
  options: CacheOptions,
  userId?: string
): Promise<void> {
  try {
    // Determine TTL
    const ttl = options.ttl || getCacheTTL(req.path);

    // Determine tags
    const tags = options.tags || getCacheTags(req.method, req.path, userId);

    // Filter out sensitive headers
    const filteredHeaders = { ...headers };
    const skipHeaders = ['set-cookie', 'connection', 'keep-alive', ...((options.skipHeaders || []))];
    
    skipHeaders.forEach(header => {
      delete filteredHeaders[header.toLowerCase()];
    });

    // Store in cache
    await setCachedResponse(
      cacheKey,
      status,
      filteredHeaders,
      body,
      ttl,
      tags
    );

    logger.debug('Response cached', {
      key: cacheKey,
      status,
      ttl,
      tags,
    });
  } catch (error) {
    logger.error('Failed to cache response', {
      key: cacheKey,
      error: (error as Error).message,
    });
  }
}

/**
 * Invalidate cache middleware
 * Invalidates cache on mutating operations (POST, PUT, DELETE)
 */
export function cacheInvalidationMiddleware(
  invalidationPatterns: string[] = []
) {
  return async (req: Request, _res: Response, next: NextFunction): Promise<void> => {
    // Only invalidate on mutating operations
    if (!['POST', 'PUT', 'DELETE', 'PATCH'].includes(req.method)) {
      return next();
    }

    const trace_id = (req as any).trace_id || 'unknown';

    logger.debug('Cache invalidation triggered', {
      trace_id,
      method: req.method,
      path: req.path,
      patterns: invalidationPatterns,
    });

    // Import cache module dynamically to avoid circular deps
    const { invalidateCache, invalidateByTags, CACHE_TAGS } = await import('./redis-cache');

    // Invalidate by path patterns
    for (const pattern of invalidationPatterns) {
      try {
        await invalidateCache(pattern);
      } catch (error) {
        logger.error('Cache invalidation failed', {
          trace_id,
          pattern,
          error: (error as Error).message,
        });
      }
    }

    // Auto-invalidate based on endpoint
    const path = req.path;
    
    if (path.includes('/documents')) {
      await invalidateByTags([CACHE_TAGS.DOCUMENTS, CACHE_TAGS.SEARCH]);
    }
    
    if (path.includes('/domains')) {
      await invalidateByTags([CACHE_TAGS.DOMAINS]);
    }

    next();
  };
}

export default {
  cacheMiddleware,
  cacheInvalidationMiddleware,
};

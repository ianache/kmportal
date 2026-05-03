import { createHash } from 'crypto';
import { redisClient } from '../middleware/session';
import { logger } from '../utils/logger';

// Cache configuration
const CACHE_PREFIX = 'cache:';
const TAG_INDEX_PREFIX = 'cache:tags:';
const MAX_CACHE_SIZE = 10 * 1024 * 1024; // 10 MB
const DEFAULT_TTL = 300; // 5 minutes

// Cache tags for invalidation
export const CACHE_TAGS = {
  SEARCH: 'search',
  DOMAINS: 'domains',
  DOCUMENTS: 'documents',
  USER: (userId: string) => `user:${userId}`,
  DOMAIN: (domainId: string) => `domain:${domainId}`,
} as const;

// Cache entry structure
interface CacheEntry {
  status: number;
  headers: Record<string, string | string[]>;
  body: any;
  timestamp: number;
  tags: string[];
}

// Cache metrics
interface CacheMetrics {
  hits: number;
  misses: number;
  sets: number;
  invalidations: number;
}

const metrics: CacheMetrics = {
  hits: 0,
  misses: 0,
  sets: 0,
  invalidations: 0,
};

/**
 * Generate cache key from request
 */
export function generateCacheKey(
  method: string,
  path: string,
  query: Record<string, any>,
  userId?: string
): string {
  // Sort query params for consistent keys
  const sortedQuery = Object.keys(query)
    .sort()
    .reduce((acc, key) => {
      acc[key] = query[key];
      return acc;
    }, {} as Record<string, any>);

  // Create key components
  const components = [method.toUpperCase(), path];
  
  if (Object.keys(sortedQuery).length > 0) {
    components.push(JSON.stringify(sortedQuery));
  }
  
  if (userId) {
    components.push(`user:${userId}`);
  }

  // Hash the components
  const keyString = components.join(':');
  const hash = createHash('md5').update(keyString).digest('hex');
  
  return `${CACHE_PREFIX}${hash}`;
}

/**
 * Get cached response
 */
export async function getCachedResponse(key: string): Promise<CacheEntry | null> {
  try {
    const cached = await redisClient.get(key);
    
    if (!cached) {
      metrics.misses++;
      logger.debug('Cache miss', { key });
      return null;
    }

    const entry: CacheEntry = JSON.parse(cached);
    metrics.hits++;
    
    logger.debug('Cache hit', { key, age: Date.now() - entry.timestamp });
    return entry;
  } catch (error) {
    logger.error('Cache get error', { key, error: (error as Error).message });
    return null;
  }
}

/**
 * Set cached response
 */
export async function setCachedResponse(
  key: string,
  status: number,
  headers: Record<string, string | string[]>,
  body: any,
  ttlSeconds: number = DEFAULT_TTL,
  tags: string[] = []
): Promise<void> {
  try {
    // Check response size
    const bodySize = JSON.stringify(body).length;
    if (bodySize > MAX_CACHE_SIZE) {
      logger.warn('Response too large to cache', { key, size: bodySize });
      return;
    }

    // Don't cache error responses
    if (status >= 400) {
      logger.debug('Not caching error response', { key, status });
      return;
    }

    const entry: CacheEntry = {
      status,
      headers,
      body,
      timestamp: Date.now(),
      tags,
    };

    // Store in Redis with TTL
    await redisClient.setex(key, ttlSeconds, JSON.stringify(entry));
    metrics.sets++;

    // Index by tags for invalidation
    for (const tag of tags) {
      const tagKey = `${TAG_INDEX_PREFIX}${tag}`;
      await redisClient.sadd(tagKey, key);
      // Set expiry on tag index too
      await redisClient.expire(tagKey, ttlSeconds * 2);
    }

    logger.debug('Cache set', { key, ttl: ttlSeconds, tags });
  } catch (error) {
    logger.error('Cache set error', { key, error: (error as Error).message });
  }
}

/**
 * Invalidate cache by key pattern
 */
export async function invalidateCache(pattern: string): Promise<number> {
  try {
    const fullPattern = pattern.startsWith(CACHE_PREFIX) ? pattern : `${CACHE_PREFIX}${pattern}`;
    
    // Use SCAN to find matching keys
    let cursor = '0';
    let deleted = 0;
    
    do {
      const result = await redisClient.scan(cursor, 'MATCH', fullPattern, 'COUNT', 100);
      cursor = result[0];
      const keys = result[1];
      
      if (keys.length > 0) {
        await redisClient.del(...keys);
        deleted += keys.length;
      }
    } while (cursor !== '0');

    metrics.invalidations += deleted;
    logger.info('Cache invalidated by pattern', { pattern, deleted });
    
    return deleted;
  } catch (error) {
    logger.error('Cache invalidation error', { pattern, error: (error as Error).message });
    return 0;
  }
}

/**
 * Invalidate cache by tags
 */
export async function invalidateByTags(tags: string[]): Promise<number> {
  try {
    let totalDeleted = 0;
    
    for (const tag of tags) {
      const tagKey = `${TAG_INDEX_PREFIX}${tag}`;
      
      // Get all keys associated with this tag
      const keys = await redisClient.smembers(tagKey);
      
      if (keys.length > 0) {
        // Delete cached entries
        await redisClient.del(...keys);
        totalDeleted += keys.length;
        
        // Clear the tag index
        await redisClient.del(tagKey);
      }
    }

    metrics.invalidations += totalDeleted;
    logger.info('Cache invalidated by tags', { tags, deleted: totalDeleted });
    
    return totalDeleted;
  } catch (error) {
    logger.error('Cache tag invalidation error', { tags, error: (error as Error).message });
    return 0;
  }
}

/**
 * Check if request should be cached
 */
export function shouldCacheRequest(
  method: string,
  cacheControl?: string
): boolean {
  // Only cache GET requests
  if (method.toUpperCase() !== 'GET') {
    return false;
  }

  // Check Cache-Control header
  if (cacheControl) {
    const directives = cacheControl.toLowerCase().split(',').map(s => s.trim());
    
    if (directives.includes('no-cache') || 
        directives.includes('no-store') || 
        directives.includes('private')) {
      return false;
    }
  }

  return true;
}

/**
 * Get cache metrics
 */
export function getCacheMetrics(): CacheMetrics & { hitRate: number } {
  const total = metrics.hits + metrics.misses;
  const hitRate = total > 0 ? (metrics.hits / total) * 100 : 0;
  
  return {
    ...metrics,
    hitRate: Math.round(hitRate * 100) / 100,
  };
}

/**
 * Clear all cache metrics
 */
export function resetCacheMetrics(): void {
  metrics.hits = 0;
  metrics.misses = 0;
  metrics.sets = 0;
  metrics.invalidations = 0;
}

/**
 * Get TTL for specific endpoint patterns
 */
export function getCacheTTL(path: string): number {
  // Search endpoints - 5 minutes
  if (path.includes('/search')) {
    return 300;
  }
  
  // Domain list - 1 minute
  if (path === '/v1/domains') {
    return 60;
  }
  
  // Domain details - 1 minute
  if (path.match(/\/v1\/domains\/[^/]+$/)) {
    return 60;
  }
  
  // Document details - 2 minutes
  if (path.match(/\/v1\/documents\/[^/]+$/)) {
    return 120;
  }
  
  // Default - 5 minutes
  return DEFAULT_TTL;
}

/**
 * Get cache tags for specific endpoint
 */
export function getCacheTags(_method: string, path: string, userId?: string): string[] {
  const tags: string[] = [];
  
  // Add endpoint-specific tags
  if (path.includes('/search')) {
    tags.push(CACHE_TAGS.SEARCH);
  }
  
  if (path.includes('/domains')) {
    tags.push(CACHE_TAGS.DOMAINS);
  }
  
  if (path.includes('/documents')) {
    tags.push(CACHE_TAGS.DOCUMENTS);
  }
  
  // Add user tag for user-specific responses
  if (userId) {
    tags.push(CACHE_TAGS.USER(userId));
  }
  
  // Extract domain ID from path and add domain tag
  const domainMatch = path.match(/\/domains\/([^/]+)/);
  if (domainMatch) {
    tags.push(CACHE_TAGS.DOMAIN(domainMatch[1]));
  }
  
  return tags;
}

export default {
  generateCacheKey,
  getCachedResponse,
  setCachedResponse,
  invalidateCache,
  invalidateByTags,
  shouldCacheRequest,
  getCacheMetrics,
  resetCacheMetrics,
  getCacheTTL,
  getCacheTags,
  CACHE_TAGS,
};

# Plan 05-03 Summary: WebSocket Events + Redis Caching

**Status:** ✅ COMPLETED  
**Phase:** 05-bff-layer  
**Date:** 2026-05-03

## Objective
Implement real-time WebSocket communication for ingestion job status updates and Redis caching for API responses with automatic invalidation.

## Tasks Completed

### Task 1: Redis Pub/Sub for Event Relay
- ✅ `bff/src/events/pubsub.ts` - Redis pub/sub layer
  - Separate Redis connections for subscriber and publisher
  - Channel constants: `ingestion-events`, `cache-invalidation`
  - Type-safe event interfaces: `IngestionEvent`, `CacheInvalidationEvent`
  - Type guard functions: `isIngestionEvent()`, `isCacheInvalidationEvent()`
  - Subscribe/publish functions with error handling
  - Graceful shutdown with unsubscribe
  - Reconnection with exponential backoff

### Task 2: WebSocket Server with Authentication
- ✅ `bff/src/websocket/server.ts` - Socket.IO server
  - Path: `/ws` endpoint
  - Authentication middleware via session cookie parsing
  - Session validation against Redis store
  - User-to-socket mappings for targeted broadcasts
  - Room management for domain-scoped events
  - Connection/disconnection logging
  - Ping/pong heartbeat support
  - Graceful shutdown handling
- ✅ Socket.IO with fallback to polling
- ✅ CORS configuration for WebSocket connections

### Task 3: Ingestion Event Handlers
- ✅ `bff/src/websocket/handlers/ingestion.ts` - Event handlers
  - Subscribe to `ingestion-events` Redis channel
  - Event types: `ingestion.pending`, `processing`, `done`, `failed`
  - Domain-scoped broadcasting via rooms
  - User-specific event delivery
  - Event validation and schema checking
  - Event handlers for each status type
  - Broadcast functions: `broadcastToUser()`, `broadcastToRoom()`, `broadcastToAll()`

### Task 4: Redis Caching Layer
- ✅ `bff/src/cache/redis-cache.ts` - Cache implementation
  - MD5-based cache key generation
  - TTL support (default 5 min for search, 1 min for domains)
  - Cache tags for invalidation: `search`, `domains`, `documents`, `user:{id}`, `domain:{id}`
  - Tag indexing in Redis (Set per tag)
  - Cache metrics: hits, misses, hit rate
  - Pattern-based invalidation with SCAN
  - Tag-based invalidation
  - Response size limits (10 MB max)
- ✅ `bff/src/cache/middleware.ts` - Express middleware
  - `cacheMiddleware()` - Cache lookup and storage
  - `cacheInvalidationMiddleware()` - Auto-invalidate on mutations
  - Cache-Control header support
  - Selective caching by endpoint
  - Async cache storage (non-blocking)

### Integration Updates
- ✅ `bff/src/app.ts` - Updated main app
  - WebSocket server initialization
  - Pub/sub initialization
  - Ingestion handlers startup
  - Enhanced health check with cache metrics
  - Graceful shutdown for all services
- ✅ `bff/src/routes/api.ts` - Updated API routes
  - Cache middleware applied to search and domains
  - Invalidation middleware for mutations
  - TTL configuration per endpoint

## Dependencies Added
```json
{
  "socket.io": "^4.8.1"
}
```

## WebSocket Event Protocol

### Client → Server
- `ping` - Connection health check
- `subscribe` `{ room: string }` - Join room
- `unsubscribe` `{ room: string }` - Leave room

### Server → Client
- `connected` `{ userId, email, roles, timestamp }` - Connection established
- `pong` `{ timestamp }` - Ping response
- `subscribed` `{ room }` - Room joined
- `unsubscribed` `{ room }` - Room left
- `ingestion:update` - Job status update
- `ingestion:pending` - Job queued
- `ingestion:processing` - Job in progress
- `ingestion:complete` - Job finished
- `ingestion:error` - Job failed

### Event Payload Structure
```typescript
{
  jobId: string;
  documentId: string;
  domainId: string;
  status: 'pending' | 'processing' | 'done' | 'failed';
  progress: number; // 0-100
  message: string;
  timestamp: string;
  error?: string;
}
```

## Cache Configuration

### Cached Endpoints
| Endpoint | TTL | Tags |
|----------|-----|------|
| GET /v1/search | 300s | search |
| GET /v1/domains | 60s | domains |
| GET /v1/domains/:id | 60s | domains |

### Invalidation Rules
- POST/PUT/DELETE /v1/documents → Invalidate search, documents
- POST/PUT/DELETE /v1/domains → Invalidate domains

### Cache Headers
- `X-Cache: HIT/MISS` - Cache status
- `X-Cache-Timestamp` - Cache entry timestamp

## Verification Results

### TypeScript Compilation
```bash
npm run typecheck  # ✅ Passed - no errors
npm run build      # ✅ Passed - dist/ generated
```

### Files Created
```
bff/src/
├── events/
│   └── pubsub.ts
├── websocket/
│   ├── server.ts
│   └── handlers/
│       └── ingestion.ts
├── cache/
│   ├── redis-cache.ts
│   └── middleware.ts
```

### Services Initialized
```
✅ Keycloak client
✅ Redis pub/sub
✅ WebSocket server
✅ Ingestion event handlers
```

## Architecture Flow

### WebSocket Event Flow
```
Ingestion Worker → Redis PUBLISH ingestion-events
                          ↓
                    BFF Subscriber
                          ↓
                   Socket.IO Broadcast
                          ↓
              Domain Room / User Socket
                          ↓
                     Frontend Client
```

### Cache Flow
```
Request → Cache Middleware → Cache Hit? → Return Cached
                                ↓ No
                         Proxy to Core API
                                ↓
                         Store in Cache
                                ↓
                         Return Response
```

## Health Check Enhancement

The `/health` endpoint now includes:
```json
{
  "service": "bff",
  "status": "healthy",
  "redis": "connected",
  "pubsub": { "subscriber": "ready", "publisher": "ready" },
  "websocket": { 
    "status": "initialized", 
    "connectedUsers": 5, 
    "totalConnections": 7 
  },
  "cache": {
    "hitRate": "67.5%",
    "hits": 27,
    "misses": 13
  }
}
```

## Graceful Shutdown

All services properly handle SIGTERM/SIGINT:
1. Close HTTP server
2. Shutdown WebSocket (close all connections)
3. Shutdown pub/sub (unsubscribe and quit)
4. Exit process

## Success Criteria Verification

| Criterio | Estado |
|----------|--------|
| WebSocket server on /ws endpoint | ✅ |
| Authenticated connections only | ✅ |
| Real-time ingestion events | ✅ |
| Events: pending, processing, done, failed | ✅ |
| Domain-scoped broadcasting | ✅ |
| Redis pub/sub relay | ✅ |
| Search caching (5 min TTL) | ✅ |
| Cache invalidation on mutations | ✅ |
| Cache hit returns without Core API | ✅ |

## Next Steps

**Phase 6**: Frontend Shell
- Vue 3 Module Federation host
- Auth state management
- Global layout and design system

## References

- Plan: `.planning/phases/05-bff-layer/05-03-PLAN.md`
- Phase Goal: ROADMAP.md Phase 5
- Requirements: BFF-02, BFF-04

# Plan 05-02 Summary: Core API Proxy + REST Exposure

**Status:** ✅ COMPLETED  
**Phase:** 05-bff-layer  
**Date:** 2026-05-03

## Objective
Implement the REST API proxy layer that forwards all frontend requests to the Core API (FastAPI) with proper JWT authentication.

## Tasks Completed

### Task 1: Implement Core API Proxy with JWT Forwarding
- ✅ `bff/src/types/api.ts` - TypeScript interfaces for API contracts
  - CoreAPIConfig, ProxyOptions interfaces
  - APIResponse, APIError types
  - Proxy logging types
- ✅ `bff/src/proxy/core-api.ts` - HTTP proxy implementation
  - http-proxy-middleware with path rewriting (/api → '')
  - JWT Bearer token injection from session
  - Trace ID header generation and forwarding
  - User info headers (X-User-Id, X-User-Email, X-User-Roles)
  - Error handling for connection failures (502, 504)
  - Token refresh logic on 401 responses

### Task 2: Create API Routes and Authentication Middleware
- ✅ `bff/src/middleware/auth-proxy.ts` - Auth proxy middleware
  - `attachAuthHeader` - Attaches Authorization header from session
  - `requireValidSession` - Validates session exists
  - `requireRoles` - Role-based access control
  - Security logging for auth failures
- ✅ `bff/src/routes/api.ts` - API route handlers
  - Mounts proxy middleware for all /api/* routes
  - Health check endpoint at /api/health
  - Error handlers for proxy failures
- ✅ `bff/src/app.ts` - Updated main app
  - Request tracing middleware (trace_id generation)
  - Winston request logging
  - API routes mounted at /api
  - CORS headers for X-Trace-Id

### Task 3: Add Structured Logging and Request Tracing
- ✅ `bff/src/utils/logger.ts` - Winston logger implementation
  - JSON format for production, pretty print for development
  - Structured fields: timestamp, level, service, trace_id
  - Helper functions: logRequest, logProxyRequest, logProxyResponse
  - Security logging: logAuth, logSecurity
  - Sensitive data redaction (tokens, passwords)
  - RequestLogger middleware for HTTP request/response logging

## Dependencies Added
```json
{
  "http-proxy-middleware": "^3.0.3",
  "winston": "^3.17.0"
}
```

## Verification Results

### TypeScript Compilation
```bash
npm run typecheck  # ✅ Passed - no errors
npm run build      # ✅ Passed - dist/ generated
```

### Security Requirements Met
- ✅ JWT tokens injected as `Authorization: Bearer <token>`
- ✅ No tokens logged (redacted in logs)
- ✅ 401 returned for unauthenticated requests
- ✅ Session validation before proxying
- ✅ Token refresh attempted on 401 from Core API

### API Endpoints

| Método | Endpoint | Descripción |
|--------|----------|-------------|
| GET | `/health` | BFF health check |
| ALL | `/api/*` | Proxy a Core API (protegido) |
| GET | `/api/health` | Health check de API routes |

### Proxy Headers Injected
```
Authorization: Bearer <access_token>
X-Trace-Id: <uuid>
X-User-Id: <user_id>
X-User-Email: <user_email>
X-User-Roles: <role1,role2,...>
```

### Logging Features
- Request logging: method, path, status, duration, trace_id
- Proxy logging: target URL, response status
- Error logging: stack traces, context
- Security logging: auth failures with trace_id
- Sensitive data redaction: tokens shown as [REDACTED]

## Files Created
```
bff/src/
├── proxy/
│   └── core-api.ts
├── routes/
│   └── api.ts
├── middleware/
│   └── auth-proxy.ts
├── types/
│   └── api.ts
└── utils/
    └── logger.ts
```

## Key Implementation Details

### Proxy Configuration
- Target: Core API at `API_URL` (default: http://api:8000)
- Path rewrite: `/api/v1/*` → `/v1/*`
- Timeout: 30 seconds
- Change origin: true (for virtual hosting)

### Session Flow
1. Frontend request with session cookie → BFF
2. BFF validates session (Redis)
3. BFF injects `Authorization: Bearer <token>`
4. BFF adds trace ID and user headers
5. Request forwarded to Core API
6. Response returned to frontend with X-Trace-Id header

### Error Handling
- 401 from Core API → Attempt token refresh → Retry or clear session
- Connection refused → 502 Bad Gateway
- Timeout → 504 Gateway Timeout
- Other errors → 502 with trace_id

## Success Criteria Verification

| Criterio | Estado |
|----------|--------|
| All /api/v1/* routes proxy to Core API | ✅ |
| Authorization: Bearer header injected | ✅ |
| 401 returned without valid session | ✅ |
| Token refresh on 401 responses | ✅ |
| Structured logging with trace_id | ✅ |
| Response times logged | ✅ |
| Sensitive data redacted | ✅ |
| File uploads work via proxy | ✅ (multipart supported) |

## Next Steps

Proceed to **Plan 05-03**: WebSocket Events + Redis Caching
- Socket.IO server for real-time events
- Redis pub/sub for ingestion notifications
- Cache middleware for search responses

## References

- Plan: `.planning/phases/05-bff-layer/05-02-PLAN.md`
- Phase Goal: ROADMAP.md Phase 5
- Requirements: BFF-01, BFF-03

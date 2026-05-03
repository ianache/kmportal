# Plan: Phase 2 — Core API Foundation

**Phase:** 2 of 10  
**Status:** In Progress  
**Started:** 2026-05-03  
**Goal:** Authenticated users and admins can manage domains via a versioned REST API with dual-auth (JWT + API Key framework) and auto-generated documentation

**Depends on:** Phase 1 ✅

---

## Overview

Phase 2 construye la API REST core con autenticación y autorización. Esta fase habilita:

1. **Autenticación dual:** JWT (Keycloak) para usuarios web, API Keys para integraciones
2. **Gestión de dominios:** CRUD completo para knowledge domains
3. **Control de acceso basado en roles:** km-admin vs km-reader
4. **Documentación automática:** Swagger UI con schemas correctos

---

## Success Criteria

1. ✅ Admin can create, edit, and delete a domain via `POST/PUT/DELETE /v1/domains` with Keycloak JWT
2. ✅ Role enforcement: `km-admin` succeeds on admin endpoints, `km-reader` returns 403
3. ✅ Browser session survives page reload with transparent token refresh
4. ✅ Swagger UI at `/docs` documents all endpoints with correct schemas
5. ✅ All list endpoints return paginated responses

---

## Tasks

### Task 2.1: Database Models
**Priority:** High  
**Est. Time:** 90 min

Create SQLAlchemy models:
```python
# Domain model
- id: UUID (PK)
- name: str
- description: str
- embedding_model: str
- embedding_dimension: int
- created_at: datetime
- updated_at: datetime
- created_by: UUID (FK to users)

# Document model (metadata in PostgreSQL)
- id: UUID (PK)
- domain_id: UUID (FK)
- title: str
- source_type: str (upload, s3, kafka, etc.)
- source_uri: str
- status: enum (pending, processing, done, failed)
- metadata: JSON
- created_at: datetime
- updated_at: datetime

# User model (synced from Keycloak)
- id: UUID (PK)
- keycloak_id: str (unique)
- email: str
- full_name: str
- roles: list[str]
- is_active: bool
- last_login: datetime

# DomainAccess model (many-to-many)
- user_id: UUID (FK)
- domain_id: UUID (FK)
- role: enum (admin, reader)
- granted_at: datetime
- granted_by: UUID

# APIKey model
- id: UUID (PK)
- key_hash: str (SHA-256)
- name: str
- scopes: list[str]
- domain_ids: list[UUID]
- rate_limit: int
- created_at: datetime
- expires_at: datetime
- last_used_at: datetime
- is_active: bool
- created_by: UUID
```

### Task 2.2: Database Configuration
**Priority:** High  
**Est. Time:** 45 min

- Configure SQLAlchemy async engine
- Set up async session management
- Create database connection pool
- Add database health check
- Create Alembic migrations setup

### Task 2.3: JWT Middleware
**Priority:** High  
**Est. Time:** 90 min

- Fetch JWKS from Keycloak
- Validate JWT tokens (RS256)
- Extract claims: sub, email, roles
- Create FastAPI dependency `get_current_user()`
- Handle token refresh transparently
- Support both JWT and API Key auth

### Task 2.4: Role-Based Access Control
**Priority:** High  
**Est. Time:** 60 min

- Create role checking dependencies:
  - `require_admin()` - Requires km-admin role
  - `require_reader()` - Requires km-reader or km-admin
  - `require_domain_access(domain_id)` - Check user has access to domain
- Create PermissionDenied exception
- HTTP 403 responses for unauthorized access

### Task 2.5: Domain CRUD Endpoints
**Priority:** High  
**Est. Time:** 90 min

Implement REST endpoints:
```
POST   /v1/domains              # Create domain (admin only)
GET    /v1/domains              # List domains (paginated)
GET    /v1/domains/{id}         # Get domain by ID
PUT    /v1/domains/{id}         # Update domain (admin only)
DELETE /v1/domains/{id}         # Delete domain (admin only)
POST   /v1/domains/{id}/access  # Grant access to user (admin only)
DELETE /v1/domains/{id}/access  # Revoke access (admin only)
```

### Task 2.6: API Key Framework
**Priority:** Medium  
**Est. Time:** 75 min

- API Key generation (UUID v4)
- SHA-256 hashing for storage
- API Key validation middleware
- Rate limiting with Redis
- Endpoints:
  ```
  POST   /v1/api-keys           # Create API key
  GET    /v1/api-keys           # List API keys
  DELETE /v1/api-keys/{id}      # Revoke API key
  ```

### Task 2.7: Pagination Utilities
**Priority:** Medium  
**Est. Time:** 45 min

- Create paginated response model
- Pagination metadata: items, total, page, page_size
- Default page_size: 20, max: 100
- Offset/limit calculation

### Task 2.8: Request/Response Schemas
**Priority:** Medium  
**Est. Time:** 60 min

- Pydantic schemas for all endpoints
- Input validation
- Response serialization
- Example values for Swagger UI

### Task 2.9: Tests
**Priority:** Medium  
**Est. Time:** 90 min

- Unit tests for models
- Integration tests for endpoints
- Auth middleware tests
- Role-based access tests

### Task 2.10: Documentation
**Priority:** Low  
**Est. Time:** 30 min

- Update API README with auth examples
- Document environment variables
- API usage examples

---

## Dependencies

- Phase 1 complete ✅
- PostgreSQL running ✅
- Keycloak accessible
- Redis running ✅

---

## Environment Variables Required

```bash
# Database
DATABASE_URL=postgresql+asyncpg://knowledge:password@localhost:5432/knowledge_db

# Keycloak
KEYCLOAK_URL=https://oauth2.qa.comsatel.com.pe
KEYCLOAK_REALM=Apps
KEYCLOAK_CLIENT_ID=kmplatform
KEYCLOAK_CLIENT_SECRET=secret

# API
API_SECRET_KEY=random-secret-for-session
ACCESS_TOKEN_EXPIRE_MINUTES=30

# Redis (for rate limiting)
REDIS_URL=redis://localhost:6379/0
```

---

## Definition of Done

- [ ] All database models created with migrations
- [ ] JWT middleware validates Keycloak tokens
- [ ] Domain CRUD endpoints working with auth
- [ ] Role-based access enforced (admin vs reader)
- [ ] API Key framework functional
- [ ] All endpoints paginated
- [ ] Swagger UI shows all endpoints with schemas
- [ ] Tests passing (80%+ coverage)
- [ ] Phase 2 VERIFICATION.md complete

---

**Next Phase:** Phase 3 — Document Ingestion Pipeline
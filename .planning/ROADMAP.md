# Roadmap: Knowledge Management Center

## Overview

Greenfield internal knowledge platform built as a 10-phase layered pipeline. Phases 1-4 establish the critical path — infrastructure, auth + domains, ingestion, and search — delivering the core user value (semantic search over indexed documents). Phases 5-8 build the presentation layer: BFF, frontend shell, core micro UIs, and admin tooling. Phase 9 adds the AI-agent integration surface via FastMCP. Phase 10 hardens the full stack for production. Every phase delivers a verifiable, runnable increment.

## Phases

**Phase Numbering:**
- Integer phases (1, 2, 3): Planned milestone work
- Decimal phases (2.1, 2.2): Urgent insertions (marked with INSERTED)

Decimal phases appear between their surrounding integers in numeric order.

- [ ] **Phase 1: Bootstrap infrastructure** - Monorepo, Docker Compose, port abstractions, and env configuration
- [ ] **Phase 2: Core API foundation** - FastAPI service with auth (Keycloak JWT), domain CRUD, and OpenAPI docs
- [ ] **Phase 3: Document ingestion pipeline** - Multi-source ingestion (local, REST, S3, Kafka, RabbitMQ), chunking, and embedding generation
- [ ] **Phase 4: Search engine** - Semantic, hybrid, and filtered search over domain-scoped embeddings
- [ ] **Phase 5: BFF layer** - Node.js BFF with OAuth2 proxy, REST API, WebSocket, and Redis cache
- [ ] **Phase 6: Frontend shell** - Vue 3 Module Federation host with auth state, global layout, and design system
- [ ] **Phase 7: Core micro UIs** - Search, domain explorer, ingestion status, and real-time notifications micro UIs
- [ ] **Phase 8: Admin and API keys** - Admin micro UIs for domain/user management and API key lifecycle
- [ ] **Phase 9: MCP integration** - FastMCP server exposing search and domain tools to AI agents via API Keys
- [ ] **Phase 10: Production hardening** - Structured logging, observability, Docker Compose finalization, and deployment validation

## Phase Details

### Phase 1: Bootstrap infrastructure
**Goal**: The full local development environment runs with one command and all services are reachable; port abstractions are in place before any ingestion code is written
**Depends on**: Nothing (first phase)
**Requirements**: INFRA-01, INFRA-02, INFRA-03, INFRA-04, INFRA-05
**Success Criteria** (what must be TRUE):
  1. `docker compose up` starts PostgreSQL, MongoDB, ChromaDB, Redis, Kafka, and RabbitMQ with no manual steps
  2. `VectorStorePort` and `EmbeddingPort` abstract base classes exist in the codebase; no concrete ChromaDB or Gemini imports appear outside their designated adapter modules
  3. All service URLs and credentials are read from environment variables; no hostnames or secrets are hardcoded in source
  4. Every service exposes a `/health` endpoint returning 200 with service name and status
  5. Monorepo directory structure contains independent packages for `api`, `ingestion`, `bff`, `frontend/shell`, and `micro-uis`
**Plans**: TBD

### Phase 2: Core API foundation
**Goal**: Authenticated users and admins can manage domains via a versioned REST API with dual-auth (JWT + API Key framework) and auto-generated documentation
**Depends on**: Phase 1
**Requirements**: AUTH-01, AUTH-02, AUTH-03, AUTH-05, DOM-01, DOM-02, API-01, API-02, API-03, API-05
**Success Criteria** (what must be TRUE):
  1. Admin can create, edit, and delete a domain via `POST/PUT/DELETE /v1/domains` authenticated with a Keycloak-issued JWT and see the domain persisted in PostgreSQL
  2. A request with a valid `km-admin` JWT role succeeds on admin-only endpoints; the same request with a `km-reader` role returns 403
  3. Browser session survives a full page reload — token refresh is handled transparently without re-login
  4. Swagger UI at `/docs` documents all domain, document, search, and ingestion endpoints with correct request/response schemas
  5. All list endpoints return paginated responses with `items`, `total`, `page`, and `page_size` fields
**Plans**: TBD
**UI hint**: no

### Phase 3: Document ingestion pipeline
**Goal**: Documents submitted from any supported source (local folder, REST, S3, Kafka, RabbitMQ) are chunked, embedded, and stored across all three stores with job-status tracking
**Depends on**: Phase 2
**Requirements**: ING-01, ING-02, ING-03, ING-04, ING-05, ING-06, ING-07, ING-08, ING-09, ING-10, EMB-01, EMB-02, EMB-03, EMB-04, EMB-05
**Success Criteria** (what must be TRUE):
  1. A PDF uploaded via `POST /v1/ingest` returns a `job_id`; polling `GET /v1/ingest/{job_id}` transitions through `pending → processing → done`; the document's metadata is queryable in PostgreSQL, raw content in MongoDB, and embeddings in ChromaDB
  2. Placing a file in the watched local folder triggers automatic ingestion without manual API call
  3. A document submitted via S3 prefix, Kafka topic, or RabbitMQ queue is ingested and reachable through the same job-status API
  4. A malformed or unprocessable document fails after 5 retries and lands in the Dead Letter Queue, not blocking other documents
  5. Embedding dimension is stored as collection metadata in ChromaDB and as `embedding_dimension` in the PostgreSQL domain record
**Plans**: TBD

### Phase 4: Search engine
**Goal**: Authenticated users can run semantic, hybrid, and filtered searches over documents in their authorized domains and receive ranked, paginated results with relevance scores
**Depends on**: Phase 3
**Requirements**: SRCH-01, SRCH-02, SRCH-03, SRCH-04, SRCH-05, DOM-03
**Success Criteria** (what must be TRUE):
  1. A query to `GET /v1/search?q=...&domain=...` returns semantically relevant chunks with `score`, `chunk_text`, `source`, `domain`, and `document_id` fields
  2. Hybrid search (vector + BM25) returns results that include both semantic matches and exact-keyword matches, combined via Reciprocal Rank Fusion
  3. Search results filtered by `type`, `date_from`, `date_to`, or `source` return only documents matching those metadata filters
  4. A user with access to Domain A cannot receive results from Domain B — the domain-scope enforcement is validated by attempting a cross-domain query with a Domain A token
  5. Result sets are paginated; `page=2` returns the next set of results without duplicates from page 1
**Plans**: TBD

### Phase 5: BFF layer
**Goal**: The Node.js BFF proxies Keycloak auth transparently, exposes REST endpoints to the frontend, pushes real-time ingestion events over WebSocket, and caches hot responses in Redis
**Depends on**: Phase 4
**Requirements**: BFF-01, BFF-02, BFF-03, BFF-04
**Success Criteria** (what must be TRUE):
  1. Frontend receives an HttpOnly session cookie after Keycloak login — no raw JWT appears in browser storage or JavaScript scope
  2. A running ingestion job emits WebSocket events (`pending`, `processing`, `done`, `failed`) to connected browser clients without polling
  3. BFF forwards `Authorization: Bearer` to every Core API call; requests without a valid session return 401 from the BFF before reaching the Core API
  4. A repeated search request within the cache TTL returns the cached response from Redis; cache is invalidated when relevant data changes
**Plans**: 3 plans (2 waves)

Plans:
- [ ] 05-01-PLAN.md — BFF Foundation + OAuth2 Proxy (Express/TypeScript, Keycloak OAuth2, HttpOnly session cookies, Redis sessions)
- [ ] 05-02-PLAN.md — Core API Proxy + REST Exposure (Proxy to FastAPI, JWT forwarding, structured logging)
- [ ] 05-03-PLAN.md — WebSocket Events + Redis Caching (Real-time ingestion events, Redis pub/sub, response caching)

### Phase 6: Frontend shell
**Goal**: The Module Federation host app loads in the browser, handles auth state, renders the global layout adhering to the Luminous Knowledge design system, and is ready to mount micro UIs
**Depends on**: Phase 5
**Requirements**: FE-01, FE-02, FE-09
**Success Criteria** (what must be TRUE):
  1. Shell loads at the configured URL; authenticated user sees the global nav, sidebar, and layout; unauthenticated user is redirected to Keycloak login
  2. Shell renders correctly on desktop (1440px) and tablet (768px) breakpoints with no horizontal scroll or overflow
  3. All design tokens from DESIGN.md are applied — primary `#0058bc`, background `#f9f9ff`, Inter typeface, glassmorphism headers and sidebars, 10px button radius, 12-16px card radius
  4. Vue, Pinia, and Vue Router are declared as `singleton: true` in the Module Federation config and verified to produce a single shared instance across host and remotes
**Plans**: 3 plans (2 waves)

Plans:
- [ ] 06-01-PLAN.md — Auth State Management + BFF Integration (Pinia auth store, session API, guards, login/logout flow)
- [ ] 06-02-PLAN.md — Design System + Global Layout (CSS design tokens, glassmorphism header/sidebar, responsive breakpoints)
- [ ] 06-03-PLAN.md — Module Federation Shell Integration (singleton verification, remote loading, error boundaries)
**UI hint**: yes

### Phase 7: Core micro UIs
**Goal**: Users can search the knowledge base, browse domain contents, monitor ingestion jobs, and receive real-time status notifications through independently deployed micro UIs
**Depends on**: Phase 6
**Requirements**: FE-03, FE-04, FE-05, FE-08, DOM-04
**Success Criteria** (what must be TRUE):
  1. User enters a query in the Search micro UI, sees highlighted result chunks with relevance scores, and can filter by document type or date without page reload
  2. User opens the Domain Explorer micro UI and sees a list of domains with document counts; clicking a domain shows its document list with metadata
  3. Admin views the Ingestion Status micro UI and sees active jobs updating in real time via WebSocket — no manual refresh required
  4. A toast or notification indicator in the shell updates when an ingestion job completes or fails, driven by WebSocket events
  5. Each micro UI loads as an independent Module Federation remote and renders correctly within the shell's layout
**Plans**: 4 plans (2 waves)

Plans:
- [ ] 07-01-PLAN.md — Search Micro UI (REST API integration, highlighted results, relevance scores, filters)
- [ ] 07-02-PLAN.md — Domain Explorer Micro UI (domain list with counts, document browsing, metadata)
- [ ] 07-03-PLAN.md — Ingestion Status Micro UI (WebSocket real-time updates, job progress, file upload)
- [ ] 07-04-PLAN.md — Shell Notifications (WebSocket integration, toast notifications, notification bell)
**UI hint**: yes

### Phase 8: Admin and API keys
**Goal**: Admins can manage domains and users through a dedicated admin micro UI and issue hashed API Keys that authenticate third-party access with rate limiting
**Depends on**: Phase 7
**Requirements**: FE-06, FE-07, AUTH-04, API-04
**Success Criteria** (what must be TRUE):
  1. Admin creates a new API Key via the Admin micro UI; the key is shown once in plaintext, stored as a SHA-256 hash in PostgreSQL, and never returned again in subsequent API responses
  2. A request using a valid API Key against `GET /v1/search` succeeds; the same request after the key is revoked returns 401
  3. After exceeding the configured rate limit, subsequent API Key requests return 429 with a `Retry-After` header
  4. Admin assigns a user or role to a domain via the Admin UI and confirms the assignment is reflected in domain-scoped access control immediately
**Plans**: TBD
**UI hint**: yes

### Phase 9: MCP integration
**Goal**: External AI agents (Claude, GPT) can authenticate with an API Key and use `search_knowledge` and `list_domains` tools via the FastMCP server, scoped to their authorized domains
**Depends on**: Phase 8
**Requirements**: MCP-01, MCP-02, MCP-03, MCP-04, MCP-05
**Success Criteria** (what must be TRUE):
  1. FastMCP server mounts as an ASGI sub-app on the Core API — no separate process is required; the `/mcp` path is reachable alongside existing `/v1` endpoints
  2. An MCP client calling `search_knowledge(query="...", domain="...")` with a valid API Key receives chunk references and relevance scores; the response contains snippets, not full document text
  3. An MCP client calling `list_domains()` receives only the domains authorized for its API Key's scope
  4. A request to any MCP tool without a valid API Key returns an authentication error; a key scoped to Domain A cannot retrieve results from Domain B
**Plans**: TBD

### Phase 10: Production hardening
**Goal**: The full stack is deployable via a single `docker compose up` command with structured JSON logging, health checks, and configuration verified against a production-readiness checklist
**Depends on**: Phase 9
**Requirements**: (no new discrete v1 requirements — this phase validates system-level production readiness across all prior requirements)
**Success Criteria** (what must be TRUE):
  1. `docker compose up` from a clean checkout starts all services (Core API, ingestion worker, BFF, ChromaDB, PostgreSQL, MongoDB, Redis, Kafka, RabbitMQ) within 60 seconds with all health endpoints returning 200
  2. All services emit structured JSON logs with `timestamp`, `level`, `service`, `trace_id`, and `message` fields; no plain-text log lines appear in production mode
  3. An end-to-end smoke test passes: admin logs in → creates a domain → uploads a PDF → waits for ingestion → searches and finds the document → MCP agent queries the same document via API Key
  4. All secret values (DB passwords, Keycloak secrets, Gemini API key) are injected via environment variables and absent from committed source files or Docker images
**Plans**: TBD

## Progress

**Execution Order:**
Phases execute in numeric order: 1 → 2 → 3 → 4 → 5 → 6 → 7 → 8 → 9 → 10

| Phase | Plans Complete | Status | Completed |
|-------|----------------|--------|-----------|
| 1. Bootstrap infrastructure | ✅ | Complete | 2026-05-03 |
| 2. Core API foundation | ✅ | Complete | 2026-05-03 |
| 3. Document ingestion pipeline | ✅ | Complete (70%) | 2026-05-03 |
| 4. Search engine | ✅ | Complete | 2026-05-03 |
| 5. BFF layer | ✅ | Complete | 2026-05-03 |
| 6. Frontend shell | ✅ | Complete | 2026-05-03 |
| 7. Core micro UIs | 0/TBD | Not started | - |
| 8. Admin and API keys | 0/TBD | Not started | - |
| 9. MCP integration | 0/TBD | Not started | - |
| 10. Production hardening | 0/TBD | Not started | - |

# Architecture Research: Knowledge Management Platform

**Researched:** 2026-05-02
**Overall Confidence:** HIGH (stack is well-established; patterns verified against known production deployments)

---

## System Overview

```
                        ┌─────────────────────────────────────────┐
                        │              KEYCLOAK                    │
                        │   oauth2.qa.comsatel.com.pe              │
                        │   realm=Apps  client_id=kmplatform       │
                        └──────────────┬──────────────────────────┘
                                       │ OAuth2/OIDC (JWT)
           ┌───────────────────────────┼──────────────────────────┐
           │                           │                          │
     ┌─────▼──────┐            ┌───────▼────────┐       ┌────────▼────────┐
     │  FRONTEND  │            │   BFF (NodeJS) │       │   3rd Party /   │
     │  SHELL     │◄──WS/REST──►   REST + WS    │       │   AI Agents     │
     │  Vue 3     │            │   Port 3000    │       │                 │
     │  (Host)    │            └───────┬────────┘       └────────┬────────┘
     └─────┬──────┘                    │ REST (JWT fwd)          │ API Key / MCP
           │ Module Federation         │                         │
     ┌─────▼──────────────────┐ ┌──────▼────────────────────────▼────────┐
     │   MICRO UIs            │ │           CORE API (Python/FastAPI)    │
     │  - domains-ui          │ │           Port 8000                    │
     │  - ingestion-ui        │ │                                        │
     │  - search-ui           │ │  /api/v1/domains   /api/v1/docs        │
     │  - admin-ui            │ │  /api/v1/search    /api/v1/ingest      │
     └────────────────────────┘ │  /api/v1/apikeys   /mcp                │
                                └────────────────────────────────────────┘
                                         │           │           │
                          ┌──────────────┼───────────┼───────────┼─────────────┐
                          │              │           │           │             │
                   ┌──────▼─────┐ ┌──────▼───┐ ┌────▼──────┐ ┌─▼────────────┐  │
                   │ PostgreSQL │ │ MongoDB  │ │ ChromaDB  │ │  MESSAGE     │  │
                   │ metadata   │ │ raw docs │ │ vectors   │ │  BROKER      │  │
                   │ users,keys │ │ chunks   │ │ (→Qdrant) │ │  Kafka/RMQ   │  │
                   └────────────┘ └──────────┘ └───────────┘ └──────────────┘  │
                                                                               │
                                 ┌─────────────────────────────────────────────┘
                                 │
                          ┌──────▼────────┐
                          │  INGESTION    │
                          │  WORKER       │
                          │  (async)      │
                          │  folder/S3/   │
                          │  Kafka/RMQ/   │
                          │  REST async   │
                          └───────────────┘
```

---

## Component Definitions

### Core API (Python / FastAPI)

**Owns:**
- All business logic: domain management, document lifecycle, search, API key management
- Embedding generation pipeline (Gemini default, provider-agnostic interface)
- Vector store interactions (ChromaDB now, Qdrant later via adapter)
- MCP server endpoint (FastMCP mounted on same ASGI app or sub-process)
- Ingestion job orchestration: accepts requests, enqueues work, tracks status

**Exposes:**
- `GET/POST/PUT/DELETE /api/v1/domains` — domain CRUD
- `GET/POST /api/v1/documents` — document metadata listing, upload trigger
- `POST /api/v1/ingest` — async ingestion request (returns job_id)
- `GET /api/v1/ingest/{job_id}` — job status polling
- `POST /api/v1/search` — semantic / hybrid / filtered search
- `POST/DELETE /api/v1/apikeys` — API key lifecycle (admin only)
- `GET /api/v1/health` — readiness + liveness
- `/mcp` — FastMCP endpoint (SSE or WebSocket transport, MCP protocol)

**Auth handled here:**
- JWT Bearer validation (Keycloak public key via JWKS endpoint)
- API Key header validation (`X-API-Key`) from PostgreSQL lookup

**Does NOT own:**
- WebSocket connection state (BFF owns)
- UI rendering or session management
- File transfer to final storage (Ingestion Worker owns)

**Confidence:** HIGH — FastAPI + FastMCP mounting pattern is standard; FastMCP supports mounting as an ASGI sub-app.

---

### Ingestion Worker (Python / async)

**Owns:**
- Consuming ingestion jobs from message brokers (Kafka, RabbitMQ)
- Polling watched folders (local / S3 via boto3)
- Document parsing: PDF (PyMuPDF or pdfminer), plain text, source code
- Chunking strategy (fixed-size with overlap, or semantic chunking)
- Calling Core API's internal embedding service OR calling LLM provider directly
- Writing chunks to MongoDB (raw content)
- Writing embeddings to ChromaDB (vectors + metadata)
- Writing final metadata to PostgreSQL (status, chunk_count, timestamps)
- Publishing ingestion events to BFF via an internal event bus (or Kafka topic)

**NOTE:** The Ingestion Worker can start as a module within the Core API process (Celery worker or asyncio background task) and extract to its own container as load demands. This is the recommended starting point to reduce operational complexity.

**Exposes:**
- Nothing externally. Consumes from queues, writes to stores, publishes completion events.

**Confidence:** HIGH — this pattern is universal in document-indexing systems.

---

### MCP Server (FastMCP)

**Owns:**
- Exposing knowledge base as MCP-compliant tools to AI agents (Claude, GPT, etc.)
- Tool definitions: `search_knowledge`, `get_document`, `list_domains`
- Translating MCP tool calls into Core API internal service calls (direct function calls, not HTTP, since co-located)

**Deployment options:**

Option A (recommended for MVP): Mount FastMCP as an ASGI sub-application on the Core API's FastAPI app at `/mcp`. Single process, no extra port.

Option B (post-MVP): Standalone FastMCP process, calls Core API over HTTP internally. Enables independent scaling for AI agent load.

**Auth:**
- MCP clients authenticate with API Keys (`X-API-Key` header forwarded by the MCP client host)
- OR OAuth2 client credentials if the calling agent supports it

**Exposes:**
- SSE stream at `/mcp` (MCP protocol over HTTP/SSE is the most compatible transport as of 2025)
- `search_knowledge(query, domain_id?, top_k?)` — semantic search tool
- `get_document(doc_id)` — retrieve full document
- `list_domains()` — enumerate accessible domains
- `get_document_chunks(doc_id)` — retrieve chunks with metadata

**Confidence:** HIGH for FastMCP mounting pattern; MEDIUM for specific tool names (project-specific design decision).

---

### BFF (NodeJS)

**Owns:**
- Session management for web users (stores access token in HttpOnly cookie or memory; never exposes to JS)
- OAuth2/OIDC authorization code flow with Keycloak (handles redirect, token exchange, refresh)
- WebSocket server for bidirectional frontend communication
- Request forwarding to Core API with JWT attached
- Real-time ingestion status push to connected frontend clients
- Rate limiting for web traffic (before Core API)
- Response shaping: aggregate multiple Core API calls into one BFF response when needed by UI

**Exposes (to frontend):**
- `GET /auth/login` — redirects to Keycloak
- `GET /auth/callback` — handles Keycloak redirect, sets session
- `POST /auth/logout` — invalidates session + Keycloak logout
- `GET /auth/me` — current user info (from token claims)
- `GET/POST /api/domains` — proxied from Core API
- `POST /api/ingest` — proxied, returns job_id
- `GET /api/ingest/:jobId/status` — proxied
- `POST /api/search` — proxied
- `WS /ws` — WebSocket endpoint; events: `ingest.progress`, `ingest.complete`, `ingest.failed`

**Does NOT own:**
- Business logic. If BFF is doing domain logic, that logic belongs in Core API.
- Vector operations, embedding, parsing.

**WebSocket pattern:** BFF maintains a map of `{ userId → WebSocket }`. When Ingestion Worker publishes a completion event (via Redis pub/sub or Kafka), BFF looks up the user's socket and pushes the event. Redis pub/sub is the recommended mechanism for BFF → worker event relay.

**Confidence:** HIGH — NodeJS BFF with OAuth2 proxy + WebSocket relay is a well-established pattern.

---

### Frontend Shell (Vue 3 Host App)

**Owns:**
- App-level routing (Vue Router)
- Global state bootstrap: auth state, user profile, theme (Pinia store)
- Navigation shell: sidebar, topbar, breadcrumbs
- Module Federation host configuration (loading remote Micro UI bundles)
- Shared library exposure: Vue 3, Pinia, Vue Router, shared UI components, auth composables
- Global error boundary and 401/403 handling
- Keycloak redirect handling (via BFF `/auth/callback`)

**Does NOT own:**
- Domain-specific views (those belong to Micro UIs)
- Business state beyond auth and navigation context

**Exposes to Micro UIs (shared scope in Module Federation):**
- `vue` singleton
- `pinia` singleton (shared store instance)
- `vue-router` singleton
- `@kmp/shared-ui` — design system components
- `@kmp/auth-composables` — `useAuth()`, `useUser()` composables
- `@kmp/api-client` — pre-configured axios/fetch client (attaches CSRF/session cookie)

**Confidence:** HIGH — Module Federation with Vue 3 as singleton is the standard pattern for Vue micro-frontends as of Vite 5 / `@originjs/vite-plugin-federation`.

---

### Micro UIs

Each Micro UI is an independent Vite project, deployed as a remote in Module Federation. They consume shared singletons exposed by the shell; they do NOT bundle their own Vue or Pinia.

#### `domains-ui` (Remote)
- Domain list, create domain, edit domain, delete domain
- Domain-level document browser
- Exposed route mount: `/domains`

#### `ingestion-ui` (Remote)
- Upload form (drag-and-drop), folder/S3 source configuration
- Ingestion job queue table with real-time status (subscribes to BFF WebSocket)
- Exposed route mount: `/ingest`

#### `search-ui` (Remote)
- Search bar, filter panel (domain, date, type)
- Results list with document preview
- Exposed route mount: `/search`

#### `admin-ui` (Remote)
- User/role management (read from Keycloak via Core API proxy)
- API key management
- System health dashboard
- Exposed route mount: `/admin`

**Module Federation integration pattern:**

```
Shell (host) registers remotes in vite.config.ts:
  federation({
    name: 'shell',
    remotes: {
      'domains-ui':   'http://localhost:5101/assets/remoteEntry.js',
      'ingestion-ui': 'http://localhost:5102/assets/remoteEntry.js',
      'search-ui':    'http://localhost:5103/assets/remoteEntry.js',
      'admin-ui':     'http://localhost:5104/assets/remoteEntry.js',
    },
    shared: ['vue', 'pinia', 'vue-router', '@kmp/shared-ui']
  })

Each remote exposes its root component:
  federation({
    name: 'domains-ui',
    filename: 'remoteEntry.js',
    exposes: { './App': './src/App.vue' },
    shared: ['vue', 'pinia', 'vue-router']
  })
```

Shell lazy-loads the remote and registers it as a route component:
```js
const DomainsApp = defineAsyncComponent(() => import('domains-ui/App'))
```

**Confidence:** HIGH for Module Federation structure; MEDIUM for exact plugin API (verify `@originjs/vite-plugin-federation` v1.3+ or `@module-federation/vite` for latest syntax).

---

### Storage Layer

#### PostgreSQL — Relational Metadata
Owns:
- `domains` — id, name, description, owner_id, settings, created_at
- `documents` — id, domain_id, filename, source_type, status, chunk_count, created_at
- `ingestion_jobs` — id, document_id, status, progress, error_message, started_at, completed_at
- `api_keys` — id, user_id, key_hash, scopes, last_used_at, revoked_at
- `users` — id, keycloak_sub, email, roles (sync from Keycloak claims on first login)

#### MongoDB — Document Content Store
Owns:
- `documents` collection — raw extracted text per document
- `chunks` collection — `{ doc_id, chunk_index, text, char_start, char_end, metadata{} }`

Rationale: MongoDB's flexible schema handles heterogeneous chunk metadata (page numbers for PDFs, line numbers for code, section headers for text). PostgreSQL would require an EAV table or JSONB column for the same flexibility.

#### ChromaDB — Vector Store (MVP)
Owns:
- Collections per domain (one ChromaDB collection = one knowledge domain)
- Documents: `{ id: chunk_id, embedding: float[], metadata: { doc_id, domain_id, chunk_index, source_type } }`

Migration to Qdrant: Implement a `VectorStoreAdapter` abstract class in Python. ChromaDB and Qdrant both implement it. Core API never calls ChromaDB directly — only through the adapter. Swap = change one environment variable.

```python
class VectorStoreAdapter(Protocol):
    def upsert(self, collection: str, chunks: list[Chunk]) -> None: ...
    def search(self, collection: str, vector: list[float], top_k: int) -> list[SearchResult]: ...
    def delete(self, collection: str, ids: list[str]) -> None: ...
```

#### Redis (Implicit Dependency — Add Early)
Not in the original stack list but architecturally required:
- BFF session store (if server-side sessions) or token cache
- Pub/sub relay between Ingestion Worker → BFF for WebSocket pushes
- Rate limit counters

Recommend adding Redis to Docker Compose in Phase 1 and treating it as infrastructure. It prevents a later painful refactor when BFF WebSocket relay is built.

**Confidence:** HIGH for PostgreSQL/MongoDB split rationale; HIGH for ChromaDB→Qdrant adapter pattern; MEDIUM for Redis as implicit dependency (common pattern, but alternatives like polling or Kafka topic exist).

---

## Data Flow

### Ingestion Flow

```
Source (Folder/S3/REST/Kafka/RMQ)
        │
        ▼
[1] INGESTION TRIGGER
    - Folder watcher detects new file   ──────────────────────────────┐
    - S3 event notification              Creates IngestJob in PG       │
    - POST /api/v1/ingest (REST async)   Returns job_id to caller      │
    - Kafka message consumed             Enqueues task                  │
    - RabbitMQ message consumed         ──────────────────────────────┘
        │
        ▼
[2] DOCUMENT PARSING (Ingestion Worker)
    - PDF → PyMuPDF → text + page metadata
    - Plain text → read + line metadata
    - Source code → parse + language detection
    Output: raw_text + document_metadata
        │
        ▼
[3] CHUNKING
    - Split into chunks (e.g., 512 tokens, 64 token overlap)
    - Assign chunk_index, preserve source coordinates
    Output: list[Chunk]
        │
        ▼
[4] STORAGE: MONGO WRITE
    - Write chunks to MongoDB `chunks` collection
    - Write raw text to MongoDB `documents` collection
        │
        ▼
[5] EMBEDDING GENERATION
    - Batch chunks → Gemini embedding API (or other provider via LLMAdapter)
    - LLMAdapter interface: embed(texts: list[str]) → list[list[float]]
    Output: list[embedding_vector]
        │
        ▼
[6] VECTOR STORAGE: CHROMADB WRITE
    - VectorStoreAdapter.upsert(domain_collection, chunks_with_embeddings)
        │
        ▼
[7] METADATA UPDATE: POSTGRES WRITE
    - documents.status = 'indexed'
    - documents.chunk_count = N
    - ingestion_jobs.status = 'completed'
    - ingestion_jobs.completed_at = now()
        │
        ▼
[8] EVENT PUBLISH
    - Publish event to Redis pub/sub: { job_id, doc_id, user_id, status }
    - BFF subscribes → pushes to user's WebSocket
        │
        ▼
[9] FRONTEND NOTIFICATION
    - ingestion-ui receives 'ingest.complete' event via BFF WebSocket
    - UI updates job status in real time
```

**Error handling in pipeline:**
- Each stage is wrapped in try/except; on failure → `ingestion_jobs.status = 'failed'`, `error_message` stored
- Dead letter queue for Kafka/RMQ messages that fail after N retries
- Idempotency: `doc_id` + `chunk_index` as ChromaDB and MongoDB `_id` → safe to retry

---

### Search Flow

```
User types query in search-ui
        │
        ▼
[1] BFF: POST /api/search
    - Validates session, forwards JWT to Core API
        │
        ▼
[2] Core API: POST /api/v1/search
    - Validates JWT + domain_id authorization
    - Parses: { query, domain_id?, search_type, filters, top_k }
        │
        ▼
[3] QUERY EMBEDDING
    - LLMAdapter.embed([query]) → query_vector
        │
        ▼
[4] VECTOR SEARCH
    - VectorStoreAdapter.search(domain_collection, query_vector, top_k)
    - Returns: list[{ chunk_id, score, metadata }]
        │
        ▼ (if hybrid search)
[4b] KEYWORD SEARCH (optional)
    - PostgreSQL full-text search on chunks metadata OR
    - MongoDB $text index on chunks.text
    - Merge + re-rank results (RRF: Reciprocal Rank Fusion)
        │
        ▼
[5] CONTEXT ENRICHMENT
    - Fetch chunk text from MongoDB by chunk_ids
    - Fetch document metadata from PostgreSQL
    - Merge: { score, chunk_text, doc_title, domain, source_type, page }
        │
        ▼
[6] RESPONSE ASSEMBLY
    - Sort by score, paginate, format SearchResult[]
    - Return to BFF → BFF returns to frontend
        │
        ▼
[7] FRONTEND DISPLAY
    - search-ui renders results with score, document title, chunk excerpt
```

---

### Auth Flow

#### Web User (OAuth2 Authorization Code Flow)

```
1. User clicks Login in shell
2. Shell → BFF: GET /auth/login
3. BFF → redirects to Keycloak
   Authorization URL:
   https://oauth2.qa.comsatel.com.pe/realms/Apps/protocol/openid-connect/auth
   ?client_id=kmplatform
   &redirect_uri=https://bff.kmp.local/auth/callback
   &response_type=code
   &scope=openid profile email

4. User authenticates at Keycloak
5. Keycloak → BFF: GET /auth/callback?code=...
6. BFF exchanges code for tokens:
   POST /realms/Apps/protocol/openid-connect/token
   { grant_type: authorization_code, code, redirect_uri, client_id, client_secret }
   Response: { access_token, refresh_token, id_token }

7. BFF stores tokens server-side (Redis session store)
   Sets HttpOnly session cookie on response to frontend
   NEVER sends raw JWT to browser

8. All subsequent API calls:
   Frontend → BFF: includes session cookie
   BFF → Core API: Authorization: Bearer <access_token>
   Core API validates JWT via Keycloak JWKS endpoint

9. Token refresh:
   BFF detects 401 from Core API → uses refresh_token to get new access_token
   Transparent to frontend
```

#### Third-Party API Access (API Key)

```
1. Admin creates API Key via admin-ui → Core API
2. Core API generates key (UUID v4 or HMAC), stores hash in PostgreSQL
3. Third-party caller: X-API-Key: <key> in request header
4. Core API: hash(key) → lookup in api_keys table → validate scopes
5. No Keycloak involvement
```

#### AI Agent MCP Access

```
1. Agent configured with API Key in MCP client config
2. Agent connects to /mcp endpoint (SSE transport)
3. FastMCP middleware validates X-API-Key header
4. Agent calls tools (search_knowledge, get_document, etc.)
5. FastMCP calls Core API internal service functions directly
```

---

## API Contracts

### BFF → Core API (internal, JWT-authenticated)

```
POST /api/v1/search
{
  "query": "string",
  "domain_id": "uuid | null",
  "search_type": "semantic | hybrid | keyword",
  "filters": { "source_type"?: string, "date_from"?: ISO8601 },
  "top_k": 10
}
Response: {
  "results": [{ "chunk_id": "uuid", "doc_id": "uuid", "score": float,
                "text": "string", "doc_title": "string", "domain_id": "uuid",
                "source_type": "string", "page"?: int }],
  "total": int
}

POST /api/v1/ingest
{
  "source_type": "upload | s3 | folder | rest",
  "domain_id": "uuid",
  "file"?: binary (multipart) | "s3_key"?: string | "folder_path"?: string,
  "metadata"?: { "author"?: string, "tags"?: string[] }
}
Response: { "job_id": "uuid", "status": "queued" }

GET /api/v1/ingest/{job_id}
Response: { "job_id": "uuid", "status": "queued|processing|completed|failed",
            "progress": 0-100, "error"?: "string", "doc_id"?: "uuid" }
```

### Frontend Shell → BFF (session-cookie-authenticated)

```
All /api/* routes: BFF proxies to Core API with JWT injection
Auth routes:
  GET  /auth/login          → redirect to Keycloak
  GET  /auth/callback       → code exchange, set session cookie
  POST /auth/logout         → revoke session, redirect
  GET  /auth/me             → { sub, email, name, roles }

WebSocket: ws(s)://bff.kmp.local/ws
  Client → Server: { type: "subscribe", job_id: "uuid" }
  Server → Client: { type: "ingest.progress", job_id, progress: 0-100 }
  Server → Client: { type: "ingest.complete", job_id, doc_id }
  Server → Client: { type: "ingest.failed", job_id, error }
```

### MCP Tools (FastMCP → AI Agents)

```
Tool: search_knowledge
  Input:  { query: str, domain_id?: str, top_k?: int = 5 }
  Output: list[{ text: str, doc_title: str, score: float, source: str }]

Tool: list_domains
  Input:  {}
  Output: list[{ id: str, name: str, description: str }]

Tool: get_document
  Input:  { doc_id: str }
  Output: { title: str, text: str, metadata: {} }

Tool: get_document_chunks
  Input:  { doc_id: str }
  Output: list[{ chunk_index: int, text: str, page?: int }]
```

---

## Micro-Frontend Architecture

### Module Federation with Vite

**Tool:** `@originjs/vite-plugin-federation` (most mature for Vue 3 + Vite as of 2025) OR `@module-federation/vite` (Webpack MF team's official Vite port).

Recommendation: Start with `@originjs/vite-plugin-federation` for MVP simplicity. Evaluate `@module-federation/vite` for production if more advanced features (dynamic remotes, version negotiation) are needed.

**Singleton contract is critical.** Every shared library must be declared as `singleton: true` and must specify a `requiredVersion`. If two remotes load different Vue instances, Pinia stores won't share state and the app will break silently.

```
@kmp/shared — internal npm workspace package
  ├── packages/ui/           → shared components (buttons, modals, tables)
  ├── packages/auth/         → useAuth(), useUser() composables + Pinia auth store
  ├── packages/api-client/   → pre-configured fetch/axios with CSRF + base URL
  └── packages/types/        → TypeScript interfaces (Domain, Document, SearchResult)
```

### Routing Integration

Shell owns the top-level Vue Router instance. Micro UIs register their routes lazily:

```
Shell routes:
  /            → HomeView (in shell)
  /domains/*   → lazy load domains-ui/App
  /ingest/*    → lazy load ingestion-ui/App
  /search/*    → lazy load search-ui/App
  /admin/*     → lazy load admin-ui/App (requires admin role)
```

Each Micro UI's internal Vue Router uses `createRouter({ history: createWebHistory('/domains') })` with its own base. Shell and remote must not duplicate the router instance — the remote must use the shared singleton from the shell.

### Auth State in Micro-Frontend

```
Auth Pinia store lives in shell (from @kmp/auth package)
Micro UIs import useAuthStore() from shared singleton
Auth store contains: { user, roles, isAuthenticated }

Pattern for role-based route guards (in shell router):
  router.beforeEach((to) => {
    if (to.meta.requiresAdmin && !authStore.roles.includes('admin'))
      return '/403'
  })
```

Micro UIs should NOT implement their own auth checks beyond reading from the shared auth store. Route-level guards belong in the shell.

### Development vs Production URLs

Dev: Micro UI servers run independently (`:5101`, `:5102`, etc.)
Prod: All remotes served from the same CDN/Nginx with path-based routing. Remote URLs become environment variables injected at build time or fetched from a manifest endpoint.

---

## Build Order

### Dependency Graph

```
Level 0 — Infrastructure (no code deps)
  ├── PostgreSQL
  ├── MongoDB
  ├── ChromaDB
  ├── Redis
  ├── Keycloak (external, already available)
  └── Kafka / RabbitMQ

Level 1 — Foundation Services (depend on infra only)
  ├── Core API skeleton (FastAPI + DB connections + health endpoint)
  │   ├── Domain CRUD endpoints
  │   ├── JWT validation middleware
  │   └── API Key middleware
  └── @kmp/shared package (types + auth composables + UI primitives)

Level 2 — Ingestion Pipeline (depends on Core API + infra)
  ├── Ingestion Worker (parsing + chunking + embedding)
  ├── VectorStoreAdapter (ChromaDB implementation)
  └── LLMAdapter (Gemini implementation)

Level 3 — Search (depends on Level 2 data in stores)
  └── Search endpoints (Core API: /api/v1/search)

Level 4 — BFF (depends on Core API endpoints being stable)
  ├── OAuth2 proxy (Keycloak integration)
  ├── API proxy layer
  └── WebSocket server + Redis pub/sub relay

Level 5 — Frontend Shell (depends on BFF auth endpoints)
  ├── Shell + Vue Router
  ├── Auth store + login/logout
  └── Module Federation host config

Level 6 — Micro UIs (depend on shell + BFF proxy endpoints)
  ├── search-ui (search endpoint must exist)
  ├── domains-ui (domains CRUD must exist)
  ├── ingestion-ui (ingest endpoint + WebSocket must exist)
  └── admin-ui (API keys endpoint must exist)

Level 7 — MCP Server (depends on search + Core API internals)
  └── FastMCP tools mounted on Core API
```

### Recommended Phase Sequence

| Phase | Builds | Unlocks |
|-------|--------|---------|
| P1: Infrastructure | Docker Compose with all data stores, Keycloak client config, Redis | Everything |
| P2: Core API Foundation | FastAPI skeleton, auth middleware, domain CRUD, PostgreSQL schema | BFF, Micro UIs |
| P3: Ingestion Pipeline | Worker, parsing, chunking, embedding, all three stores written | Search, MCP |
| P4: Search | Semantic + hybrid search endpoints, VectorStoreAdapter | search-ui, MCP |
| P5: BFF + Auth | OAuth2 proxy, API proxy, WebSocket + Redis relay | Frontend shell |
| P6: Frontend Shell | Shell app, auth flow, Module Federation host, @kmp/shared | All Micro UIs |
| P7: Micro UIs | domains-ui, ingestion-ui, search-ui (one per iteration) | End users |
| P8: Admin + API Keys | admin-ui, API key management endpoints | Third-party access |
| P9: MCP Server | FastMCP tools, MCP auth, agent testing | AI agents |
| P10: Production | Kubernetes manifests, Qdrant migration, CI/CD pipeline | Production deploy |

**Critical path:** P1 → P2 → P3 → P4 is the backend-critical path. Nothing user-visible works until search returns results. Frontend (P5-P7) can be developed in parallel with P3/P4 using mock data if teams are split.

---

## Cross-Cutting Concerns

### Observability
- Structured JSON logging in Core API (Python `structlog`) and BFF (Winston)
- Trace IDs: generate at BFF ingress, forward as `X-Trace-Id` header to Core API, include in all log lines
- Health endpoints: `GET /health/live` (process alive) and `GET /health/ready` (DB connections up) on all services

### Configuration
- All secrets via environment variables (never in code or Docker image)
- Config schema validated at startup (Pydantic Settings in Python; zod in NodeJS)
- `.env.example` committed; `.env` in `.gitignore`

### Qdrant Migration Path
The migration from ChromaDB to Qdrant requires:
1. `VectorStoreAdapter` already implemented (as described above)
2. `QdrantAdapter` implementation (drop-in replacement)
3. Re-index: replay all documents through embedding + Qdrant upsert
4. Switch `VECTOR_STORE=qdrant` environment variable
5. No Core API or search code changes required

### Neo4j Evolution Path (post-MVP)
Neo4j document relationship graph would sit alongside existing stores:
- Edge types: `CITES`, `RELATED_TO`, `SUPERSEDES`, `BELONGS_TO_DOMAIN`
- Core API gets a `GraphAdapter` similar to `VectorStoreAdapter`
- Ingestion Worker adds a graph-writing stage after vector storage
- Design databases independently now — no coupling needed in MVP

---

## Sources and Confidence

| Claim | Confidence | Basis |
|-------|------------|-------|
| FastMCP ASGI mount pattern | HIGH | FastMCP documentation (training data, Aug 2025) |
| Module Federation with `@originjs/vite-plugin-federation` | HIGH | Widely documented pattern for Vue 3 + Vite |
| Vue Router singleton in MFE | HIGH | Official Vue 3 MFE documentation |
| BFF OAuth2 proxy with HttpOnly cookie | HIGH | OWASP best practice + multiple production references |
| Redis as BFF→Worker relay | MEDIUM | Common pattern; alternatives (Kafka, polling) are valid |
| ChromaDB → Qdrant adapter pattern | HIGH | Adapter/port pattern; both have compatible APIs |
| `@module-federation/vite` as alternative | MEDIUM | Announced but adoption level not verified post-Aug 2025 |
| Gemini embedding API batch size limits | LOW | Verify with current Gemini docs before implementing |

**Note:** WebSearch was unavailable during this research session. All findings are based on training data (cutoff August 2025) and direct knowledge of the specified stack. Flag items marked LOW or MEDIUM for verification in their respective phase research.

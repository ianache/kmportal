# Stack Reference: Knowledge Management Platform

> **WEB VERIFICATION UNAVAILABLE**
> All version numbers, API shapes, and compatibility claims below are derived from
> training-data knowledge (cutoff August 2025). Every version claim is marked
> `[verify before use]`. Before pinning any version in `pyproject.toml`, `package.json`,
> or a Docker image tag, confirm against the official source (PyPI, npm, Docker Hub,
> or the project's own changelog).
>
> This document is a complete skeleton — intentionally erring on the side of coverage.
> A roadmap builder reading this should treat it as a structured checklist, not a
> copy-paste manifest.

**Researched:** 2026-05-02
**Updated:** 2026-05-03 (v1.1 milestone additions)
**Status:** Training-data draft — pending web verification

---

## Table of Contents

1. [Language Runtimes](#1-language-runtimes)
2. [Python Ecosystem (Core API + Ingestion Worker)](#2-python-ecosystem-core-api--ingestion-worker)
3. [Node.js Ecosystem (BFF)](#3-nodejs-ecosystem-bff)
4. [Frontend Ecosystem (Vue Shell + Micro UIs)](#4-frontend-ecosystem-vue-shell--micro-uis)
5. [Databases and Storage](#5-databases-and-storage)
6. [Message Brokers](#6-message-brokers)
7. [Auth and Security](#7-auth-and-security)
8. [LLM and Embedding Providers](#8-llm-and-embedding-providers)
9. [Infrastructure and DevOps](#9-infrastructure-and-devops)
10. [Observability](#10-observability)
11. [Testing](#11-testing)
12. [Version Compatibility Matrix](#12-version-compatibility-matrix)
13. [Package Manager Commands](#13-package-manager-commands)
14. [Upgrade and Migration Notes](#14-upgrade-and-migration-notes)

---

## 1. Language Runtimes

### Python

| Item | Value | Notes |
|------|-------|-------|
| **Minimum version** | `3.13` [verify before use] | Project constraint — do not downgrade |
| **Package manager** | `uv` [verify before use] | Project constraint — do not use pip or poetry |
| **uv version** | `0.4+` [verify before use] | Check `pip show uv` or `uv --version` |
| **Virtual env** | Managed by uv (`uv venv`) | `uv sync` installs from `pyproject.toml` |
| **Lockfile** | `uv.lock` | Commit this file; do not gitignore |

Key Python 3.13 features used:
- `tomllib` in stdlib (no extra dep for config parsing)
- Improved `asyncio` task group ergonomics
- Free-threaded mode available (not enabled by default; not required here)

### Node.js

| Item | Value | Notes |
|------|-------|-------|
| **Minimum version** | `20 LTS` [verify before use] | Check `node --version` |
| **Recommended version** | `22 LTS` [verify before use] | Latest even-numbered LTS as of Aug 2025 |
| **Package manager** | `npm` or `pnpm` [verify before use] | Choose one and pin it; pnpm preferred for monorepo workspace |
| **pnpm version** | `9+` [verify before use] | Required for workspace protocol |

---

## 2. Python Ecosystem (Core API + Ingestion Worker)

### Web Framework

| Package | Version | Purpose | Notes |
|---------|---------|---------|-------|
| `fastapi` | `0.115+` [verify before use] | HTTP framework for Core API | Pydantic v2 required by FastAPI 0.100+ |
| `uvicorn[standard]` | `0.30+` [verify before use] | ASGI server | `[standard]` adds uvloop + httptools |
| `pydantic` | `v2.x` [verify before use] | Request/response validation, settings | v2 is a hard dependency of FastAPI 0.100+; do not use v1 |
| `pydantic-settings` | `2.x` [verify before use] | `BaseSettings` for env-var config | Replaces `pydantic.BaseSettings` removed in v2 |
| `python-multipart` | `0.0.9+` [verify before use] | File upload support in FastAPI | Required for `UploadFile` to work |
| `starlette` | Pinned by FastAPI | ASGI toolkit | Do not pin separately — let FastAPI control the version |

### MCP Server

| Package | Version | Purpose | Notes |
|---------|---------|---------|-------|
| `fastmcp` | `0.4+` [verify before use] | Model Context Protocol server | Mount as ASGI sub-app on FastAPI; check `fastmcp.FastMCP.as_asgi()` API |
| `mcp` | `1.x` [verify before use] | MCP protocol primitives | FastMCP depends on this; usually transitive |

FastMCP ASGI mount pattern [verify before use]:
```python
from fastapi import FastAPI
from fastmcp import FastMCP

mcp = FastMCP("knowledge-mcp")
app = FastAPI()
app.mount("/mcp", mcp.as_asgi())
```

### Auth and JWT

| Package | Version | Purpose | Notes |
|---------|---------|---------|-------|
| `python-jose[cryptography]` | `3.3+` [verify before use] | JWT validation (RS256 from Keycloak) | `[cryptography]` backend required for RS256 |
| `httpx` | `0.27+` [verify before use] | Async HTTP client (JWKS fetch, internal calls) | Preferred over `requests` for async FastAPI code |
| `cryptography` | `42+` [verify before use] | Crypto primitives (transitive via jose) | Pin minimum; OpenSSL-linked |

Keycloak JWKS endpoint pattern:
```
https://oauth2.qa.comsatel.com.pe/realms/Apps/protocol/openid-connect/certs
```
Cache the JWKS response; re-fetch only on `kid` miss.

### Database Clients

| Package | Version | Purpose | Notes |
|---------|---------|---------|-------|
| `asyncpg` | `0.29+` [verify before use] | Async PostgreSQL driver | Fastest async PG driver; works with SQLAlchemy async |
| `sqlalchemy[asyncio]` | `2.x` [verify before use] | ORM + query builder for PostgreSQL | Use async session (`AsyncSession`) only |
| `alembic` | `1.13+` [verify before use] | Database migrations for PostgreSQL | Generates migration scripts from SQLAlchemy models |
| `motor` | `3.x` [verify before use] | Async MongoDB driver (pymongo-based) | For chunks and raw document content |
| `pymongo` | `4.x` [verify before use] | Sync MongoDB driver (used by motor internally) | Usually pulled in transitively by motor |
| `chromadb` | `0.5+` [verify before use] | Vector store client (MVP) | Import only inside `adapters/vectorstore/chroma.py` |
| `qdrant-client` | `1.9+` [verify before use] | Vector store client (v2 migration) | Import only inside `adapters/vectorstore/qdrant.py` |
| `redis[asyncio]` | `5.x` [verify before use] | Redis client for pub/sub and session cache | Use `redis.asyncio` (async interface) |

SQLAlchemy async engine pattern [verify before use]:
```python
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker

engine = create_async_engine("postgresql+asyncpg://...", echo=False)
AsyncSessionLocal = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)
```

### Ontology API — Backend (v1.1, NEW)

**No new Python packages required.** The ontology graph is stored as JSONB in PostgreSQL,
which SQLAlchemy 2.x already supports via `sqlalchemy.dialects.postgresql.JSONB`.
The existing `asyncpg`, `sqlalchemy[asyncio]`, and `alembic` cover all needs.

What needs to be added to the existing codebase (not new packages):

1. **Alembic migration** — add `ontology_data JSONB NOT NULL DEFAULT '{}'` column to the
   `domains` table, or create a separate `domain_ontologies` table (see Section 5 for the
   storage decision).

2. **SQLAlchemy model** — add `ontology_data` column to `Domain` model using `JSONB`:
   ```python
   from sqlalchemy.dialects.postgresql import JSONB
   ontology_data = Column(JSONB, nullable=False, server_default='{"nodes": [], "edges": []}')
   ```

3. **Pydantic schemas** — add `OntologyGraph`, `OntologyNode`, `OntologyEdge` schemas.

4. **Router** — add two routes to `api/src/api/domains.py`:
   - `GET /v1/domains/{domain_id}/ontology`
   - `PUT /v1/domains/{domain_id}/ontology`

5. **Service method** — add `get_ontology` and `update_ontology` to `DomainService`.

### Document Parsing

| Package | Version | Purpose | Notes |
|---------|---------|---------|-------|
| `pymupdf` | `1.24+` [verify before use] | PDF text extraction (also known as `fitz`) | Best balance of accuracy and speed for enterprise PDFs |
| `pdfminer.six` | `20221105+` [verify before use] | Alternative PDF parser (fallback) | Better at complex layouts; slower than PyMuPDF |
| `chardet` | `5.x` [verify before use] | Character encoding detection for text files | For files without a declared encoding |
| `pygments` | `2.18+` [verify before use] | Source code language detection and tokenization | Used in code ingestion to detect language |
| `tree-sitter` | `0.22+` [verify before use] | AST-based code parsing (optional enhancement) | Only needed if semantic code chunking is required |

### Embedding and LLM

| Package | Version | Purpose | Notes |
|---------|---------|---------|-------|
| `google-generativeai` | `0.7+` [verify before use] | Gemini embedding API client | Import only inside `adapters/embeddings/gemini.py` |
| `openai` | `1.30+` [verify before use] | OpenAI embedding API client (future) | Import only inside `adapters/embeddings/openai.py` |
| `tiktoken` | `0.7+` [verify before use] | Token counting for OpenAI models | Useful for chunking logic even with Gemini (as rough count) |

Embedding port contract (enforce this — do not let providers leak):
```python
from abc import ABC, abstractmethod

class EmbeddingPort(ABC):
    @property
    @abstractmethod
    def dimension(self) -> int: ...

    @abstractmethod
    async def embed_documents(self, texts: list[str]) -> list[list[float]]: ...

    @abstractmethod
    async def embed_query(self, text: str) -> list[float]: ...
```

### Message Broker Clients

| Package | Version | Purpose | Notes |
|---------|---------|---------|-------|
| `aiokafka` | `0.11+` [verify before use] | Async Kafka consumer/producer | For ingestion trigger events from Kafka topics |
| `aio-pika` | `9.x` [verify before use] | Async RabbitMQ client (AMQP) | For ingestion trigger events from RabbitMQ queues |
| `boto3` | `1.34+` [verify before use] | AWS S3 client (sync; wrap in asyncio executor) | For S3 source connector |
| `aioboto3` | `12+` [verify before use] | Async wrapper around boto3 | Preferred for async S3 polling in ingestion worker |

### Task Queue (Ingestion Worker)

| Package | Version | Purpose | Notes |
|---------|---------|---------|-------|
| `celery[redis]` | `5.4+` [verify before use] | Task queue for async ingestion jobs (option A) | If separate worker process is used; `[redis]` broker backend |
| `arq` | `0.26+` [verify before use] | Lightweight async task queue using Redis (option B) | Simpler than Celery for async-first codebases |

Recommendation: Start with `arq` (fewer moving parts, native asyncio). Migrate to Celery only if you need beat scheduling, canvas workflows, or cross-language task interop.

### Code Quality and Static Analysis

| Package | Version | Purpose | Notes |
|---------|---------|---------|-------|
| `ruff` | `0.5+` [verify before use] | Linter + formatter (replaces flake8, isort, black) | Configure with `[tool.ruff]` in `pyproject.toml` |
| `mypy` | `1.10+` [verify before use] | Static type checking | Use `--strict` mode; FastAPI/Pydantic stubs are bundled |
| `import-linter` | `2.x` [verify before use] | Enforce import boundaries (e.g., ban chromadb outside adapter) | Critical for enforcing adapter isolation |
| `pre-commit` | `3.7+` [verify before use] | Git hook runner (runs ruff, mypy, tests) | Configure in `.pre-commit-config.yaml` |

---

## 3. Node.js Ecosystem (BFF)

### Framework

| Package | Version | Purpose | Notes |
|---------|---------|---------|-------|
| `fastify` | `4.x` [verify before use] | HTTP framework for BFF (faster than Express) | Native async/await, schema validation built-in |
| `@fastify/cookie` | `9.x` [verify before use] | Cookie parsing/setting for session | Required for HttpOnly session cookie |
| `@fastify/session` | `10.x` [verify before use] | Server-side session management | Backed by Redis store |
| `connect-redis` | `7.x` [verify before use] | Redis session store adapter | If using express-session pattern; Fastify has its own |
| `@fastify/proxy-http` | `3.x` [verify before use] | HTTP proxy plugin for forwarding to Core API | Alternative: `fastify-http-proxy` |
| `@fastify/websocket` | `10.x` [verify before use] | WebSocket support for BFF | Built on `ws` under the hood |
| `@fastify/rate-limit` | `9.x` [verify before use] | Rate limiting before Core API | Protects against abuse |

Alternative: Use `express` + `express-session` + `ws` if team is more familiar. Fastify recommended for performance, but the architecture is framework-agnostic.

### Auth (OAuth2 / OIDC)

| Package | Version | Purpose | Notes |
|---------|---------|---------|-------|
| `openid-client` | `5.x` [verify before use] | OIDC Authorization Code flow with Keycloak | De facto standard for server-side OIDC in Node.js |
| `jose` | `5.x` [verify before use] | JWT verification in Node.js (Keycloak public key) | Used by openid-client; can be used directly |

Keycloak discovery URL:
```
https://oauth2.qa.comsatel.com.pe/realms/Apps/.well-known/openid-configuration
```
Use `openid-client`'s `Issuer.discover()` to auto-fetch endpoints and public keys.

### Redis Client

| Package | Version | Purpose | Notes |
|---------|---------|---------|-------|
| `ioredis` | `5.x` [verify before use] | Redis client for session store and pub/sub | Supports cluster mode; preferred over `redis` npm package |

### HTTP Client (BFF → Core API)

| Package | Version | Purpose | Notes |
|---------|---------|---------|-------|
| `undici` | `6.x` [verify before use] | Fast native HTTP client (used internally by Node.js 18+) | Preferred for Core API proxying; no external dep |
| `axios` | `1.7+` [verify before use] | Alternative HTTP client if interceptor patterns needed | Familiar API for teams coming from browser JS |

### Configuration and Logging

| Package | Version | Purpose | Notes |
|---------|---------|---------|-------|
| `zod` | `3.23+` [verify before use] | Runtime config schema validation | Validate env vars on startup |
| `dotenv` | `16.x` [verify before use] | Load `.env` files in development | Do not use in production containers |
| `pino` | `9.x` [verify before use] | Structured JSON logger (fast, Fastify-native) | Built into Fastify; configure `level`, `transport` |
| `pino-pretty` | `11.x` [verify before use] | Human-readable pino output for dev | Dev-only; do not use in production |

### Type Safety

| Package | Version | Purpose | Notes |
|---------|---------|---------|-------|
| `typescript` | `5.5+` [verify before use] | TypeScript compiler for BFF | Use `strict: true` in `tsconfig.json` |
| `tsx` | `4.x` [verify before use] | TypeScript execute (fast dev run) | Replaces `ts-node` for development |
| `@types/node` | Match Node.js version [verify before use] | Node.js type definitions | Pin to match your Node.js major version |

### Code Quality

| Package | Version | Purpose | Notes |
|---------|---------|---------|-------|
| `eslint` | `9.x` [verify before use] | Linter for TypeScript/JavaScript | Use flat config format (eslint.config.js) |
| `@typescript-eslint/eslint-plugin` | `7.x` [verify before use] | TypeScript-specific ESLint rules | |
| `prettier` | `3.x` [verify before use] | Code formatter | Integrate with ESLint via `eslint-config-prettier` |

---

## 4. Frontend Ecosystem (Vue Shell + Micro UIs)

### Core Framework (Confirmed Installed Versions)

| Package | Installed Version | Purpose | Notes |
|---------|------------------|---------|-------|
| `vue` | `3.5.33` (confirmed) | UI framework — must be singleton across all micro UIs | Declared `singleton: true, eager: true` in shell MF config |
| `pinia` | `^2.1.0` (package.json) | State management — must be singleton | Shared store instance exposed by shell |
| `vue-router` | `^4.3.0` (package.json) | Routing — must be singleton | Shell owns the router instance |
| `@vueuse/core` | `10.x` [verify before use] | Vue 3 composable utilities | Optional but widely used |

### Build Tools (Confirmed Installed Versions)

| Package | Installed Version | Purpose | Notes |
|---------|------------------|---------|-------|
| `vite` | `5.4.21` (confirmed) | Build tool and dev server for all frontend apps | Fast HMR; ESM-native |
| `@vitejs/plugin-vue` | `^5.0.0` (package.json) | Vite plugin for `.vue` files | Match major version with Vite |
| `typescript` | `^5.5.0` (package.json) | TypeScript in frontend | Same version pinned as BFF (workspace constraint) |

### Micro-Frontend (Confirmed Installed Version)

| Package | Installed Version | Purpose | Notes |
|---------|------------------|---------|-------|
| `@originjs/vite-plugin-federation` | `1.4.1` (confirmed) | Module Federation for Vite | Currently installed in both shell and domains-ui |

Singleton config already in use (confirmed from `vite.config.ts`):
```js
// shell vite.config.ts — confirmed current configuration
federation({
  name: 'shell',
  remotes: {
    domainsUi: 'http://localhost:5101/assets/remoteEntry.js',
    searchUi: 'http://localhost:5103/assets/remoteEntry.js',
    ingestionUi: 'http://localhost:5102/assets/remoteEntry.js',
    adminUi: 'http://localhost:5104/assets/remoteEntry.js',
  },
  shared: {
    vue:          { singleton: true, eager: true, requiredVersion: '^3.4.0' },
    pinia:        { singleton: true, eager: true, requiredVersion: '^2.1.0' },
    'vue-router': { singleton: true, eager: true, requiredVersion: '^4.3.0' },
  }
})
```

### Canvas / Graph Library for Ontology Editor (v1.1, NEW)

**Recommendation: `@vue-flow/core`**

| Package | Version | Purpose | Why |
|---------|---------|---------|-----|
| `@vue-flow/core` | `^1.42.0` [verify before use] | Ontology editor canvas — nodes, edges, drag/connect | Only first-class Vue 3 canvas library; renders via SVG+DOM; exposes `useVueFlow()` composable; no React dependency |
| `@vue-flow/background` | `^1.3.0` [verify before use] | Dotted/line grid background for canvas | Optional but improves spatial UX |
| `@vue-flow/controls` | `^1.1.0` [verify before use] | Built-in zoom +/−, fit-to-window buttons | Use as reference implementation; will be superseded by the custom Toolbox component |

**Why `@vue-flow/core` over alternatives:**

- **Cytoscape.js** — headless graph library with imperative DOM manipulation. Not Vue-idiomatic; requires mounting to a raw `<div>` and manual bridging to Vue reactivity. Works well for read-only graph display but poor DX for interactive node editing in Vue SFCs. No built-in drag-to-connect edge creation.
- **D3.js** — low-level visualization primitives. Powerful but requires building every interaction from scratch (node dragging, edge routing, zoom/pan). Estimated 3-5x more implementation effort than Vue Flow for the same feature set.
- **React Flow / @xyflow/react** — the upstream library Vue Flow is ported from. Not usable directly in Vue — React runtime would conflict catastrophically with Vue's virtual DOM in the same Module Federation scope.
- **@vue-flow/core** — purpose-built Vue 3 port of React Flow. Node and edge types are Vue SFCs. Uses Vue reactivity natively. Exposes `useVueFlow()` composable. Actively maintained as of training cutoff. **Most DX-appropriate choice for this stack.**

**Vue Flow integration note for Module Federation:**
`@vue-flow/core` must be declared in the `shared` config of `domainsUi`'s `vite.config.ts` if the ontology editor lives in `domains-ui`. Do NOT declare it `singleton: true` — it is not a shared runtime like Vue itself, so let each remote bundle its own copy. The concern is only size, not correctness.

```js
// domains-ui/vite.config.ts — add @vue-flow/core to dependencies only (not shared)
// No change to shared config needed for @vue-flow/core
```

**Node data shape for ontology:**
```typescript
// OntologyNode — Vue Flow custom node data
interface OntologyNodeData {
  label: string;         // concept name
  type: string;          // e.g. "entity", "concept", "relationship"
  description: string;
  color: string;         // hex color for node header
  icon?: string;         // optional icon identifier
}
```

### Shared Canvas Toolbox (v1.1, NEW)

**Recommendation: Build as a Vue SFC lib package, exposed by `domains-ui` via Module Federation.**

The milestone spec places this in `frontend/libs/canvas-toolbox`. The existing monorepo has no
`frontend/libs` or `frontend/packages` directory yet. Two structural options exist:

**Option A (Recommended): `frontend/libs/canvas-toolbox` as a local workspace package**

Create `frontend/libs/canvas-toolbox/package.json` with `name: "@kmp/canvas-toolbox"`.
Add to pnpm workspace (or npm workspace). Each consuming remote (`domains-ui`, future
`ingestion-ui`) adds it as a local dep: `"@kmp/canvas-toolbox": "workspace:*"`.

```
frontend/
  libs/
    canvas-toolbox/          # @kmp/canvas-toolbox
      package.json           # name: "@kmp/canvas-toolbox", type: "module"
      src/
        CanvasToolbox.vue    # Toolbox component
        index.ts             # exports { CanvasToolbox }
```

Toolbox component receives its actions via props/emits rather than directly importing
`@vue-flow/core` — this keeps the toolbox independent of any specific canvas library:
```typescript
// CanvasToolbox.vue props
interface Props {
  onZoomIn: () => void;
  onZoomOut: () => void;
  onFitView: () => void;
  onToggleGrid: () => void;
  snapEnabled: boolean;
}
```
The caller (ontology editor in `domains-ui`) passes `useVueFlow()`'s `zoomIn`, `zoomOut`,
`fitView` functions as props. The future ingestion flow editor passes its own canvas
controls. This decoupling means `@kmp/canvas-toolbox` has zero dependencies on
`@vue-flow/core` — it is pure Vue 3 + CSS.

**Option B (Avoid): Shell-exported shared component via Module Federation**

The shell could expose a `./CanvasToolbox` component in its `exposes` block. This would
allow any remote to `import CanvasToolbox from 'shell/CanvasToolbox'`.

*Why to avoid:* The shell is a runtime host — adding domain-specific UI components to it
creates coupling between the shell and feature development. Shell changes require
coordinated redeployment. A workspace lib package can be developed and versioned
independently, and is compiled into each consuming remote's bundle (no runtime dependency
on the shell).

**Installation command:**
```bash
# In frontend/libs/canvas-toolbox/
npm init --scope @kmp  # or create package.json manually

# In domains-ui/ (consuming package)
pnpm --filter domains-ui add @kmp/canvas-toolbox --workspace
```

### UI Components

| Package | Version | Purpose | Notes |
|---------|---------|---------|-------|
| `tailwindcss` | `3.4+` [verify before use] | Utility CSS — matches DESIGN.md token system | Configure with Inter font, custom color tokens |
| `@headlessui/vue` | `1.7+` [verify before use] | Accessible unstyled UI primitives (dialogs, dropdowns) | Matches Tailwind ecosystem |
| `lucide-vue-next` | `0.400+` [verify before use] | Icon set | Clean SVG icons; tree-shakeable |

Design system tokens (from DESIGN.md) should be mapped in `tailwind.config.ts`:
- Primary blue: `#007AFF` (override `primary` in Tailwind)
- Background: `#F5F5F7`
- Body font: Inter (import from Google Fonts or bundle via Fontsource)

### HTTP Client (Frontend → BFF)

| Package | Version | Purpose | Notes |
|---------|---------|---------|-------|
| `axios` | `1.7+` [verify before use] | HTTP client used in `@kmp/api-client` shared package | Configure base URL + CSRF header in one place |

CSRF protection note: Since BFF uses HttpOnly session cookies, the frontend does not handle tokens — but you need a CSRF token mechanism. Use `@fastify/csrf-protection` on the BFF and attach `X-CSRF-Token` header via the `@kmp/api-client` shared package.

### WebSocket Client

| Package | Version | Purpose | Notes |
|---------|---------|---------|-------|
| Native `WebSocket` | Browser built-in | BFF WebSocket connection | No extra package; manage reconnect logic in `@kmp/auth` composable |

Reconnect pattern: implement exponential backoff reconnect in a `useWebSocket()` composable in `@kmp/auth` package. Exposed to all micro UIs via Module Federation shared scope.

### Workspace / Monorepo

| Tool | Version | Purpose | Notes |
|------|---------|---------|-------|
| `pnpm workspaces` | `9+` [verify before use] | Manage `@kmp/*` shared packages + all micro UIs in one repo | Define workspace in root `pnpm-workspace.yaml` |
| `turbo` | `2.x` [verify before use] | Monorepo build orchestration (optional) | Useful for parallel builds across micro UIs |

**Current confirmed structure** (no `libs/` or `packages/` yet):
```
frontend/
  apps/
    shell/           # host app — port 5100
    domains-ui/      # remote — port 5101
    search-ui/       # remote — port 5103
    ingestion-ui/    # remote — port 5102
    admin-ui/        # remote — port 5104
```

**Target structure after v1.1** (add `libs/`):
```
frontend/
  libs/
    canvas-toolbox/  # @kmp/canvas-toolbox (new in v1.1)
  apps/
    shell/
    domains-ui/      # ontology editor lives here
    search-ui/
    ingestion-ui/
    admin-ui/
```

### Code Quality

| Package | Version | Purpose | Notes |
|---------|---------|---------|-------|
| `eslint` | `9.x` [verify before use] | Linting for Vue + TypeScript | Use `eslint-plugin-vue` |
| `eslint-plugin-vue` | `9.x` [verify before use] | Vue 3 specific ESLint rules | |
| `prettier` | `3.x` [verify before use] | Formatting | Shared config at workspace root |
| `rollup-plugin-visualizer` | `5.x` [verify before use] | Bundle size analysis | Use to detect MF shared dep leakage |

---

## 5. Databases and Storage

### PostgreSQL — Ontology Storage (v1.1, NEW)

**Recommendation: Single JSONB column `ontology_data` on the `domains` table.**

```sql
-- Alembic migration (add to existing domains table)
ALTER TABLE domains ADD COLUMN ontology_data JSONB NOT NULL DEFAULT '{"nodes": [], "edges": []}';
```

**Why JSONB over separate `ontology_nodes` / `ontology_edges` tables:**

| Concern | JSONB single column | Separate tables |
|---------|--------------------|-----------------| 
| Query complexity | Read/write entire graph in one query | JOIN-heavy for full graph retrieval |
| Schema flexibility | Node/edge shapes evolve freely | Schema migration per shape change |
| Atomic update | `UPDATE domains SET ontology_data=$1` | Multi-table transaction |
| Indexing (if needed later) | GIN index on JSONB for node/edge lookup | B-tree indexes per column |
| SQLAlchemy ORM fit | Trivially mapped to `Column(JSONB)` | Requires new model classes + relationships |
| Use pattern here | Always read/write full graph (editor loads all, saves all) | Needed only for partial updates at scale |

The deciding factor is the access pattern: the ontology editor always loads the full graph
and saves the full graph as a unit. There is no query requirement like "find all domains
where a node named X exists" (that would favor separate tables or a GIN index). A JSONB
blob is the correct fit.

**When to reconsider:** If the ontology grows beyond ~500 nodes per domain AND you need
server-side filtering of nodes, switch to separate tables. A migration from JSONB → tables
is straightforward via Alembic. This is a Neo4J migration target already in the roadmap
(PROJECT.md line 49), so the JSONB representation is intentionally transient.

**SQLAlchemy model change (no new packages):**
```python
from sqlalchemy.dialects.postgresql import JSONB

class Domain(Base):
    # ... existing columns ...
    ontology_data = Column(
        JSONB,
        nullable=False,
        server_default='{"nodes": [], "edges": []}',
    )
```

**Pydantic schema:**
```python
class OntologyNode(BaseModel):
    id: str                    # client-generated UUID
    position_x: float
    position_y: float
    data: OntologyNodeData

class OntologyEdge(BaseModel):
    id: str
    source: str                # node id
    target: str                # node id
    label: str | None = None

class OntologyNodeData(BaseModel):
    label: str
    type: str
    description: str
    color: str
    icon: str | None = None

class OntologyGraph(BaseModel):
    nodes: list[OntologyNode] = []
    edges: list[OntologyEdge] = []
```

### PostgreSQL (General)

| Item | Value | Notes |
|------|-------|-------|
| **Version** | `16` [verify before use] | Latest stable as of Aug 2025; check Docker Hub `postgres` tags |
| **Docker image** | `postgres:16-alpine` [verify before use] | Alpine for smaller image size |
| **Extensions** | `uuid-ossp` or `gen_random_uuid()` (built-in in PG13+) | Use `gen_random_uuid()` — no extension needed in PG13+ |
| **Full-text search** | `tsvector` / `tsquery` built-in | For hybrid search keyword component |
| **Connection pooling** | `pgbouncer` (recommended for prod) [verify before use] | Or SQLAlchemy's built-in pool for MVP |

Key schema tables (see ARCHITECTURE.md for full schema):
- `domains`, `documents`, `ingestion_jobs`, `api_keys`, `users`
- **`domains.ontology_data`** (new in v1.1)

Index recommendations:
- `documents(domain_id, status)` — for filtered queries during ingestion
- `ingestion_jobs(status, started_at)` — for job queue processing
- `api_keys(key_hash)` — unique index; every API call lookups here
- GIN index on `domains.ontology_data` — only if server-side node filtering is required (likely not in v1.1)

### MongoDB

| Item | Value | Notes |
|------|-------|-------|
| **Version** | `7.x` [verify before use] | Latest stable as of Aug 2025 |
| **Docker image** | `mongo:7` [verify before use] | |
| **Driver** | `motor 3.x` (async) [verify before use] | |
| **Collections** | `documents`, `chunks` | See ARCHITECTURE.md |
| **Indexes** | `chunks: { doc_id: 1, chunk_index: 1 }` (unique) | Required for upsert idempotency |

MongoDB text index for hybrid search keyword component:
```js
db.chunks.createIndex({ text: "text" }, { defaultLanguage: "none" })
```
`defaultLanguage: "none"` disables stemming — better for technical content.

### ChromaDB (MVP Vector Store)

| Item | Value | Notes |
|------|-------|-------|
| **Version** | `0.5+` [verify before use] | Breaking API changes between 0.4 and 0.5 — check release notes |
| **Deployment** | Embedded (in-process) for dev; `chromadb-server` for staging/prod | |
| **Docker image** | `chromadb/chroma:0.5.x` [verify before use] | |
| **Client** | `chromadb` Python package [verify before use] | Only imported in `adapters/vectorstore/chroma.py` |
| **Collection per domain** | Yes — one ChromaDB collection per knowledge domain | Collection name: `domain_{domain_id}` |

ChromaDB HTTP client pattern (for deployed server):
```python
import chromadb
client = chromadb.HttpClient(host=settings.CHROMA_HOST, port=settings.CHROMA_PORT)
```

### Qdrant (v2 Vector Store — Migration Target)

| Item | Value | Notes |
|------|-------|-------|
| **Version** | `1.9+` [verify before use] | |
| **Docker image** | `qdrant/qdrant:v1.9.x` [verify before use] | |
| **Client** | `qdrant-client` Python package [verify before use] | Only imported in `adapters/vectorstore/qdrant.py` |
| **Namespacing** | Use Qdrant Collections (one per domain) + payload filtering | Equivalent to ChromaDB collection model |

Migration trigger: switch environment variable `VECTOR_STORE=qdrant` and re-index. See ARCHITECTURE.md VectorStoreAdapter pattern.

### Redis

| Item | Value | Notes |
|------|-------|-------|
| **Version** | `7.x` [verify before use] | |
| **Docker image** | `redis:7-alpine` [verify before use] | |
| **Use cases** | BFF session store, pub/sub (worker → BFF WebSocket relay), rate-limit counters | |
| **Persistence** | AOF persistence recommended for session store | Disable for pure cache/rate-limit use |

Redis pub/sub channel naming convention:
```
ingest.events.{user_id}    # per-user ingestion events
ingest.events.broadcast    # system-wide events
```

### Object Storage (S3)

| Item | Value | Notes |
|------|-------|-------|
| **AWS S3** | Production object storage | Use `aioboto3` in ingestion worker |
| **MinIO** | S3-compatible local/staging alternative [verify before use] | Docker: `minio/minio:latest` |
| **Event triggers** | S3 Event Notifications → SQS → Ingestion Worker | For production event-driven ingestion |

---

## 6. Message Brokers

### Kafka

| Item | Value | Notes |
|------|-------|-------|
| **Version** | `3.7+` [verify before use] | |
| **Docker image** | `confluentinc/cp-kafka:7.6.x` [verify before use] | Confluent Platform packages Kafka + ZooKeeper/KRaft |
| **Mode** | KRaft mode (ZooKeeper-free) recommended for new deployments [verify before use] | KRaft GA since Kafka 3.3 |
| **Python client** | `aiokafka 0.11+` [verify before use] | Async Kafka consumer |
| **Ingestion topic** | `km.ingest.requests` | Document ingestion trigger messages |
| **DLQ topic** | `km.ingest.requests.DLQ` | Dead letter queue for failed processing |
| **Consumer group** | `km-ingestion-worker` | |

Kafka message schema (ingestion trigger):
```json
{
  "schema_version": "1",
  "doc_id": "uuid",
  "domain_id": "uuid",
  "source_type": "kafka",
  "payload": { "content": "base64-encoded" | "s3_key": "string" },
  "metadata": { "author": "string", "tags": [] },
  "submitted_by": "user_id or api_key_id"
}
```

### RabbitMQ

| Item | Value | Notes |
|------|-------|-------|
| **Version** | `3.13+` [verify before use] | |
| **Docker image** | `rabbitmq:3.13-management-alpine` [verify before use] | `-management` adds admin UI on port 15672 |
| **Python client** | `aio-pika 9.x` [verify before use] | Async AMQP client |
| **Exchange** | `km.ingest` (direct exchange) | Route by `routing_key=ingest.request` |
| **Queue** | `km.ingest.requests` | Durable queue bound to exchange |
| **DLQ** | `km.ingest.dlq` | Set via `x-dead-letter-exchange` argument |

RabbitMQ queue declaration (ensure idempotent setup):
```python
queue = await channel.declare_queue(
    "km.ingest.requests",
    durable=True,
    arguments={"x-dead-letter-exchange": "km.ingest.dlx", "x-max-retries": 5},
)
```

---

## 7. Auth and Security

### Keycloak

| Item | Value | Notes |
|------|-------|-------|
| **Version** | `26+` [verify before use] | Existing instance — do not control this version |
| **Host** | `https://oauth2.qa.comsatel.com.pe` | Project constraint |
| **Realm** | `Apps` | Project constraint |
| **Client ID** | `kmplatform` | Project constraint |
| **Grant type (web)** | Authorization Code with PKCE | BFF handles the flow; frontend never sees tokens |
| **Grant type (service)** | Client Credentials | For FastMCP service account and internal service-to-service |
| **Token algorithm** | RS256 [verify before use] | Verify in Keycloak client config |
| **JWKS endpoint** | `{host}/realms/Apps/protocol/openid-connect/certs` | Used by Core API to validate JWTs |
| **Token endpoint** | `{host}/realms/Apps/protocol/openid-connect/token` | Used by BFF for code exchange |
| **Logout endpoint** | `{host}/realms/Apps/protocol/openid-connect/logout` | Used by BFF on logout |

Required Keycloak client config for `kmplatform`:
- **Access Type:** `confidential` (has client_secret)
- **Valid redirect URIs:** `https://bff.kmp.local/auth/callback`
- **Web origins:** `https://shell.kmp.local` (CORS)
- **Roles to create in realm:** `km-admin`, `km-reader`

### API Key Security

| Decision | Implementation |
|----------|---------------|
| Key format | UUID v4 (128-bit random) — NOT sequential or predictable |
| Storage | SHA-256 hash stored in PostgreSQL `api_keys.key_hash` |
| Transmission | HTTPS only; `X-API-Key` header |
| Rotation | New key issued, old key immediately revoked |
| Scopes | Array of strings: `["read:search", "read:documents", "admin:all"]` |
| Rate limiting | Per-key rate limit tracked in Redis |

### Secret Management

| Item | Rule |
|------|------|
| Database passwords | Environment variables — never in code or Docker image |
| Keycloak client_secret | Environment variable |
| Gemini API key | Environment variable |
| Redis password | Environment variable |
| API key secrets | Never stored plaintext — only the SHA-256 hash |
| `.env` files | In `.gitignore`; `.env.example` committed with placeholder values |

---

## 8. LLM and Embedding Providers

### Gemini (Default)

| Item | Value | Notes |
|------|-------|-------|
| **Package** | `google-generativeai 0.7+` [verify before use] | Or `google-genai` (newer SDK alias — verify package name) |
| **Embedding model** | `models/text-embedding-004` [verify before use] | 768 dimensions [verify before use] |
| **Document task type** | `RETRIEVAL_DOCUMENT` [verify before use] | Passed internally in `GeminiEmbeddingAdapter` |
| **Query task type** | `RETRIEVAL_QUERY` [verify before use] | Improves asymmetric retrieval quality |
| **Batch size limit** | ~100 texts per call [verify before use] | LOW confidence — verify with current API docs |
| **Rate limits** | Depends on billing tier [verify before use] | Implement exponential backoff + retry |
| **Dimension** | `768` [verify before use] | Store per-domain in PostgreSQL; changing this requires re-index |

Critical: Store `embedding_model` and `embedding_dimension` per domain in PostgreSQL. Switching models without re-indexing corrupts results.

### OpenAI (Future / Secondary)

| Item | Value | Notes |
|------|-------|-------|
| **Package** | `openai 1.30+` [verify before use] | |
| **Embedding model** | `text-embedding-3-small` (1536-dim) or `text-embedding-3-large` (3072-dim) [verify before use] | Different dimension from Gemini — per-domain, cannot mix |
| **Batch size** | Up to 2048 inputs per call [verify before use] | Verify current limits |

### Local Models (Future)

| Tool | Notes |
|------|-------|
| `Ollama` | Serve local embedding models (e.g., `nomic-embed-text`); OpenAI-compatible API endpoint |
| `sentence-transformers` | Python library for local SBERT models; implement `LocalEmbeddingAdapter` |

### LLM Provider Adapter Contract

```python
# adapters/embeddings/base.py — only file other code should import from
class EmbeddingPort(ABC):
    @property
    @abstractmethod
    def dimension(self) -> int: ...
    @abstractmethod
    async def embed_documents(self, texts: list[str]) -> list[list[float]]: ...
    @abstractmethod
    async def embed_query(self, text: str) -> list[float]: ...

def get_embedding_provider(settings: Settings) -> EmbeddingPort:
    match settings.EMBEDDING_PROVIDER:
        case "gemini": return GeminiEmbeddingAdapter(settings)
        case "openai": return OpenAIEmbeddingAdapter(settings)
        case "local":  return LocalEmbeddingAdapter(settings)
        case _: raise ValueError(f"Unknown provider: {settings.EMBEDDING_PROVIDER}")
```

---

## 9. Infrastructure and DevOps

### Docker

| Item | Value | Notes |
|------|-------|-------|
| **Docker Engine** | `26+` [verify before use] | |
| **Docker Compose** | `v2` (built-in plugin, `docker compose`) [verify before use] | Do not use legacy `docker-compose` v1 |
| **Base image — Python** | `python:3.13-slim` [verify before use] | Slim variant; add only required system deps |
| **Base image — Node.js** | `node:22-alpine` [verify before use] | Alpine for BFF |
| **Base image — Frontend** | `nginx:1.27-alpine` [verify before use] | Serve built static files |
| **Multi-stage builds** | Required for all services | Builder stage + runtime stage |

Multi-stage Python build pattern:
```dockerfile
FROM python:3.13-slim AS builder
RUN pip install uv
WORKDIR /app
COPY pyproject.toml uv.lock ./
RUN uv sync --frozen --no-dev

FROM python:3.13-slim AS runtime
COPY --from=builder /app/.venv /app/.venv
COPY . .
ENV PATH="/app/.venv/bin:$PATH"
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

### Docker Compose Services

```yaml
# docker-compose.yml service names (set as env var, never hardcode in source)
services:
  core-api:      # Port 8000
  bff:           # Port 3000
  shell:         # Port 5100 (nginx, serves built static files)
  domains-ui:    # Port 5101
  ingestion-ui:  # Port 5102
  search-ui:     # Port 5103
  admin-ui:      # Port 5104
  postgres:      # Port 5432
  mongo:         # Port 27017
  chroma:        # Port 8001
  redis:         # Port 6379
  kafka:         # Port 9092
  rabbitmq:      # Port 5672 (AMQP), 15672 (management UI)
  minio:         # Port 9000 (S3 API), 9001 (console) — local S3 substitute
```

### Kubernetes (Production Target)

| Item | Value | Notes |
|------|-------|-------|
| **Minimum version** | `1.29+` [verify before use] | |
| **Manifests** | Helm charts or plain YAML in `k8s/` directory | Helm recommended for environment parameterization |
| **Ingress** | `nginx-ingress` or cloud-native (AWS ALB, GCP GLB) [verify before use] | |
| **Secrets** | Kubernetes Secrets + external-secrets-operator [verify before use] | Or Vault integration |
| **Persistent volumes** | PVC for PostgreSQL, MongoDB data dirs | Do not use hostPath in production |
| **HPA** | Horizontal Pod Autoscaler on Core API and Ingestion Worker | Scale on CPU + queue depth |

### Nginx (Frontend Serving)

```nginx
# nginx.conf for Vue shell (SPA routing)
server {
  listen 80;
  root /usr/share/nginx/html;
  index index.html;

  location / {
    try_files $uri $uri/ /index.html;  # SPA fallback
  }

  location /assets/ {
    expires 1y;
    add_header Cache-Control "public, immutable";
  }
}
```

---

## 10. Observability

### Logging

| Component | Library | Format | Notes |
|-----------|---------|--------|-------|
| Core API (Python) | `structlog 24+` [verify before use] | JSON | Configure with `structlog.configure(processors=[...JSONRenderer()])` |
| Ingestion Worker | `structlog` | JSON | Same config as Core API |
| BFF (Node.js) | `pino 9+` [verify before use] | JSON | Fastify native; configure `level: "info"` in production |
| Frontend | Browser console only (MVP) | N/A | Structured logging from frontend is a v2 concern |

Every log entry must include:
- `service`: service name (`core-api`, `bff`, `ingestion-worker`)
- `trace_id`: forwarded from `X-Trace-Id` header
- `level`: `debug|info|warning|error`
- `timestamp`: ISO 8601

Trace ID propagation:
1. BFF generates `trace_id = uuid4()` on every incoming request if not already present
2. BFF forwards `X-Trace-Id: {trace_id}` to Core API
3. Core API attaches `trace_id` to all structlog context
4. Ingestion Worker receives `trace_id` in the job payload and includes in all log lines

### Metrics (Optional for MVP, Required for Production)

| Tool | Purpose | Notes |
|------|---------|-------|
| `prometheus-fastapi-instrumentator` [verify before use] | Expose `/metrics` in Core API | Auto-instruments FastAPI routes |
| `prom-client` (Node.js) [verify before use] | Expose `/metrics` in BFF | |
| Prometheus | Scrape metrics from services | |
| Grafana | Dashboards for metrics | |

### Health Endpoints (Required from Phase 1)

All services must expose:
```
GET /health/live   → 200 { "status": "ok" }                   (process alive)
GET /health/ready  → 200 { "status": "ok", "checks": {...} }  (dependencies connected)
```

Ready check must verify: PostgreSQL reachable, MongoDB reachable, Redis reachable, ChromaDB reachable.

---

## 11. Testing

### Python Testing Stack

| Package | Version | Purpose | Notes |
|---------|---------|---------|-------|
| `pytest` | `8.x` [verify before use] | Test runner | |
| `pytest-asyncio` | `0.23+` [verify before use] | Async test support | `asyncio_mode = "auto"` in `pytest.ini` |
| `pytest-cov` | `5.x` [verify before use] | Coverage reporting | |
| `httpx` | `0.27+` [verify before use] | TestClient for FastAPI (async) | `AsyncClient(app=app)` for async tests |
| `testcontainers` | `4.x` [verify before use] | Spin up real PostgreSQL/MongoDB/Redis in tests | Integration tests against real services |
| `factory-boy` | `3.x` [verify before use] | Test data factories for SQLAlchemy models | |
| `faker` | `25+` [verify before use] | Realistic fake data generation | |
| `respx` | `0.21+` [verify before use] | Mock HTTP calls (e.g., Gemini API) in tests | Works with httpx |

FastAPI test pattern:
```python
import pytest
from httpx import AsyncClient, ASGITransport
from app.main import app

@pytest.mark.asyncio
async def test_health():
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        response = await client.get("/health/live")
    assert response.status_code == 200
```

### Node.js / BFF Testing Stack

| Package | Version | Purpose | Notes |
|---------|---------|---------|-------|
| `vitest` | `2.x` [verify before use] | Test runner (fast, Vite-native) | Works for BFF unit tests too |
| `@fastify/inject` | Built into Fastify [verify before use] | HTTP injection testing without a real server | |
| `nock` | `13.x` [verify before use] | Mock HTTP calls to Core API | |
| `supertest` | `7.x` [verify before use] | HTTP integration testing (if using Express) | Less needed with Fastify inject |

### Frontend Testing Stack

| Package | Version | Purpose | Notes |
|---------|---------|---------|-------|
| `vitest` | `2.x` [verify before use] | Unit test runner | Same as BFF — consistent tooling |
| `@vue/test-utils` | `2.x` [verify before use] | Vue component mounting and testing | |
| `@testing-library/vue` | `8.x` [verify before use] | User-centric component testing | Preferred over raw test-utils for behavior tests |
| `jsdom` | `24+` [verify before use] | DOM simulation for vitest | |
| `msw` | `2.x` [verify before use] | Mock Service Worker for API mocking in tests | Works at the network level — no need to mock axios |
| `playwright` | `1.45+` [verify before use] | E2E browser testing | Test the full stack from browser perspective |

---

## 12. Version Compatibility Matrix

> All versions below are `[verify before use]` unless marked "confirmed". This matrix summarizes the critical cross-component version constraints.

| Layer | Package | Pinned/Min Version | Reason for Constraint |
|-------|---------|-------------------|----------------------|
| Python | `python` | `3.13+` | Project constraint (uv + fastapi) |
| Python | `fastapi` | `0.115+` | Requires pydantic v2 |
| Python | `pydantic` | `v2.x` | FastAPI 0.100+ hard requirement |
| Python | `fastmcp` | `0.4+` | ASGI mount API (check changelog) |
| Python | `chromadb` | `0.5+` | API changed significantly from 0.4 |
| Python | `sqlalchemy` | `2.x` | Async session API; v1 incompatible |
| Node.js | `node` | `20 LTS` | Minimum; 22 LTS recommended |
| Node.js | `openid-client` | `5.x` | v6 has breaking changes [verify] |
| Frontend | `vue` | `3.5.33` (confirmed installed) | Singleton in MF; version must match across ALL apps |
| Frontend | `pinia` | `^2.1.0` (confirmed package.json) | Singleton in MF; version must match across ALL apps |
| Frontend | `vite` | `5.4.21` (confirmed installed) | Required by `@originjs/vite-plugin-federation` 1.4.1 |
| Frontend | `@originjs/vite-plugin-federation` | `1.4.1` (confirmed installed) | Module Federation support for Vite 5 |
| Frontend | `typescript` | `^5.5.0` (confirmed package.json) | Same version everywhere (monorepo constraint) |
| Frontend | `@vue-flow/core` | `^1.42.0` (NEW, verify) | Ontology editor canvas; not singleton |
| Storage | `postgres` | `16` | Uses `gen_random_uuid()` (no extension); `tsvector` built-in; JSONB for ontology |
| Storage | `mongodb` | `7.x` | Motor 3.x compatibility |
| Storage | `redis` | `7.x` | ACL, streams (for potential pub/sub upgrade) |
| Infra | `docker compose` | `v2` | `docker compose` plugin syntax (not `docker-compose`) |

---

## 13. Package Manager Commands

### Python (uv)

```bash
# Create venv and install all deps
uv sync

# Add a production dependency
uv add fastapi

# Add a dev-only dependency
uv add --dev pytest pytest-asyncio

# Update all packages (respects version constraints)
uv lock --upgrade

# Run a script/command in the venv
uv run uvicorn app.main:app --reload

# Show installed packages
uv pip list
```

### Node.js / BFF (pnpm)

```bash
# Install all dependencies
pnpm install

# Add a dependency to the BFF app
pnpm --filter bff add fastify

# Add a dev dependency to the root
pnpm add -D -w typescript

# Run dev server
pnpm --filter bff dev

# Build all packages in dependency order
pnpm --filter '...' build
```

### Frontend Workspace (pnpm)

```bash
# Install all workspace packages
pnpm install

# Run shell dev server
pnpm --filter shell dev

# Run all micro UIs in parallel (requires concurrently or turbo)
pnpm --filter './apps/*' dev

# Build all apps
pnpm --filter './apps/*' build

# Add @vue-flow/core to domains-ui (ontology editor)
pnpm --filter domains-ui add @vue-flow/core @vue-flow/background @vue-flow/controls

# Add canvas-toolbox lib as local workspace dep to domains-ui
pnpm --filter domains-ui add @kmp/canvas-toolbox --workspace
```

---

## 14. Upgrade and Migration Notes

### ChromaDB 0.4 → 0.5

- Breaking changes in collection API and metadata filter syntax [verify before use]
- The `VectorStoreAdapter` pattern (see ARCHITECTURE.md) isolates this change to `adapters/vectorstore/chroma.py`
- Data migration: existing collections may need to be recreated and re-indexed
- Pin exact version in `pyproject.toml` until you verify upgrade is safe

### ChromaDB → Qdrant (v1 → v2)

1. Implement `QdrantVectorStoreAdapter(VectorStorePort)` in `adapters/vectorstore/qdrant.py`
2. Add `qdrant-client` to `pyproject.toml`
3. Run Qdrant in Docker Compose alongside ChromaDB (dual-write period optional)
4. Re-index all domains: replay each document through the embedding → Qdrant upsert pipeline
5. Switch `VECTOR_STORE=qdrant` environment variable
6. Verify search quality on a sample query set before switching traffic
7. Remove ChromaDB service and `chromadb` package

### PostgreSQL JSONB → Separate Ontology Tables (v2+)

If server-side node/edge filtering becomes necessary:
1. Add Alembic migration: create `ontology_nodes` and `ontology_edges` tables
2. Write a one-time data migration script to unpack `domains.ontology_data` JSONB into rows
3. Update `DomainService.get_ontology` and `update_ontology` to JOIN instead of column read
4. Remove `ontology_data` column after migration is validated

### PostgreSQL Ontology → Neo4J (roadmap target per PROJECT.md)

The JSONB representation is intentionally the same graph shape that Neo4J would ingest:
nodes (with id, label, properties) and edges (with source, target, label). When migrating:
1. Neo4J import can consume the JSONB data directly via `apoc.load.json`
2. The `OntologyGraph` Pydantic schema translates to Cypher `CREATE` statements 1:1
3. The API endpoints (`GET/PUT /v1/domains/:id/ontology`) do not change shape

### FastMCP Version Upgrades

FastMCP is an emerging library with rapid iteration [verify before use]:
- Check `CHANGELOG.md` on the FastMCP GitHub repo before upgrading
- The ASGI mount API (`mcp.as_asgi()`) is the most likely surface to change
- The MCP protocol itself (transport layer) may evolve — verify SSE transport is still recommended
- Pin exact version in `pyproject.toml`; upgrade deliberately with a test suite run

### Vue 3 Micro-Frontend Shared Dep Upgrades

When upgrading `vue`, `pinia`, or `vue-router` in the monorepo:
1. Update the version in ALL `package.json` files simultaneously (shell + all remotes + all shared packages)
2. Update `requiredVersion` in all Module Federation configs
3. Run `pnpm install` from workspace root
4. Build all apps and check for version conflict warnings in the browser console
5. Run E2E tests across all micro UIs before deploying

### Keycloak Version Upgrades

The existing Keycloak instance (`26+`) is not controlled by this project. When the ops team upgrades Keycloak:
- Re-validate JWKS endpoint URL and token claims format
- Check that `openid-client` (BFF) is compatible with the new Keycloak version
- Check that `python-jose` can still validate tokens (RS256 algorithm unlikely to change)
- Verify realm/client configuration is preserved after upgrade

---

*Last updated: 2026-05-03 — v1.1 additions: ontology editor canvas library, canvas toolbox structure, JSONB storage decision*
*Confirmed versions sourced directly from installed node_modules and package.json files in this repository.*
*Training-data estimates marked `[verify before use]` throughout.*

# Research Summary: Knowledge Management Platform

**Project:** Knowledge Management Center
**Domain:** Enterprise internal knowledge management with semantic search and AI agent integration
**Researched:** 2026-05-02
**Confidence:** MEDIUM-HIGH (training data cutoff August 2025; web verification unavailable)

---

## Executive Summary

This is a greenfield internal enterprise knowledge platform built around semantic search over multi-source document ingestion. Experts build this type of system as a layered pipeline: structured metadata in a relational store, raw content in a document store, vectors in a purpose-built vector database, and a thin adapter layer keeping all three in sync. The defining architectural risk is tight coupling. Teams that let ChromaDB or Gemini details leak into service logic end up with unmigrateable codebases. The VectorStorePort and EmbeddingPort abstractions must be defined in Phase 1, before a single ingestion worker is written.

The recommended stack is FastAPI (Python 3.13 + uv) for the Core API, Fastify (Node.js 22 LTS) for the BFF, Vue 3 + Module Federation for the micro-frontend, and PostgreSQL + MongoDB + ChromaDB for storage. Gemini text-embedding-004 is the default embedding provider. All are production-proven choices aligned to the project constraints. The single highest-risk technology decision is @originjs/vite-plugin-federation for micro-frontend Module Federation. It is the most mature option for Vue 3 + Vite but requires strict version pinning of Vue, Pinia, and Vue Router as singletons across all micro UIs; a version mismatch breaks reactivity silently.

The critical build path is: infrastructure scaffolding, Core API with auth and domain CRUD, ingestion pipeline, search, BFF + WebSocket, frontend shell, micro UIs, admin and API keys, FastMCP server, production hardening. Frontend development (BFF onward) can start in parallel with ingestion pipeline work if teams are split, using mock API data. The MCP server is deliberately last. It costs little to add once the Core API search endpoint is solid, and it is the primary AI-agent differentiator of this platform.

---

## Recommended Stack

The stack is fully constrained by PROJECT.md. No technology elections remain. Research confirms every constraint is sound and maps specific packages and version floors needed. Python 3.13 + uv is required; FastAPI 0.115+ with Pydantic v2 is non-negotiable. FastMCP mounts as an ASGI sub-app on the Core API (no separate process needed for MVP). On the Node.js side, Fastify 4.x is preferred over Express for performance, but the architecture is framework-agnostic.

**Core technologies:**

| Technology | Purpose | Confidence | Key Constraint |
|-----------|---------|------------|---------------|
| Python 3.13 + uv | Core API + ingestion worker | HIGH | Project constraint; uv.lock must be committed |
| FastAPI 0.115 + Pydantic v2 | HTTP framework | HIGH | Pydantic v2 is a hard dep of FastAPI 0.100+ |
| FastMCP 0.4+ | MCP server | MEDIUM | Pin exact version; breaking changes expected; ASGI mount API most likely to change |
| arq (not Celery) | Async task queue | MEDIUM | Simpler, asyncio-native; upgrade to Celery only if beat scheduling needed |
| Fastify 4.x + openid-client 5.x | BFF + OAuth2 | HIGH | HttpOnly session cookie; never expose JWT to browser |
| Vue 3.4 + Pinia 2.1 + vite-plugin-federation 1.3+ | Micro-frontend | HIGH | All three must be singleton:true across all MF apps; version mismatch breaks silently |
| PostgreSQL 16 | Relational metadata | HIGH | domains, documents, jobs, users, API keys |
| MongoDB 7 | Document content store | HIGH | Raw text + chunk content with flexible metadata |
| ChromaDB 0.5+ (HTTP mode) | Vector store MVP | MEDIUM | Verify 0.5 API shape before use; one collection per domain |
| Redis 7 | Session store + pub/sub relay | HIGH | BFF session + ingestion worker to BFF WebSocket notifications |
| Gemini text-embedding-004 | Default embeddings | LOW (limits) | 768 dims; store model + dim per domain in PostgreSQL; verify batch limits |
| Qdrant 1.9+ | Vector store v2 migration target | HIGH (pattern) | Adapter swap only; no service code changes |

**What to validate before pinning:** All versions are training-data estimates (cutoff August 2025). Run against live registries before locking. Priority items: Gemini batch limits, FastMCP ASGI mount API, @originjs/vite-plugin-federation 1.3+ config syntax, ChromaDB 0.5 collection API.

---

## v1 Feature Scope

### Must Have (Table Stakes)

- **Domain CRUD + access control** - admin creates/edits/deletes domains; users see only authorized domains
- **Document ingestion** - PDF (PyMuPDF), plain text, source code; chunking with overlap; deduplication by content hash; ingestion status tracking with per-document error reporting
- **Metadata extraction** - filename, source, domain, content type, timestamps, file size stored in PostgreSQL
- **Semantic (vector) search** - primary value-add over a file share
- **Hybrid search** - vector + BM25 keyword combined with Reciprocal Rank Fusion; pure vector search misses exact-match queries
- **Domain-scoped search with ACL** - users cannot receive results from unauthorized domains
- **Metadata/filter search + pagination** - filter by file type, date, source, domain
- **Search result snippets + relevance scores** - users need to see why a result ranked first
- **OAuth2/OIDC via Keycloak** - non-negotiable given project constraint (realm=Apps, client_id=kmplatform)
- **RBAC** - km-admin and km-reader roles minimum
- **API key issuance + scoping** - third-party access requires it; hash at rest, header-only transmission
- **Session management** - token refresh and logout handled by BFF transparently
- **Async REST endpoints** - document upload returns job_id; /v1/ versioned from day one
- **Health + readiness endpoints** - required for Docker Compose and Kubernetes
- **Docker Compose deployment** - full stack with single command
- **Structured JSON logging** - required to diagnose production issues

### Differentiators to Ship in v1

- **Multi-source ingestion connectors** - S3, Kafka, RabbitMQ alongside folder-watch and REST async; source-agnostic pipeline (all sources produce the same internal document event)
- **FastMCP server** - search_knowledge, list_domains, get_document, get_document_chunks tools; enables external AI agents to query the knowledge base as a tool call; very few KM platforms have native MCP support
- **LLM provider abstraction (EmbeddingPort)** - swap Gemini to OpenAI to local model without touching ingestion or search code
- **VectorStorePort abstraction** - ChromaDB v1, Qdrant v2; swap with one env var + re-index, no service code changes
- **Micro-frontend architecture** - shell + 4 independently deployable micro UIs (domains, ingestion, search, admin)
- **BFF in Node.js** - HttpOnly session cookies (no JWT in browser storage), WebSocket ingestion notifications (no polling)
- **WebSocket real-time ingestion status** - BFF pushes job progress/complete/failed events via Redis pub/sub relay

### Deferred to v2+

- Qdrant migration (abstraction built in v1; actual migration is ops work in v2)
- Neo4j document relationship graph (CITES, RELATED_TO, SUPERSEDES)
- Per-domain configurable embedding model
- Configurable re-ranking
- Local model embeddings (Ollama / sentence-transformers)
- Frontend structured logging / error tracking

**Explicitly out of scope:** collaborative editing, RAG answer/chat synthesis, real-time chat UI, native mobile app, billing/multi-tenancy, direct user auth outside Keycloak, document version control, email/calendar ingestion, user-generated tagging.

---

## Architecture & Build Order

### Component Map



### Critical Path

Nothing user-visible works until Levels 0-3 are complete.



### Phase Sequencing Recommendation

| Phase | Name | Rationale |
|-------|------|-----------|
| P1 | Infrastructure + Scaffolding | All subsequent phases depend on running stores and correct abstractions; retrofit is expensive |
| P2 | Core API + Auth | Cross-cutting auth contract must be settled before anything else builds on it |
| P3 | Ingestion Pipeline | Data production side; search returns nothing until documents are indexed |
| P4 | Search | Primary user value; blocked on P3 indexed data |
| P5 | BFF + WebSocket | Frontend blocked on BFF; WebSocket needs P3 Redis pub/sub live |
| P6 | Frontend Shell + Shared Packages | Module Federation singleton contract before any micro UI is scaffolded |
| P7 | Core Micro UIs (search, domains, ingestion) | Daily-use interfaces before admin features |
| P8 | Admin UI + API Keys | Lower-traffic admin features; API keys needed before MCP external access |
| P9 | FastMCP Server | Near-zero-cost add-on once P4 search and P8 API keys exist; last to avoid chasing evolving spec |
| P10 | Production Hardening | Kubernetes, observability, Qdrant migration, CI/CD |

### Research Flags

**Needs deeper research before or during phase:**
- **Phase 3 (Ingestion):** Gemini embedding API current batch size limits (LOW confidence) and text-embedding-004 dimension (768 - verify against current API docs)
- **Phase 6 (Frontend Shell):** @originjs/vite-plugin-federation v1.3+ exact plugin config API - verify against current docs before scaffolding; breaking changes between minor versions are possible
- **Phase 9 (FastMCP):** FastMCP ASGI mount API and SSE transport status - pin exact version in pyproject.toml; check CHANGELOG before implementation

**Standard patterns (skip research-phase):**
- **Phase 1:** Docker Compose, monorepo scaffolding, ABC patterns are fully established
- **Phase 2:** FastAPI + SQLAlchemy async + Keycloak JWKS validation is a well-documented pattern
- **Phase 4:** Vector search + BM25 RRF merge is standard RAG retrieval pattern
- **Phase 5:** Node.js OAuth2 proxy + HttpOnly cookies is OWASP-recommended and well-documented
- **Phase 7:** Vue 3 component development with established design system
- **Phase 8:** CRUD interface + API key management

---

## Top 5 Pitfalls to Prevent

| # | Pitfall | Prevention | Address In |
|---|---------|------------|------------|
| 1 | **VectorStorePort tight coupling** - ChromaDB constructs leak into service layer; migration becomes full rewrite | Define VectorStorePort ABC before any ingestion code; enforce via import-linter banning chromadb imports outside adapters/vectorstore/ | Phase 1 |
| 2 | **EmbeddingPort tight coupling** - Gemini task_type leaks into service code; provider swap requires code changes + corrupt index if dimension not stored | Define EmbeddingPort ABC with dimension property; store embedding_model + embedding_dimension per domain in PostgreSQL | Phase 1 |
| 3 | **Keycloak token propagation gap** - BFF validates JWT but Core API trusts BFF IP blindly; domain ACL bypassable; FastMCP has unconstrained internal access | BFF forwards Authorization: Bearer to every Core API call; Core API validates JWT independently via JWKS; Core API enforces domain ACL from token claims | Phase 2 |
| 4 | **Async ingestion poison pills** - malformed documents retry infinitely; consumer group rebalances; pipeline stalls for all documents | Every Kafka/RabbitMQ consumer: try/except + exponential backoff + max 5 retries + DLQ on exhaustion; idempotency key prevents double-processing | Phase 3 |
| 5 | **Module Federation version hell** - Vue/Pinia/Vue Router mismatch causes silent dual instances; Pinia stores invisible across micro UI boundaries | Shell: singleton:true, eager:true for Vue/Pinia/vue-router; all remotes: singleton:true; matching requiredVersion; CI check fails on diverged shared dep versions | Phase 6 |

Additional significant pitfalls (see PITFALLS.md for full matrix):
- **MongoDB + PostgreSQL dual-write inconsistency** (Phase 3): use outbox pattern; never fire-and-forget dual writes
- **Hardcoded Docker service names** (Phase 1): all service URLs from env vars; no hostnames in source code
- **API keys stored/transmitted insecurely** (Phase 2): SHA-256 hash at rest, X-API-Key header only, never query params
- **FastMCP context window exhaustion** (Phase 9): return chunk references + snippets, not full text; long operations return job_id immediately

---

## Frontend Design System (DESIGN.md)

Design system name: **"Luminous Knowledge"**. Source of truth for all visual decisions. No deviations without modifying DESIGN.md first. All micro UIs must adhere.

**Brand:** Minimalism + Glassmorphism, Apple-inspired. Emotional target: "focused sophistication." Content is the focal point; the UI is invisible.

**Color tokens for Tailwind config:**

| Token | Hex | Usage |
|-------|-----|-------|
| primary | #0058BC / action blue #007AFF | Primary buttons, active states, focus rings. Use sparingly. |
| background / surface | #F9F9FF | Page background |
| surface-container-lowest | #FFFFFF | Cards, elevated content |
| on-surface | #181C23 | Body text, headings |
| on-surface-variant | #414755 | Secondary text, metadata, icons |
| outline-variant | #C1C6D7 | Card borders, dividers (1px) |
| error | #BA1A1A | Error states |

**Typography (Inter, single typeface):**

| Scale | Size | Weight | Letter Spacing | Notes |
|-------|------|--------|---------------|-------|
| display-lg | 48px | 700 | -0.02em | Page titles |
| headline-md | 24px | 600 | -0.01em | Section headers |
| body-base | 17px | 400 | -0.01em | Primary reading. Apple signature size. |
| body-sm | 14px | 400 | 0 | Metadata, breadcrumbs, captions |
| label-caps | 12px | 600 | +0.05em | Chips, tags, labels |

Configure fontFamily.sans = Inter in Tailwind. Import via @fontsource/inter or Google Fonts.

**Spacing:** 8px base unit. Desktop margins 40px. Max content width 1200px. Card padding 24-32px. Section separation 48-64px.

**Glassmorphism rules:**
- Headers + sidebars: backdrop-filter: saturate(180%) blur(20px) with background: rgba(255,255,255,0.7)
- Glass sidebar: backdrop-filter: blur(30px); nav items full-width hover, 8px border-radius
- Cards: white, 1px #E5E5E7 border, diffuse glow shadow (0px Y-offset)
- Floating modals: 4px Y-offset shadow for higher elevation feel

**Shape language:**
- Buttons + inputs: 10px border-radius
- Cards + containers: 12-16px border-radius
- Hover states (list/nav): 6-8px border-radius
- Chips/pills: border-radius: 9999px

**Component patterns:**
- Primary button: Solid #007AFF, white text, 10% white-to-transparent vertical gradient (gloss)
- Secondary button: Light gray background, blue text, no border
- Input field: #F2F2F7 background transitions to white with blue glow/border on focus
- Card: White, 1px #E5E5E7 border, diffuse shadow, 24-32px padding
- Chip/tag: Pill-shaped, light gray fill, #424245 text, no border
- Segmented control: Soft gray track, white elevated thumb for active state
- Breadcrumbs: Minimalist text links, chevron separator, body-sm scale

**Tailwind implementation checklist:**
- Override primary color with #0058BC (default) / #007AFF (action)
- Set background to #F9F9FF
- Configure fontFamily.sans with Inter
- Register all design tokens as Tailwind theme extensions
- Use @headlessui/vue for dialogs, dropdowns, segmented controls
- Use lucide-vue-next for icons
- Verify Tailwind v3.4+ vs v4 stability before scaffolding Phase 6

---

## Open Questions

The roadmap must resolve or explicitly defer these:

1. **Keycloak client readiness:** Is kmplatform already configured as confidential in realm=Apps with correct redirect URIs and roles (km-admin, km-reader)? Blocks Phase 2. Needs ops team confirmation.

2. **Deployment hostnames:** What are the actual domain names for BFF, shell, and API in staging/production? bff.kmp.local and shell.kmp.local are placeholders needed before Keycloak redirect URIs, CORS config, and nginx configs can be finalized.

3. **Kafka vs RabbitMQ vs both:** Support both simultaneously for different customer environments, or one primary + one secondary? Affects ingestion worker architecture and testing scope.

4. **Ingestion worker process isolation:** Co-located with Core API (simpler MVP) or separate container from day one? Affects Phase 1 Docker Compose design and arq vs Celery decision.

5. **Gemini API billing tier:** Actual batch size limits and rate limits depend on billing tier. LOW confidence in training-data estimates. Affects Phase 3 chunking batch configuration.

6. **ChromaDB version in production:** Fresh installation or existing data from 0.4? If existing, migration plan needed before Phase 3.

7. **Frontend micro UI deployment origin:** All remotes from same CDN origin (path-based) or separate origins? Affects CORS config and remoteEntry.js URL resolution strategy.

8. **Tailwind v3 vs v4:** Tailwind v4 was in alpha as of Aug 2025. Pin 3.4+ for stability, or evaluate v4? Affects all tailwind.config.ts token mapping in Phase 6.

9. **FastMCP transport:** SSE was most compatible as of 2025 but MCP spec was actively evolving. Verify current recommended transport (SSE vs Streamable HTTP) against current FastMCP docs before Phase 9.

10. **Scale target:** No concurrent user target defined. Acceptable for MVP but needed for Phase 10 HPA sizing and ChromaDB to Qdrant migration trigger threshold.

---

## Confidence Assessment

| Area | Confidence | Notes |
|------|------------|-------|
| Stack | MEDIUM | Package names and patterns correct; all version numbers are training-data estimates needing live verification before pinning |
| Features | MEDIUM-HIGH | Table stakes from established KM platforms; differentiators from direct PROJECT.md constraints; anti-features from explicit Out of Scope; no competitor matrix consulted |
| Architecture | HIGH | All major patterns are well-documented production patterns; FastMCP surface is MEDIUM (emerging, rapid iteration) |
| Pitfalls | HIGH / MEDIUM | Vector/LLM abstraction leakage, token propagation, DLQ, MF version hell are documented production failure modes; FastMCP constraints inferred from MCP spec |

**Overall confidence:** MEDIUM-HIGH

### Gaps to Address During Implementation

- **Gemini embedding API limits** (Phase 3): batch size, rate limits, model name. Verify against Google AI Studio docs.
- **FastMCP ASGI mount API** (Phase 9): pin exact version immediately; check CHANGELOG before implementation.
- **@originjs/vite-plugin-federation vs @module-federation/vite** (Phase 6): evaluate current maturity before scaffolding.
- **ChromaDB 0.5 collection API** (Phase 3): verify breaking changes from 0.4 before implementing adapter.
- **uv workspace multi-project lockfile behavior** (Phase 1): verify current docs before relying on it for cross-service dep consistency.

---

## Sources

All research is based on training data (knowledge cutoff August 2025). Web verification was unavailable.

### Primary (HIGH confidence)
- FastAPI / Pydantic v2 / SQLAlchemy async documentation - patterns verified against known production deployments
- OWASP OAuth2 session management guidelines - BFF HttpOnly cookie pattern
- Keycloak OIDC documentation - Authorization Code flow, JWKS endpoint, client credentials grant
- Webpack Module Federation docs - singleton pattern, requiredVersion, eager loading contract
- Kafka and RabbitMQ official documentation - DLQ, consumer group configuration, idempotency
- PostgreSQL 16 documentation - gen_random_uuid(), tsvector/tsquery, index strategies

### Secondary (MEDIUM confidence)
- FastMCP GitHub (training data, Aug 2025) - ASGI mount pattern, SSE transport
- @originjs/vite-plugin-federation documentation - Vue 3 + Vite Module Federation
- ChromaDB 0.5 documentation - HTTP client mode, collection-per-domain pattern
- Qdrant 1.9 documentation - collection model, payload filtering

### Tertiary (LOW confidence, verify before use)
- Gemini embedding API - batch size limits, task_type parameters, dimension for text-embedding-004
- @module-federation/vite adoption level post-Aug 2025
- uv workspace multi-project support - relatively new feature

---

*Research completed: 2026-05-02*
*Ready for roadmap: yes*

# Features Research: Knowledge Management Platform

**Domain:** Internal enterprise knowledge management with semantic search and AI agent integration
**Researched:** 2026-05-02
**Confidence:** MEDIUM (training data + full project context; WebSearch unavailable)

---

## Table Stakes (Must Have)

These are features users and integrators expect from any serious KM platform. Missing any of these causes abandonment or rejection during evaluation.

### Domain Management

- **Domain CRUD (admin)** — Admins create, name, describe, and delete knowledge domains. Domains are the top-level organizational primitive; without them the platform has no structure. | Complexity: Low | v1
- **Domain access control** — Assign which users/roles can read which domains. A domain is useless if everyone sees everything or nothing. Depends on: Auth/AuthZ. | Complexity: Medium | v1
- **Domain listing and browsing** — Users see the list of domains they can access, with document counts and last-updated timestamps. Basic discoverability. | Complexity: Low | v1

### Document Ingestion and Processing

- **PDF ingestion** — Extract text from PDFs including multi-page, mixed layout. De-facto standard enterprise document format. | Complexity: Medium | v1
- **Plain text ingestion** — Ingest `.txt`, `.md`, and similar files. Lowest-friction format; expected. | Complexity: Low | v1
- **Source code ingestion** — Ingest code files preserving structure (language detection, file-level chunking). Needed for developer-facing knowledge bases. | Complexity: Medium | v1
- **Folder-watch / local folder source** — Monitor a local directory and auto-ingest new/changed files. Simplest source for initial setup and demos. | Complexity: Medium | v1
- **Chunking and preprocessing pipeline** — Split documents into semantically coherent chunks before embedding. Quality here directly determines search quality. | Complexity: Medium | v1
- **Embedding generation** — Convert chunks to vector representations. Core of semantic search; without it you only have keyword search. Depends on: LLM embedding provider. | Complexity: Medium | v1
- **Ingestion status tracking** — Per-document status (queued, processing, indexed, failed) stored and queryable. Users need to know if their upload worked. | Complexity: Low | v1
- **Ingestion error reporting** — Surface failures with enough detail to diagnose (parse error, unsupported encoding, embedding API failure). Without this, failed docs silently disappear. | Complexity: Low | v1
- **Document deduplication** — Detect re-ingested identical content (by hash) and skip or update rather than creating duplicates. Required for S3/folder sources that re-scan. | Complexity: Medium | v1
- **Metadata extraction and storage** — Capture filename, source, domain, content type, ingestion timestamp, file size. Needed for filtering and audit. | Complexity: Low | v1

### Search

- **Semantic (vector) search** — Find documents by meaning, not just keywords. This is the primary value-add over a simple file share. | Complexity: Medium | v1
- **Hybrid search** — Combine vector similarity with keyword (BM25) scoring for better recall. Pure vector search misses exact-match queries (IDs, names, codes). | Complexity: Medium | v1
- **Domain-scoped search** — Search within one domain or across multiple authorized domains. Users must not get results from domains they cannot access. | Complexity: Low | v1
- **Metadata/filter search** — Filter results by file type, date range, source, domain. Required for power users working with large corpora. | Complexity: Low | v1
- **Search result ranking and relevance scores** — Return results with a relevance score, not just a list. Users need to trust and understand why a result ranked first. | Complexity: Low | v1
- **Snippet/excerpt in results** — Show the relevant text passage around the match, not just a filename. Critical for deciding which result to open. | Complexity: Low | v1
- **Pagination** — Handle large result sets without returning thousands of chunks at once. | Complexity: Low | v1

### Authentication and Authorization

- **OAuth2/OIDC login via Keycloak** — Web users authenticate through the existing Keycloak instance. Non-negotiable given the project constraint and enterprise context. | Complexity: Medium | v1
- **Role-based access control (RBAC)** — At minimum: admin and reader roles. Admins manage domains/sources; readers search. | Complexity: Medium | v1
- **API Key issuance and management** — Create, revoke, and list API Keys for third-party callers. Without this, third parties cannot access the platform. | Complexity: Medium | v1
- **API Key scoping** — Keys scoped to specific domains or read-only operations. A key that accesses everything is a security liability. | Complexity: Medium | v1
- **Session management** — Token refresh, logout, and session expiry handled correctly. Standard OIDC requirement. | Complexity: Medium | v1

### Core API

- **Document upload endpoint (REST async)** — Accept document uploads, return a job ID, process asynchronously. Synchronous processing blocks and times out for large files. | Complexity: Medium | v1
- **Job status polling endpoint** — Query ingestion job status by job ID. Needed because ingestion is async. | Complexity: Low | v1
- **Search endpoint** — Accept query + filters + domain, return ranked results. The primary read path. | Complexity: Low | v1
- **Domain management endpoints** — CRUD for domains over REST. Needed by admin UI and any programmatic domain setup. | Complexity: Low | v1
- **Health / readiness endpoints** — `/health` and `/ready` for load balancers and orchestration. Required for Docker Compose and Kubernetes deployments. | Complexity: Low | v1
- **Structured error responses** — Consistent JSON error format (code, message, detail). Without this, clients cannot handle errors reliably. | Complexity: Low | v1
- **API versioning** — Version prefix (`/v1/`) from day one. Retrofitting versioning is painful. | Complexity: Low | v1

### Frontend (Web UI)

- **Login / auth flow** — Redirect to Keycloak, handle callback, store token, redirect to app. Required to enter the platform. | Complexity: Medium | v1
- **Domain browser** — List accessible domains with counts and metadata. Entry point for all users. | Complexity: Low | v1
- **Search interface** — Input field, filters panel, results list with snippets. Primary daily-use interface. | Complexity: Medium | v1
- **Document detail view** — View extracted text, metadata, and source information for a single document. | Complexity: Low | v1
- **Admin panel — domain management** — UI for creating/editing/deleting domains, assigning access. | Complexity: Medium | v1
- **Admin panel — ingestion sources** — UI for configuring and monitoring ingestion sources. | Complexity: Medium | v1
- **Ingestion status dashboard** — Real-time view of ingestion jobs via WebSocket notifications. | Complexity: Medium | v1

### Infrastructure and Operations

- **Docker Compose deployment** — Full stack runnable locally and in staging with a single command. | Complexity: Medium | v1
- **Environment configuration** — All secrets and configuration via environment variables (12-factor). | Complexity: Low | v1
- **Logging** — Structured logs (JSON) for all services. Required to diagnose production issues. | Complexity: Low | v1

---

## Differentiators

These features distinguish this platform from generic document stores or basic search indexes. They are what makes this platform valuable for AI-driven, multi-source enterprise knowledge management.

### Multi-Source Ingestion Pipeline

- **S3 source connector** — Poll or event-trigger ingestion from S3 buckets. Covers organizations storing documents in object storage. | Complexity: High | v1
- **Kafka consumer connector** — Consume document events from Kafka topics (event-driven ingestion). Rare in KM platforms; enables real-time knowledge updates in event-driven architectures. | Complexity: High | v1
- **RabbitMQ consumer connector** — Same pattern for AMQP-based message queues. Organizations using RabbitMQ get first-class support. | Complexity: High | v1
- **Source-agnostic ingestion pipeline** — Uniform processing regardless of source (folder, S3, Kafka, REST). Each source produces the same internal document event; the pipeline normalizes everything. | Complexity: High | v1
- **Source configuration and management API** — CRUD for source definitions (which S3 bucket, which Kafka topic, credentials). | Complexity: Medium | v1

### MCP Server for AI Agent Integration

- **FastMCP server exposing knowledge base** — External AI agents (Claude, GPT, etc.) query knowledge as a tool call using the Model Context Protocol. This is a genuine differentiator: very few KM platforms have native MCP support. | Complexity: High | v1
- **MCP tool: `search_knowledge`** — Core tool; agents call with a query and receive ranked, sourced results. | Complexity: Medium | v1
- **MCP tool: `list_domains`** — Agents discover what domains exist before querying. | Complexity: Low | v1
- **MCP tool: `get_document`** — Agents retrieve full document content by ID for deeper analysis. | Complexity: Low | v1
- **MCP authentication** — MCP clients authenticate with API Keys (same mechanism as third-party REST). API Key scoping carries over. | Complexity: Medium | v1

### Multi-LLM Embedding Architecture

- **LLM provider abstraction layer** — Swap embedding providers (Gemini → OpenAI → local model) without changing the ingestion or search pipeline. Protects against provider lock-in and cost increases. | Complexity: Medium | v1
- **Gemini embeddings (default)** — Production-quality multilingual embeddings with generous free tier. | Complexity: Low | v1
- **Configurable embedding model per domain** — Different domains can use different models (e.g., a code domain uses a code-specialized model). | Complexity: Medium | v2

### Vector Store Portability

- **ChromaDB for MVP** — Zero-ops setup for development and initial deployment. | Complexity: Low | v1
- **Qdrant migration path** — Swap ChromaDB for Qdrant without rewriting search/ingest logic (abstraction layer). Qdrant handles production scale, filtering, and multi-tenant isolation better. | Complexity: Medium | v2
- **Vector store abstraction interface** — Single interface that both ChromaDB and Qdrant implement; the service layer never talks directly to a specific vector store. | Complexity: Medium | v1

### Micro-Frontend Architecture

- **Shell / host application** — Central shell loads and composes micro UIs via Module Federation. Independent deployability of each UI section is the key benefit. | Complexity: High | v1
- **Search micro UI** — Standalone, independently deployable search interface. | Complexity: Medium | v1
- **Admin micro UI** — Standalone admin panel (domain management, source config, user roles). | Complexity: Medium | v1
- **WebSocket-based real-time notifications** — Ingestion status, indexing progress pushed to UI via BFF WebSocket. No polling. | Complexity: Medium | v1

### BFF (Backend for Frontend) Layer

- **BFF in Node.js** — Decouples frontend concerns from Core API; handles session cookies, WebSocket, and response shaping. Enables frontend to evolve without touching Core API contracts. | Complexity: Medium | v1
- **REST → Core API proxying with auth enrichment** — BFF adds user identity (from Keycloak token) to downstream calls so Core API trusts a single internal identity header. | Complexity: Medium | v1

### Knowledge Graph Relations (Post-MVP)

- **Document relationship graph (Neo4j)** — Model "cites", "relates to", "supersedes" relationships between documents. Enables graph-based navigation that vector search alone cannot provide. | Complexity: High | v2
- **Automatic relationship extraction** — Detect citations, shared concepts, and cross-references during ingestion. | Complexity: High | v2

---

## Anti-Features (Deliberately Exclude)

These are features that appear attractive but would harm the platform by adding complexity, scope creep, or contradicting the platform's identity.

- **Collaborative document editing** — This platform reads and indexes documents; it does not author them. Adding an editor (like Notion or Confluence) would require a completely different data model, conflict resolution, and permissions philosophy. The platform's value is in *finding* knowledge, not *creating* it.
- **LLM-generated content / RAG answer synthesis** — Generating answers from retrieved chunks (RAG chat) would require prompt engineering, answer validation, hallucination handling, and rate-limit management per LLM provider. It also blurs the line between "what the document says" and "what the AI inferred." Exclude from scope; the MCP server lets AI agents do this themselves.
- **Real-time chat / conversational interface** — The WebSocket connection is for ingestion notifications, not chat. A chat UI would imply stateful conversation management, session history, and streaming responses — a separate product. The MCP server covers the conversational AI use case.
- **Billing and multi-tenancy isolation** — This is an internal platform. Introducing billing tiers, tenant billing separation, or commercial SaaS multi-tenancy adds an entire product dimension with no value to the stated use case.
- **Native mobile app** — Web-first with responsive design is sufficient. A native mobile app requires separate development, a mobile auth flow, platform-specific push notifications, and app store maintenance.
- **End-user direct authentication (outside Keycloak)** — Username/password or social login managed by this platform itself would duplicate what Keycloak already provides and create a second identity system to secure and maintain.
- **Document version control / history** — Tracking every version of an ingested document (diff, rollback) is a document management system feature, not a KM search feature. Re-ingestion overwrites or appends; version history belongs in the source system (Git, S3 versioning, etc.).
- **Full document editor / rich text UI** — Not a Google Docs replacement. Users upload documents from their existing tools.
- **Email / calendar integration** — Ingesting email threads or calendar events is a different domain entirely and introduces serious privacy and consent concerns in an enterprise context.
- **User-generated tagging / annotation** — Crowdsourced tagging sounds useful but degrades without moderation, creates inconsistent taxonomy, and competes with the admin-controlled domain structure.

---

## Feature Dependencies

Key chains where a feature cannot ship without another being ready first.

```
Keycloak OAuth2/OIDC login
  └─ RBAC (roles come from Keycloak claims)
      └─ Domain access control (roles map to domain permissions)
          └─ Domain-scoped search (search enforces domain ACL)
              └─ MCP tool: search_knowledge (inherits domain ACL via API Key scoping)

Domain CRUD
  └─ Document ingestion (documents must be assigned to a domain)
      └─ Chunking and preprocessing
          └─ Embedding generation (LLM provider abstraction)
              └─ Vector store write (ChromaDB → Qdrant)
                  └─ Semantic search
                      └─ Hybrid search (adds BM25 layer on top)
                          └─ Snippet/excerpt in results

REST async upload endpoint
  └─ Ingestion job tracking (returns job ID)
      └─ Job status polling
          └─ WebSocket ingestion notifications (BFF pushes status events)
              └─ Ingestion status dashboard (UI consumes WebSocket)

API Key issuance
  └─ API Key scoping (keys reference domains)
      └─ Third-party REST access
          └─ MCP server authentication (MCP clients use API Keys)
              └─ MCP tools (search, list_domains, get_document)

Shell / host app (Module Federation)
  └─ Search micro UI (registered remote in shell)
  └─ Admin micro UI (registered remote in shell)

BFF (Node.js)
  └─ REST → Core API proxying
  └─ WebSocket bridge (Keycloak session → WebSocket auth)

Vector store abstraction interface
  └─ ChromaDB adapter (v1)
  └─ Qdrant adapter (v2, swap without service changes)

LLM provider abstraction layer
  └─ Gemini adapter (default)
  └─ Future: OpenAI, local model adapters
```

---

## MVP vs v2 Summary

| Scope | Feature Count | Key Capabilities |
|-------|--------------|-----------------|
| v1 (MVP) | ~45 features | All table stakes + S3/Kafka/RabbitMQ sources + MCP server + micro-frontend shell + ChromaDB + Gemini |
| v2 | ~5 features | Qdrant migration, Neo4j knowledge graph, per-domain embedding model, configurable reranking |

The v1 scope is large but coherent: every feature serves the core value ("find knowledge in seconds"). The v1 MCP server is explicitly v1 because it's a primary differentiator and can be built with low overhead once the Core API search endpoint exists.

---

## Confidence Notes

- Table stakes derived from: training knowledge of Confluence, Notion, Elasticsearch-based platforms, SharePoint, and enterprise search products. Confidence: MEDIUM-HIGH.
- Differentiators derived from: project constraints in PROJECT.md + knowledge of MCP specification (2024-2025 standard), FastMCP library patterns, micro-frontend with Module Federation, ChromaDB/Qdrant operational characteristics. Confidence: MEDIUM.
- Anti-features derived from: project Out of Scope section + known failure modes in enterprise KM products. Confidence: HIGH (directly from project definition).
- WebSearch was unavailable; no real-time competitor feature matrix was consulted. Findings should be cross-referenced against current Guru, Tettra, Bloomfire, or Elastic Enterprise Search feature lists before final roadmap commitment.

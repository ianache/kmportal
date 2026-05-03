# Pitfalls Research: Knowledge Management Platform

**Domain:** Multi-service Knowledge Management (Python FastAPI + NodeJS BFF + Vue micro-frontend)
**Researched:** 2026-05-02
**Overall Confidence:** HIGH for distributed systems / async patterns; MEDIUM for FastMCP specifics (emerging tech)

---

## Critical Pitfalls (Project-killers)

### 1. Vector Store Tight Coupling — ChromaDB Bleeds Into Business Logic

- **What goes wrong:** Developers use ChromaDB-specific constructs (collection.query(), metadata filter syntax, distance metric names, embedding function objects passed directly to the collection) throughout the Core API. When Qdrant migration begins, every repository method, search service, and ingestion worker needs rewriting. The migration becomes a partial rewrite of the entire search layer.
- **Warning signs:** Any file outside a `vectorstore/` or `repositories/vector/` package imports `chromadb` directly. Search filters use ChromaDB's `where` dict syntax in service-layer code. Embedding dimension or distance metric is hardcoded in ingestion workers rather than retrieved from a config/enum.
- **Prevention:** Define a `VectorStorePort` abstract class (Python ABC) with exactly the methods the rest of the system needs: `upsert(id, vector, metadata)`, `query(vector, top_k, filters)`, `delete(id)`, `collection_exists()`. ChromaDB adapter implements it; Qdrant adapter implements it. Nothing outside the `adapters/vectorstore/` package ever imports `chromadb` or `qdrant_client`. Enforce with an `import-linter` or `ruff` rule banning direct chromadb imports outside the adapter module.
- **Address in:** Phase 1 (Core API skeleton) — the port must exist before the first ingestion worker is written.

---

### 2. Micro-Frontend Auth Token Chaos — Each Micro-UI Manages Its Own Token Lifecycle

- **What goes wrong:** Each micro UI (deployed independently) tries to handle Keycloak token refresh on its own. Race conditions cause simultaneous refresh calls. Token stored in `localStorage` by one micro UI becomes stale while another is still holding the old value in memory. After a 401, micro UI A refreshes the token, but micro UI B is still sending requests with the old access token. The user sees intermittent auth failures that are impossible to reproduce.
- **Warning signs:** More than one micro UI calls `keycloak.updateToken()` or listens to `keycloak.onTokenExpired`. Token is stored as a plain string in `localStorage` without a mutex/lock. BFF WebSocket connection drops silently after token expiry with no reconnect logic.
- **Prevention:** The shell (host app) owns the Keycloak instance — one instance, one token refresh loop. Micro UIs receive tokens via a shared auth bus (a custom event or a shared Pinia store exposed through Module Federation). The shell exposes `getToken(): Promise<string>` — micro UIs call that function and never hold a token reference longer than a single HTTP call. BFF validates tokens on every WebSocket message (not just on connect). Use `keycloak-js` only in the shell; micro UIs get a lightweight auth interface injected at runtime.
- **Address in:** Phase 2 (Auth infrastructure) and Phase 3 (Micro-frontend shell).

---

### 3. Async Ingestion Poison Pills — Malformed Documents Halt the Pipeline Indefinitely

- **What goes wrong:** A PDF with corrupt structure, a code file with null bytes, or a document whose embedding call returns a 429 gets retried infinitely. The message never gets acknowledged, the consumer crashes or loops, and the queue backs up. Kafka's default retry behavior (`max.poll.interval.ms` exceeded) causes consumer group rebalances. The entire ingestion pipeline stalls for all documents behind the bad one.
- **Warning signs:** Dead letter queue (DLQ) is absent or unconfigured. Retry logic uses a simple `while True` loop without exponential backoff. No maximum retry count. Error metrics show the same document ID in error logs repeatedly. Consumer lag grows without consumer crashes.
- **Prevention:** Every Kafka consumer and RabbitMQ handler must implement: (1) try/except catching all exceptions, (2) exponential backoff with jitter (start 1s, max 60s), (3) max retry count (e.g., 5 attempts), (4) on exhaustion: publish to DLQ with full error context and `ack` the original message. RabbitMQ: set `x-dead-letter-exchange`. Kafka: use a separate `*.DLQ` topic. Document all failure reasons as structured log events. Idempotency key (document hash or UUID) prevents double-processing on retry.
- **Address in:** Phase 2 (Ingestion pipeline foundation).

---

### 4. Keycloak Token Propagation Gap — BFF Validates but Core API Trusts Blindly

- **What goes wrong:** The BFF validates the Keycloak JWT on entry and proxies requests to the Core API without forwarding the token. The Core API trusts any request from the BFF's internal IP. This means: (1) the Core API has no identity context (can't enforce domain-level authorization), (2) if the BFF is compromised or misconfigured, the Core API is fully open internally, (3) the FastMCP server calling the Core API also bypasses Keycloak, giving AI agents unconstrained access.
- **Warning signs:** Core API routes have no `Authorization` header dependency. Core API has no concept of `current_user` or `current_realm_roles`. Domain permission checks live only in the BFF. FastMCP tools call Core API with a static service account token that never expires.
- **Prevention:** BFF forwards the original `Authorization: Bearer <token>` header to every Core API call — do not re-sign or replace it. Core API validates the JWT independently using Keycloak's JWKS endpoint (cache the public key, re-fetch on `kid` miss). Core API enforces domain-level access (user can only query domains they're assigned to) based on token claims. FastMCP server uses a short-lived service account token from Keycloak (client credentials flow) with minimal scopes, rotated on startup. Internal-only network isolation does not replace token validation.
- **Address in:** Phase 2 (Auth infrastructure). Every subsequent phase must respect this contract.

---

### 5. LLM Provider Lock-In Through Gemini API Shape Leakage

- **What goes wrong:** The embedding service calls `genai.embed_content(model=..., content=..., task_type=...)` directly in ingestion workers and search handlers. Gemini-specific parameters (`task_type="RETRIEVAL_DOCUMENT"`, `task_type="RETRIEVAL_QUERY"`) get embedded in business logic. When switching to OpenAI or a local model (Ollama), the call sites must be rewritten because the abstraction leaks Gemini's vocabulary. Worse: different providers return different embedding dimensions (Gemini text-embedding-004 = 768, OpenAI text-embedding-3-small = 1536). If dimensions are not captured in the vector store metadata, a provider switch corrupts the existing index.
- **Warning signs:** `import google.generativeai` appears outside an `embeddings/providers/` package. Code references `task_type` or `output_dimensionality` (Gemini params) in service-layer code. Vector collection is created without storing the embedding model name and dimension as collection metadata.
- **Prevention:** Define an `EmbeddingPort` abstract class: `embed_documents(texts: list[str]) -> list[list[float]]` and `embed_query(text: str) -> list[float]`. Gemini adapter handles task_type internally. OpenAI adapter handles its own parameters. The port exposes `dimension: int` as a property so the vector store adapter can create collections with the right size. Store `embedding_model` and `embedding_dimension` in PostgreSQL per domain — migration to a new provider requires a re-index of that domain, not a code change. Never mix embedding providers within a single domain collection.
- **Address in:** Phase 1 (Core API skeleton).

---

## Significant Pitfalls (Costly if ignored)

### 6. Docker Compose Hardcoded Service Discovery Breaking Kubernetes Migration

- **What goes wrong:** Services reference each other by Docker Compose service names hardcoded in config files or — worse — in source code (e.g., `http://chroma:8000`, `mongodb://mongo:27017`). When moving to Kubernetes, service names are in a different DNS namespace, and hostnames like `chroma` don't resolve. Environment variables exist but contain Docker Compose names as defaults in code. Volume mounts use host paths (`./data:/data`) that map to nothing in a Kubernetes PersistentVolumeClaim.
- **Warning signs:** Any `http://servicename:port` appears as a Python/JS string literal outside a config/env file. `docker-compose.yml` volumes use relative host paths for persistent data. Service URLs are constructed with f-strings using hardcoded hostnames.
- **Prevention:** Every service address is configured via environment variable with no default value in code (fail fast if unset). Use a `config.py` / `config.ts` that reads from env and validates on startup. Docker Compose sets those env vars to its service names; Kubernetes ConfigMaps/Secrets set them to cluster-internal DNS names. Volume strategy: use named volumes in Docker Compose from day one (not host-bind mounts for persistent data). Never reference sibling service names in application source code.
- **Address in:** Phase 1 (project scaffolding). Retrofit is painful.

---

### 7. MongoDB + PostgreSQL Dual-Write Inconsistency — Documents Without Metadata or Metadata Without Content

- **What goes wrong:** Ingestion writes raw content to MongoDB, then writes metadata to PostgreSQL in a non-atomic sequence. If the MongoDB write succeeds but the PostgreSQL write fails (network hiccup, constraint violation), the document exists in MongoDB but is invisible to search (no metadata = no domain assignment = never indexed). The reverse — metadata in PostgreSQL but content missing in MongoDB — causes 500 errors on document retrieval. Over time, ghost records accumulate. No cleanup process exists.
- **Warning signs:** Ingestion service has two separate `await` calls for MongoDB and PostgreSQL with only a try/except around each independently. No reconciliation job. No transactional outbox pattern. Document count in PostgreSQL and MongoDB diverge over days.
- **Prevention:** Use the outbox pattern: write to PostgreSQL first (metadata + status=PENDING in a single transaction), then an async worker reads PENDING rows and writes to MongoDB, marking the row COMPLETE atomically. If MongoDB write fails, the row stays PENDING and retries. Alternatively: treat PostgreSQL as the system of record; MongoDB is populated from a Kafka event fired after the PostgreSQL commit (event sourcing lite). Add a nightly reconciliation job that queries both stores and alerts on orphaned records. Never do fire-and-forget dual writes.
- **Address in:** Phase 2 (Ingestion pipeline).

---

### 8. Module Federation Version Hell — Shared Dependencies Clash at Runtime

- **What goes wrong:** Shell app exposes Vue 3.4.x and Pinia 2.1.x as shared singletons. A micro UI was built against Vue 3.3.x and has it bundled separately (eager: true accidentally set). At runtime, two Vue instances exist simultaneously. Reactivity breaks across component boundaries. Pinia stores initialized in the shell are invisible to the micro UI's components because they're registered in the wrong Vue app instance. Errors are non-obvious: "inject() can only be used inside setup()" appearing at seemingly random times.
- **Warning signs:** `vue` appears in the micro UI's own `node_modules` bundle output (check with `rollup-plugin-visualizer`). `shared` config in `module-federation.config.js` does not specify `singleton: true` and `requiredVersion`. Different micro UIs have different `package.json` versions of Vue or Pinia.
- **Prevention:** In every Module Federation config: `vue` and `pinia` must have `singleton: true, eager: true` in the shell, and `singleton: true` in all remotes. Pin the same exact semver range for shared deps across all micro UI package.json files. Use `requiredVersion` to enforce this at runtime. Run a CI check that fails if shared dep versions diverge across micro UI repos. Never set `eager: true` in a remote (only the shell).
- **Address in:** Phase 3 (Micro-frontend shell scaffolding).

---

### 9. FastMCP Protocol Constraints — Blocking Tool Calls and Context Window Exhaustion

- **What goes wrong:** FastMCP tools return large document payloads directly (full text of retrieved chunks). AI agents (Claude, GPT) receive 50KB+ responses per tool call, burning context rapidly. For multi-turn agent sessions, context fills after 2-3 tool calls. Separately: MCP tools are synchronous from the agent's perspective — if the tool triggers a long ingestion job and waits, the MCP session times out. Agents also have no way to paginate results unless the tool explicitly supports a cursor parameter.
- **Warning signs:** MCP tool return values are raw document text rather than summaries + references. No `max_chunks` or `max_tokens_per_result` parameter on search tools. Tool that triggers ingestion does not return immediately with a job ID.
- **Prevention:** MCP search tools return chunk references (id, score, snippet of ~200 chars, source_doc_id) — not full text. Provide a separate `get_document_chunk(chunk_id)` tool for agents that need full content. Implement cursor-based pagination on search tools (`cursor` param, `next_cursor` in response). Any operation that takes >2 seconds returns a job ID immediately; provide a `get_job_status(job_id)` tool. Cap total response size to ~8KB per tool call. Document these constraints explicitly in the MCP server's tool descriptions so agents can plan accordingly.
- **Address in:** Phase 4 (FastMCP server).

---

### 10. API Key Security — Keys Stored or Transmitted Insecurely

- **What goes wrong:** API keys are stored as plaintext in PostgreSQL. A database dump or SQL injection exposes every third-party integration credential at once. Keys are passed in URL query parameters (`?api_key=xxx`) which get logged by every reverse proxy, load balancer, and access log in the chain. No key rotation mechanism exists, so a compromised key stays valid indefinitely.
- **Warning signs:** API key column type is `VARCHAR` or `TEXT` with no prefix about hashing. API key appears in any HTTP access log. No `last_used_at`, `created_at`, or `expires_at` columns. No audit trail of which key was used for which operation.
- **Prevention:** Store only the SHA-256 hash of the key (or use bcrypt for extra safety). Display the plaintext key only once at creation time. Accept keys via `Authorization: Bearer` or `X-API-Key` header only — never query params. Add `key_prefix` (first 8 chars, like `km_live_xxxx`) as a plaintext column for identification without exposing the full key. Include `last_used_at`, `expires_at`, `rate_limit_tier`, and a usage audit log table from day one. Implement key revocation as an instant operation (set `revoked_at`).
- **Address in:** Phase 2 (Auth infrastructure) when API key model is designed.

---

## Minor Pitfalls (Easy to recover from)

### 11. ChromaDB Persistence Mode Surprise in Docker

- **What goes wrong:** ChromaDB defaults to in-memory mode if not explicitly configured for persistence. In Docker Compose, the container restarts and all vectors are gone. Developers discover this after indexing 10,000 documents.
- **Warning signs:** ChromaDB client is instantiated as `chromadb.Client()` rather than `chromadb.PersistentClient(path=...)` or via the HTTP client pointed at a running ChromaDB server.
- **Prevention:** Run ChromaDB as a separate Docker Compose service (HTTP mode). Core API connects via `chromadb.HttpClient`. This also matches the Qdrant migration path (Qdrant is always a separate HTTP service).
- **Address in:** Phase 1 (infrastructure scaffolding).

---

### 12. Pinia Store Pollution Across Micro-UI Boundaries

- **What goes wrong:** Micro UI A registers a Pinia store named `useDocuments`. Micro UI B also registers a store named `useDocuments` for a different domain. Since they share a single Pinia instance (correctly), the second registration silently overwrites the first, causing subtle state bugs that appear only when both micro UIs are mounted simultaneously.
- **Warning signs:** Store IDs are short and generic (`documents`, `search`, `user`) without namespace prefixes.
- **Prevention:** Prefix all store IDs with the micro UI name: `kmDomains/documents`, `kmSearch/results`. Document this as a project-wide convention before any micro UI is scaffolded.
- **Address in:** Phase 3 (Micro-frontend shell).

---

### 13. Kafka Consumer Group Misconfiguration During Development

- **What goes wrong:** Each developer runs their own consumer instance with the same `group.id` as production. Messages get distributed across developer machines and the integration environment, leading to messages being "lost" (processed on dev, not in integration). After restarting Kafka in dev, `auto.offset.reset=latest` causes all previously unprocessed messages to be skipped.
- **Warning signs:** `group.id` is hardcoded as a constant in source code. `auto.offset.reset` is not explicitly set.
- **Prevention:** `group.id` is configured via environment variable. Dev environments use `group.id=dev-{developer-name}-{service}`. Set `auto.offset.reset=earliest` for all environments to avoid silent message loss on restart. Document this in the project README.
- **Address in:** Phase 2 (Ingestion pipeline) during local dev setup.

---

### 14. Uv Lockfile Drift Between Python Services

- **What goes wrong:** Core API and FastMCP server share some dependencies (e.g., `langchain-core`, embedding libraries) but are in separate `uv` projects. They drift to different versions of shared packages. Embeddings generated by the Core API use a different tokenizer version than the one used by the MCP server when it invokes embedding for query rewriting. Subtle semantic differences in search quality, hard to diagnose.
- **Warning signs:** Core API and FastMCP server have separate `pyproject.toml` files with no shared constraints on critical shared dependencies. No CI check comparing dependency versions across services.
- **Prevention:** Use a `uv` workspace at the monorepo root to manage shared dependencies as a workspace package. Or at minimum, maintain a `shared-constraints.txt` file that pins critical shared dependencies and reference it from both `pyproject.toml` files. Run a CI check that diffs the locked versions of critical packages across all Python services.
- **Address in:** Phase 1 (project scaffolding).

---

## Pitfall Priority Matrix

| Pitfall | Probability | Impact | Address In |
|---------|-------------|--------|------------|
| Vector store tight coupling (ChromaDB bleeds into business logic) | HIGH | CRITICAL | Phase 1 |
| LLM provider lock-in through Gemini API shape leakage | HIGH | CRITICAL | Phase 1 |
| Docker Compose hardcoded service names | HIGH | HIGH | Phase 1 |
| ChromaDB in-memory mode in Docker | HIGH | MEDIUM | Phase 1 |
| Uv lockfile drift across Python services | MEDIUM | MEDIUM | Phase 1 |
| Keycloak token propagation gap (BFF trusts, Core API doesn't validate) | HIGH | CRITICAL | Phase 2 |
| API key stored/transmitted insecurely | HIGH | HIGH | Phase 2 |
| MongoDB + PostgreSQL dual-write inconsistency | MEDIUM | HIGH | Phase 2 |
| Async ingestion poison pills | HIGH | HIGH | Phase 2 |
| Kafka consumer group misconfiguration | MEDIUM | MEDIUM | Phase 2 |
| Micro-frontend auth token chaos | HIGH | HIGH | Phase 2–3 |
| Module Federation version hell (Vue/Pinia singletons) | HIGH | HIGH | Phase 3 |
| Pinia store ID namespace collision | MEDIUM | LOW | Phase 3 |
| FastMCP context window exhaustion + blocking tools | MEDIUM | HIGH | Phase 4 |

---

## Phase-Specific Warnings Summary

| Phase Topic | Likely Pitfall | Mitigation |
|-------------|---------------|------------|
| Core API skeleton | No `VectorStorePort` abstraction | Define ABC before writing first ingestion code |
| Core API skeleton | Gemini imports in service layer | Enforce `EmbeddingPort` ABC; ruff import rule |
| Core API skeleton | Hardcoded Docker service hostnames | All service URLs from env vars, no code defaults |
| Ingestion pipeline | Poison pill messages | DLQ + max retries + exponential backoff required |
| Ingestion pipeline | Dual-write PostgreSQL+MongoDB | Use outbox pattern or event-driven consistency |
| Ingestion pipeline | Kafka consumer group in dev | Env-var group IDs, `auto.offset.reset=earliest` |
| Auth infrastructure | BFF validates, Core API trusts | Core API validates JWT independently via JWKS |
| Auth infrastructure | API keys in plaintext | Hash at rest, header-only transmission |
| Micro-frontend shell | Keycloak instance per micro UI | Shell owns single Keycloak instance; token bus |
| Micro-frontend shell | Duplicate Vue/Pinia instances | `singleton: true` for all shared deps in MF config |
| FastMCP server | Large payload per tool call | Return references + snippets, not full text |
| FastMCP server | Synchronous long-running tools | Return job ID immediately; poll with `get_job_status` |
| ChromaDB → Qdrant | Migration requires code changes | Only if port was violated; test against both adapters early |

---

## Confidence Notes

- **Vector store abstraction, LLM abstraction, Docker service discovery:** HIGH — these are well-documented failure modes in production RAG systems and microservice migrations.
- **Keycloak token propagation, API key security:** HIGH — standard OAuth2/OIDC security practices; Keycloak documentation is explicit about service-to-service token forwarding.
- **Async pipeline (Kafka/RabbitMQ poison pills, DLQ):** HIGH — documented in Kafka and RabbitMQ official documentation; standard distributed systems resilience patterns.
- **Module Federation Vue singletons:** HIGH — documented in Webpack Module Federation docs and Vue 3 ecosystem guides; common production issue.
- **FastMCP protocol constraints:** MEDIUM — FastMCP is emerging (MCP protocol is ~1 year old as of 2026-05); constraints are inferred from MCP spec and how LLM agent tool calls work; specific FastMCP server behavior should be validated against current docs.
- **MongoDB + PostgreSQL dual-write:** HIGH — standard distributed data consistency problem; outbox pattern is well-established.
- **Uv workspace / lockfile drift:** MEDIUM — uv workspace support exists but is relatively new; verify current workspace behavior in uv docs before implementing.

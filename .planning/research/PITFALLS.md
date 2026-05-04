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

---

# Milestone v1.1 Pitfalls: Visual Ontology Editor + Domain Edit Modal

**Milestone:** Domain Intelligence — adds visual canvas editor (`@vue-flow/core` in `domains-ui`), domain edit modal reusing the create form, shared `CanvasToolbox` component via Module Federation, and JSONB ontology persistence in PostgreSQL.
**Researched:** 2026-05-03
**Confidence:** HIGH for Vue 3 reactivity and MF integration patterns; HIGH for PostgreSQL JSONB; MEDIUM for `@vue-flow/core` specifics (verify CSS import paths against current version).

---

## Critical Pitfalls — Canvas/Graph Editor

### C1. Missing CSS Import Kills the Entire Canvas Silently

**What goes wrong:** `@vue-flow/core` requires its own stylesheet to be imported explicitly. If `@vue-flow/core/dist/style.css` (and optionally `@vue-flow/core/dist/theme-default.css`) are not imported, the canvas renders as a blank area with zero visible nodes and no error. Developers spend time debugging Vue component logic when the problem is a missing 2-line CSS import. In a micro-frontend setup this is worse: the CSS must be imported in the consuming micro UI (`domains-ui`), not in the shell, because the shell doesn't mount the canvas.

**Why it happens:** Vue Flow uses absolute CSS class names for node positioning (`.vue-flow__node`, `.vue-flow__edge`). Without the stylesheet those classes have no dimensions or positioning, so nodes collapse to 0x0 pixels and are invisible.

**Consequences:** Canvas appears blank. No console error. Debugging leads developers into Vue Flow's JavaScript internals rather than CSS. Hours lost.

**Prevention:** Import both required stylesheets at the top of `domains-ui/src/main.ts` (not in a component):
```ts
import '@vue-flow/core/dist/style.css'
import '@vue-flow/core/dist/theme-default.css'
```
Add a CI lint rule or a component test that mounts `<VueFlow>` with a test node and asserts the node element has `offsetWidth > 0`. This catches the missing import before it reaches review.

**Detection warning signs:** Canvas container div exists in DOM but has no children, or children are present with `width: 0; height: 0`. `document.querySelectorAll('.vue-flow__node')` returns elements but `getBoundingClientRect()` is all zeros.

**Address in:** `domains-ui` setup phase, first canvas component. Put in component scaffold checklist.

---

### C2. Vue Flow Container Requires Explicit Pixel Dimensions — Percentage Heights Silently Fail

**What goes wrong:** `<VueFlow>` sizes itself to fill its parent container. If the parent container has `height: 100%` without a concrete ancestor height, or if the parent is a flexbox child with no `flex: 1` + explicit height on the flex parent, the canvas resolves to `height: 0` and renders nothing. This is a browser CSS behavior, not a Vue Flow bug, but it manifests as a blank canvas and is non-obvious in a glassmorphism modal where layers of `backdrop-filter` and absolute positioning are already present.

**Why it happens:** `height: 100%` on a non-replaced element only works if the parent has a definite height. Modal dialogs frequently use `max-height` and overflow patterns that break percentage-height children.

**Consequences:** Canvas blank inside modal. Confusing because it worked in a standalone test page with explicit `height: 600px`. The DESIGN.md glassmorphism aesthetic makes this especially likely because modals are sized with fluid constraints.

**Prevention:**
- Give the `<VueFlow>` wrapper a concrete height: either an explicit pixel value (`height: 600px`) or a CSS variable from the design system, not `100%`.
- Use `height: calc(100vh - Xpx)` for the modal body, then assign that to the canvas wrapper.
- Test the canvas inside the actual modal component, not in an isolated dev page with a simple `<div style="height:600px">`.

**Detection warning signs:** Canvas node dragging API fires events but nothing moves on screen. `getComputedStyle(canvasEl).height` returns `'0px'`.

**Address in:** `domains-ui` ontology editor modal implementation.

---

### C3. Bundle Size — @vue-flow/core Is Not Tree-Shakeable for Non-Used Node Types

**What goes wrong:** `@vue-flow/core` bundles all built-in node renderers (default, input, output, group) and edge types. Even if only one node type is used, the full library ships. As of late 2024 the gzipped bundle was approximately 45–60KB. In a micro-frontend context this is per-remote — `domains-ui` pays the full cost. If `@vue-flow/core` is added to Module Federation's `shared` scope to avoid duplication with a future `ingestion-ui` flow editor, the singleton constraint means both apps must use the exact same version, which creates a forced upgrade coupling.

**Why it happens:** Vue Flow is a monolithic package with no subpath exports for individual node types. The official advice is to use it as-is and accept the bundle size.

**Consequences:** `domains-ui` remote bundle grows by ~60KB gzipped. If shared via MF, any version upgrade in one remote forces an upgrade in all remotes simultaneously.

**Prevention:**
- Do NOT add `@vue-flow/core` to the Module Federation `shared` scope for v1.1. Let each remote bundle its own copy. 60KB is acceptable for an admin-use ontology editor, not a daily-use search UI.
- If `ingestion-ui` later adds a flow editor (Phase: ingest pipeline visualization), accept the duplication rather than creating a forced version coupling. Re-evaluate sharing only when both remotes are on the same minor version and a deliberate shared-upgrade policy exists.
- Monitor bundle size with `rollup-plugin-visualizer` after adding Vue Flow. Flag if `domains-ui` total bundle exceeds 300KB gzipped.

**Address in:** `domains-ui` Vite configuration. Do not add Vue Flow to shell's `shared` list.

---

### C4. Event Conflicts Between Vue Flow's Internal Pointer Events and the Modal Drag Handler

**What goes wrong:** Vue Flow registers `pointerdown`, `pointermove`, `pointerup` event listeners on the canvas container for node dragging, panning, and selection. If the parent modal component also registers drag-to-resize or scroll-lock behavior (common in glassmorphism modals for resizing the panel), the events conflict. Vue Flow's `stopPropagation()` calls prevent the modal from receiving events it needs; alternatively the modal's event handlers intercept Vue Flow's drag before Vue Flow gets it. Result: node dragging either doesn't work or causes the modal to move/resize instead.

**Why it happens:** Both Vue Flow and modal drag handlers compete for the same pointer event stream on overlapping DOM elements. Glassmorphism modals in this design system are often resizable or positioned via drag — they use the same event primitives.

**Consequences:** Node dragging non-functional inside modal. Or worse: dragging a node drags the entire modal window. User experience breaks.

**Prevention:**
- The ontology editor modal must be non-draggable and non-resizable by the user. Use a fixed-size, centered modal (not a floating draggable panel) for the editor. This eliminates the competing drag handler entirely.
- If a resizable modal is required in the future, attach the resize handle events to a narrow border element with `pointer-events: none` on the inner canvas wrapper, then re-enable via `pointer-events: auto` on the resize handle only.
- In `VueFlow`'s parent element, apply `touch-action: none` to prevent scroll interference on touch devices.

**Address in:** Ontology editor modal component design. Decide non-draggable modal as the architecture before implementation.

---

### C5. Vue Flow State Lives Outside Pinia — Ontology Data Is Duplicated

**What goes wrong:** Vue Flow's nodes and edges are managed internally by the library via its own reactive state (accessed through `useVueFlow()` composable). Developers often store a second copy in a Pinia store (for persistence, undo, or dirty-state tracking) and then try to keep the two in sync with watchers. The watcher fires on every tiny drag movement (position update), causing Pinia writes at 60fps during drag, which triggers re-renders across any component subscribed to that store, and causes visible jank.

**Why it happens:** Vue Flow's internal state is the source of truth for rendering positions. Pinia is the source of truth for saved/persisted data. These are two different concerns that developers conflate.

**Consequences:** Performance degradation during node dragging. 60fps Pinia writes slow the app on mobile/low-end devices. Infinite update loops if Pinia write triggers a Vue Flow nodes prop update, which triggers the watcher again.

**Prevention:**
- Maintain a clear separation: Vue Flow owns position/interaction state; Pinia owns the saved ontology model.
- Only synchronize to Pinia on explicit user actions: `onNodeDragStop`, `onConnect`, `onEdgesChange` (for deletions), and explicit "Save" button.
- Never watch Vue Flow's `nodes` array reactively and write to Pinia on every change.
- The Pinia store shape should be the serialized JSONB format (node ID, type, label, position, edges), not a clone of Vue Flow's internal node object. Transform on save, transform on load.

**Address in:** `domains-ui` ontology store design. Define the Pinia↔Vue Flow boundary before writing the first composable.

---

## Critical Pitfalls — Module Federation Shared Canvas Toolbox

### MF1. The Shared Toolbox Becomes a Version Anchor That Blocks Both Editor Upgrades

**What goes wrong:** `CanvasToolbox` is extracted to `frontend/libs/canvas-toolbox` and exposed via Module Federation shared scope, consumed by both `domains-ui` and the future `ingestion-ui`. Six months later, `ingestion-ui` needs the toolbox to support a "minimap toggle" button that is specific to its flow type. The fix requires changing the `CanvasToolbox` component's props interface. But `domains-ui` has not been updated. Because both remotes depend on the same shared version, modifying `canvas-toolbox` to support the new prop either: (a) requires bumping the version and updating both remotes simultaneously, or (b) adds `optional` props with different behaviors, creating an inconsistent component.

**Why it happens:** The "shared toolbox" assumption is that toolbox controls are generic. In practice, each editor type has slightly different viewport controls (minimap for one, layout reset for the other, grid toggle for one but not the other). The divergence is slow and invisible until it's painful.

**Consequences:** Either both remotes are always coupled for deployment (defeating the micro-frontend independence goal), or the shared component accumulates a prop explosion of editor-specific flags.

**Prevention:** Design `CanvasToolbox` with a slot-based extension model from day one:
```vue
<CanvasToolbox>
  <template #custom-actions>
    <!-- ingestion-ui inserts its own buttons here -->
  </template>
</CanvasToolbox>
```
The toolbox exposes fixed slots for `left-actions`, `right-actions`, and `center-actions`. Core controls (zoom-in, zoom-out, fit-to-window, snap-to-grid toggle) are always rendered by the component. Editor-specific controls are slotted in by the consuming micro UI. This prevents prop explosion while keeping the shared contract stable.

Also: version `canvas-toolbox` with semantic versioning from the start (`1.0.0`). Any breaking slot or prop change bumps major version. Both remotes declare which major version they consume, allowing independent upgrade cycles.

**Address in:** `canvas-toolbox` library initial design. Do not ship v1.1 without the slot architecture.

---

### MF2. CSS From canvas-toolbox Leaks Into the Shell's Global Scope

**What goes wrong:** `CanvasToolbox` is a Vue component in a shared library. When bundled and loaded via Module Federation, its `<style>` blocks are injected into the document `<head>` as global `<style>` tags (standard Vue SFC behavior). If `CanvasToolbox` uses class names like `.toolbox-btn`, `.zoom-control`, or `.icon-btn` without a unique prefix or CSS Modules, those classes collide with any other component in the shell or other micro UIs that use the same names. In a glassmorphism design system where many components share structural class names (`.btn`, `.card`, `.icon`), this is a high-probability collision.

**Why it happens:** `@originjs/vite-plugin-federation` does not isolate CSS by default. Shared library CSS is injected globally. Vue SFCs use scoped styles (`<style scoped>`) which generate per-component attribute selectors, but only if `scoped` is explicitly used.

**Consequences:** Visual regression in unrelated components after adding the toolbox. Styles bleed between micro UIs. Hard to debug because the class name collision only appears at runtime when all remotes are loaded, not during isolated development.

**Prevention:**
- Every `<style>` block in `canvas-toolbox` components must use `<style scoped>` or CSS Modules (`<style module>`).
- Use the `scoped` approach by default. It generates `[data-v-xxxxxxxx]` attribute selectors that namespace the styles automatically.
- Alternatively: prefix all class names in `canvas-toolbox` with `ktb-` (Knowledge Toolbox) — e.g., `ktb-btn`, `ktb-zoom-control`. This is belt-and-suspenders protection even without `scoped`.
- Add a visual regression test that loads the shell with `domains-ui` mounted and checks that shell nav component styles are unchanged after the toolbox is loaded.

**Address in:** `canvas-toolbox` component authoring standards. Enforce in code review checklist.

---

### MF3. canvas-toolbox Shared in MF Scope Requires @vue-flow/core to Be Available — Which Creates a Hidden Transitive Dependency

**What goes wrong:** `CanvasToolbox` imports Vue Flow composables (`useVueFlow()`) to drive zoom and fit-to-window actions. When `canvas-toolbox` is declared as a Module Federation shared module, any remote that loads it must also have `@vue-flow/core` available — either bundled or also shared. If `ingestion-ui` uses a different flow library (e.g., `vue-flow-render` or a custom canvas), it either (a) must also install `@vue-flow/core` as a dead dependency just to satisfy the shared toolbox, or (b) the toolbox fails at runtime with "cannot find module @vue-flow/core."

**Why it happens:** The toolbox was designed assuming every consumer uses Vue Flow. When the second editor type uses a different canvas library, the assumption is violated.

**Prevention:** Decouple `CanvasToolbox` from `@vue-flow/core` internals. Instead of calling `useVueFlow()` directly inside the toolbox, accept the zoom/fit actions as props or emit events that the parent editor wires up:
```ts
// CanvasToolbox interface — no vue-flow import
defineProps<{
  onZoomIn: () => void
  onZoomOut: () => void
  onFitView: () => void
  snapToGrid: boolean
  onSnapToggle: () => void
}>()
```
The consuming editor (`domains-ui`) calls `useVueFlow()` itself and passes the action functions as props. `CanvasToolbox` has zero canvas library dependency and works with any canvas implementation.

**Address in:** `canvas-toolbox` API design. Define this interface before any implementation is written.

---

## Critical Pitfalls — Domain Edit Modal (Form Reuse)

### FM1. Dirty State Is Not Isolated Per Modal Instance — Opening Edit Modal Corrupts Create Form State

**What goes wrong:** The create form and edit modal share one Pinia store (e.g., `useDomainFormStore`) that holds `{ name, description, icon, color }`. When the user opens the edit modal pre-loaded with an existing domain's values, those values are written into the shared store. If the user then cancels the edit (or the modal closes unexpectedly), the create form now shows the previously edited domain's values. Next time the user opens "Create New Domain," the form is pre-filled with the last-edited domain's data.

**Why it happens:** A single Pinia store instance is shared between two components (create form and edit modal) instead of each component owning its own reactive local state.

**Prevention:** The form fields (`name`, `description`, etc.) must live in `useLocalState` (local `ref`s or `reactive()`) inside the form component, not in a shared Pinia store. Only persist to Pinia (or to the API) on explicit submit. The edit modal initializes local state from props (`editingDomain`) via `watch` on mount:
```ts
const localForm = reactive({ name: '', description: '', icon: '', color: '' })

// Edit mode: seed from prop
watch(() => props.editingDomain, (domain) => {
  if (domain) Object.assign(localForm, { ...domain })
}, { immediate: true })

// Create mode: reset on mount
onMounted(() => {
  if (!props.editingDomain) Object.assign(localForm, defaultForm())
})
```
The form component is stateless beyond its own lifecycle. Pinia store only holds the list of saved domains, not unsaved form drafts.

**Address in:** Domain form component architecture. Establish this pattern before the first form component is coded.

---

### FM2. Optimistic UI Update Causes Visible Domain Card Data Flip on Save Failure

**What goes wrong:** The domain list in `domains-ui` updates the card immediately when the user clicks Save in the edit modal (optimistic update), before the `PUT /v1/domains/:id` response arrives. If the API returns a 400 (validation error) or 500, the UI must revert the card to its previous values. The reversal is visible as a data "flip" — the card shows the new values for ~500ms, then snaps back to the old values. On slow connections this is confusing and erodes trust.

**Compounding issue:** If the user opens another domain card while the first save is in-flight, and the first save fails, the revert affects the card that is now scrolled out of view. The user has no feedback that the edit failed.

**Why it happens:** Optimistic updates require a clean rollback path that most implementations forget to design for, especially when the user has navigated away from the element being updated.

**Prevention:** For this use case, do NOT use optimistic updates. Use a confirmed-save pattern:
1. User clicks Save. Button shows spinner. Modal stays open.
2. `PUT /v1/domains/:id` request is sent. Await response.
3. On success: close modal, update Pinia store with server-returned data, show brief success toast.
4. On failure: keep modal open, show inline error message (e.g., "Failed to save: Name already exists"), leave form data intact.

The perceived latency (200-400ms) for a domain save is acceptable. Optimistic updates are appropriate for low-stakes, easily reversible operations (e.g., toggling a star/favorite). Domain metadata edits are high-stakes enough to require confirmed save.

**Address in:** Domain edit modal UX design. Document the confirmed-save pattern as a project-wide convention for entity edit operations.

---

### FM3. Form Validation State Not Reset Between Edit Invocations — Stale Error Messages Appear

**What goes wrong:** User edits Domain A, submits with an empty name, sees "Name is required" error. Closes the modal. Opens the edit modal for Domain B (which has a valid name). The "Name is required" error message from Domain A's failed submit is still visible in the form immediately on open, before the user has done anything. This happens because the validation state (error messages, touched flags) lives in a reactive object that persists between modal invocations.

**Why it happens:** VeeValidate, vuelidate, and custom validation composables all maintain state that is not automatically reset when a parent component's `v-if` is false. If the modal uses `v-show` instead of `v-if`, the component is never unmounted, so `onMounted` reset logic never runs.

**Prevention:**
- Use `v-if` on the modal component, not `v-show`. This fully unmounts and remounts the form component on each open, clearing all reactive validation state automatically. This is the simplest and most reliable solution.
- If `v-show` is required for animation performance: call an explicit `resetForm()` (VeeValidate) or manually clear all error refs in the `watch` that responds to `props.editingDomain` changing.
- Never use `v-show` for a form modal that shares validation state across different entity instances.

**Address in:** Domain edit modal component template. Decision must be made at scaffold time (v-if vs v-show).

---

## Critical Pitfalls — JSONB Ontology in PostgreSQL

### DB1. JSONB Ontology Column Has No Schema Enforcement — Silent Data Corruption Accumulates

**What goes wrong:** The ontology is stored as a JSONB column in the `domains` table (or a separate `domain_ontologies` table). Early in development the node shape is `{ id, label, type, x, y }`. Six weeks later the frontend adds `color`, `icon`, and `description` to nodes. The save path writes the new shape. The load path reads old records that have no `color`, `icon`, or `description` fields. The frontend receives mixed shapes — some nodes have the new fields, some don't. Components crash with "Cannot read properties of undefined (reading 'color')." Worse: a schema change that renames `label` to `name` permanently corrupts records saved under the old key.

**Why it happens:** JSONB imposes zero schema constraints. The database accepts any JSON. Without explicit versioning and migration, every saved ontology is a time capsule of whichever frontend version wrote it.

**Consequences:** Frontend crashes on old ontologies. Data loss if a rename migration is applied to JSONB without a data migration script. Impossible to query ontology contents for analytics or debugging without knowing the current schema.

**Prevention:**
1. Include a `schema_version` field in every saved ontology document: `{ "schema_version": 1, "nodes": [...], "edges": [...] }`.
2. Write a `normalizeOntology(raw, version)` function in the frontend that migrates older versions to the current shape on load. Keep all version migrations forever.
3. Write a PostgreSQL migration for every ontology schema change that runs an `UPDATE` to transform existing JSONB records. Never assume old records will just work with new frontend code.
4. Define a TypeScript `OntologySchema` type for the JSONB content and generate it from a single source of truth (a `zod` schema). The API serializes/deserializes through this schema, rejecting any stored document that fails validation on read (logs and returns an empty default instead of crashing).

**Address in:** First time `PUT /v1/domains/:id/ontology` is implemented. The `schema_version: 1` must be in the first write. Retroactively adding it is a migration.

---

### DB2. Full JSONB Blob Written on Every Save — Concurrent Edits and Large Graphs Cause Last-Write-Wins Data Loss

**What goes wrong:** The save operation is `PUT /v1/domains/:id/ontology` with the full JSONB body. If two users have the ontology editor open simultaneously (Admin A and Admin B), both make changes, and both click Save: the second save overwrites the first completely, silently discarding the first user's changes. For an ontology with 50+ nodes, the full blob on every save is also 10–50KB per PUT request, which is acceptable for small graphs but will become a problem as ontologies grow.

**Why it happens:** Full-document PUT is the simplest API design. Without optimistic concurrency control (OCC), there is no conflict detection.

**Consequences:** Silent data loss on concurrent edits. No error, no warning — the second user's save silently destroys the first user's work.

**Prevention:**
- Add an `updated_at` timestamp (or an integer `version` field) to the ontology record.
- The PUT request must include the `version` the client last loaded: `{ "schema_version": 1, "client_version": 3, "nodes": [...], "edges": [...] }`.
- The API checks: if `stored_version != client_version`, return HTTP 409 Conflict. Frontend shows "Another user has modified this ontology. Reload before saving."
- For MVP (single-admin platform): the likelihood of concurrent edits is low, but the OCC field costs almost nothing to add and prevents a class of bugs. Add it from the first write.
- If the ontology grows large (100+ nodes), consider a partial-update endpoint: `PATCH /v1/domains/:id/ontology/nodes/:nodeId` for individual node edits, rather than full-document PUT.

**Address in:** Ontology API design. Must be specified before implementation of `PUT /v1/domains/:id/ontology`.

---

### DB3. No Index on JSONB Fields Means Future Ontology Queries Are Full Table Scans

**What goes wrong:** In v1.1 the only query is "load the full ontology for domain X" — a point lookup by `domain_id`. This is fast (indexed by `domain_id`). In v2, requirements emerge to query across ontologies: "find all domains that have a node of type `Concept`" or "find all nodes labeled `Machine Learning` across all domain ontologies." These queries use JSONB path operators (`@>`, `jsonb_path_query`) and require a GIN index on the JSONB column. Without the index, a search across 1,000 domain ontologies is a sequential scan of the entire JSONB column.

**Why it happens:** JSONB columns have no index by default. Standard B-tree indexes don't work on JSON content. Adding a GIN index later, after the table has grown, is a long-running `CREATE INDEX CONCURRENTLY` that blocks during maintenance windows.

**Prevention:** Add a GIN index on the ontology column at migration time, in the same migration that creates the column:
```sql
CREATE INDEX idx_domain_ontology_gin ON domain_ontologies USING gin (ontology_data);
```
This costs ~5ms at table creation (empty table) and costs nothing to maintain on a table that is updated infrequently. It makes future cross-domain ontology queries efficient without a schema change.

Also: extract `node_count` and `edge_count` as regular integer columns (updated on every PUT) so summary queries never need to inspect the JSONB blob.

**Address in:** The Alembic migration that creates the `domain_ontologies` table.

---

### DB4. Vue Flow's Node Position Data Is Transient UI State — Storing It in the Canonical Ontology Is a Design Error

**What goes wrong:** Vue Flow nodes have `position: { x, y }` which represents where the node was last dropped on the canvas. Developers include this position in the JSONB ontology blob saved to the backend: `{ id, label, type, color, position: { x: 120, y: 340 } }`. The position is now part of the canonical domain knowledge representation. This creates two problems: (1) auto-layout algorithms (dagre, elk) recalculate positions on every render and generate spurious `PUT /ontology` diffs even when no domain knowledge changed; (2) when the canvas library is swapped in the future (Vue Flow → a custom renderer), the stored position coordinate system may differ.

**Why it happens:** It is convenient to serialize the entire Vue Flow node object to JSON and POST it. The position is just there.

**Prevention:** Separate the ontology schema (semantic knowledge) from the layout schema (visual positions):
```json
{
  "schema_version": 1,
  "nodes": [
    { "id": "uuid", "label": "Machine Learning", "type": "concept", "color": "#007AFF", "description": "..." }
  ],
  "edges": [
    { "id": "uuid", "source": "node-id-1", "target": "node-id-2", "label": "includes" }
  ],
  "layout": {
    "node-id-1": { "x": 120, "y": 340 },
    "node-id-2": { "x": 400, "y": 200 }
  }
}
```
`nodes` and `edges` are the semantic ontology. `layout` is canvas position data. The PUT to the backend only triggers a meaningful change notification if `nodes` or `edges` changed. `layout` changes are debounced and saved separately (or only saved when the user explicitly clicks "Save Layout"). This also makes it trivial to apply an auto-layout: regenerate `layout` without touching `nodes`/`edges`.

**Address in:** Ontology data model design. Define this separation in the TypeScript `OntologySchema` type before any data is written to the backend.

---

## The "Reuse the Toolbox" Assumption — Divergence Pitfalls

### DIV1. The Toolbox Diverges Along Editor Semantics, Not UI Controls

**What goes wrong:** The assumption is that all canvas editors share the same toolbox controls: Zoom In, Zoom Out, Fit to Window, Snap to Grid. This is true at launch. Within two to three months of building the second editor type (e.g., ingestion pipeline flow editor in `ingestion-ui`), the toolbox needs diverge along semantic lines, not cosmetic ones:

| Control | Ontology Editor | Pipeline Flow Editor |
|---------|----------------|---------------------|
| Zoom In/Out | Yes | Yes |
| Fit to View | Yes | Yes |
| Snap to Grid | Yes | Yes |
| Auto Layout (dagre) | Yes — for concept graphs | No — user designs pipeline manually |
| Validate Pipeline | No | Yes — check for disconnected nodes |
| Minimap Toggle | Maybe | Yes — pipelines are large |
| Undo/Redo | Yes | Yes — but different history depth |
| Node Palette | No | Yes — drag-and-drop node types |

The semantic controls (Validate, Auto Layout) are specific to one editor type. Adding them as optional props/slots to the shared `CanvasToolbox` creates a component that is 60% conditional rendering based on `editorType` prop. This is an anti-pattern (god component).

**Prevention:** The shared `CanvasToolbox` must be a thin structural shell that provides consistent sizing, visual styling (glassmorphism button group from DESIGN.md), and keyboard shortcut registration infrastructure. It exposes four named slots: `#start`, `#center`, `#end`, `#overflow-menu`. Each editor injects its own semantic controls into the appropriate slot. The toolbox never knows what editor type it's in.

This is the same as MF1 (slot architecture) but stated here as a behavioral principle: shared = structure, not semantics.

**Address in:** `canvas-toolbox` design specification. Must be resolved before building the second editor type.

---

### DIV2. Keyboard Shortcut Conflicts Between the Toolbox and Vue Flow's Internal Shortcuts

**What goes wrong:** `@vue-flow/core` registers keyboard shortcuts internally: Delete/Backspace to remove selected elements, Ctrl+A to select all. The `CanvasToolbox` also wants to register Ctrl+Z (undo), Ctrl+Y (redo), Ctrl+Shift+F (fit view), and `+`/`-` for zoom. If both the toolbox and Vue Flow register handlers for the same keys via `addEventListener('keydown')` on `document`, both fire. Pressing Delete intending to remove a selected node also triggers the toolbox's "delete graph" confirmation dialog, if one exists.

**Why it happens:** `addEventListener` on `document` does not automatically check for conflicts. Vue Flow uses its own internal keyboard handling that is not exposed to the consumer. The toolbox registers global key handlers without awareness of Vue Flow's existing bindings.

**Consequences:** Unexpected dialog popups on standard keypresses. Node deletion triggers both the Vue Flow removal and the toolbox's action.

**Prevention:**
- Do NOT register global `keydown` listeners in the toolbox. Register them on the canvas wrapper element only, scoped to when the canvas has focus. Use `e.stopPropagation()` only for toolbox-specific shortcuts, not as a blanket call.
- Check Vue Flow's documented keyboard shortcuts and exclude them from the toolbox's shortcut registry.
- Provide a `disableKeyboardShortcuts` prop on `CanvasToolbox` for the rare case where the host page has its own shortcut system.
- Document all keyboard shortcuts in a central file (`shortcuts.ts`) so both editors and the toolbox register from the same source of truth, preventing duplicates.

**Address in:** `canvas-toolbox` keyboard handler implementation.

---

## Updated Pitfall Priority Matrix

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
| **[v1.1] Vue Flow CSS import missing** | HIGH | HIGH | domains-ui canvas setup |
| **[v1.1] Vue Flow container height = 0 in modal** | HIGH | HIGH | ontology editor modal |
| **[v1.1] Vue Flow bundled in MF shared scope** | MEDIUM | MEDIUM | domains-ui Vite config |
| **[v1.1] Pointer event conflict in draggable modal** | MEDIUM | HIGH | modal component design |
| **[v1.1] Vue Flow state synced to Pinia at 60fps** | HIGH | HIGH | ontology store design |
| **[v1.1] canvas-toolbox becomes version anchor** | HIGH | HIGH | canvas-toolbox library design |
| **[v1.1] canvas-toolbox CSS leaks into global scope** | HIGH | MEDIUM | canvas-toolbox component styles |
| **[v1.1] canvas-toolbox imports @vue-flow/core internally** | MEDIUM | HIGH | canvas-toolbox API design |
| **[v1.1] Shared form store corrupts create/edit state** | HIGH | HIGH | domain form component design |
| **[v1.1] Optimistic update data flip on save failure** | MEDIUM | MEDIUM | edit modal UX pattern |
| **[v1.1] Stale validation errors across modal invocations** | HIGH | MEDIUM | modal v-if vs v-show decision |
| **[v1.1] JSONB schema drift — no version field** | HIGH | CRITICAL | first ontology API migration |
| **[v1.1] Full JSONB PUT — last-write-wins data loss** | MEDIUM | HIGH | ontology API design |
| **[v1.1] No GIN index on ontology JSONB** | MEDIUM | MEDIUM | Alembic migration |
| **[v1.1] Vue Flow position stored in canonical ontology** | HIGH | MEDIUM | OntologySchema type definition |
| **[v1.1] Toolbox diverges into god component** | HIGH | HIGH | canvas-toolbox slot architecture |
| **[v1.1] Keyboard shortcut conflict (toolbox vs Vue Flow)** | MEDIUM | MEDIUM | canvas-toolbox keyboard handler |

---

## Phase-Specific Warnings Summary — v1.1 Additions

| Phase / Component | Likely Pitfall | Mitigation |
|-------------------|---------------|------------|
| domains-ui canvas setup | Missing Vue Flow CSS imports | Import both style files in `main.ts`; add height-assertion test |
| ontology editor modal | Canvas height resolves to 0 | Explicit pixel height on canvas wrapper; test inside modal not standalone |
| domains-ui Vite config | Vue Flow in MF shared scope | Do NOT share; let each remote bundle its own copy |
| Modal component design | Pointer events conflict with drag | Non-draggable, non-resizable modal for canvas; `touch-action: none` on canvas |
| Ontology store design | Vue Flow nodes synced to Pinia at 60fps | Only sync on `onNodeDragStop`, `onConnect`, explicit Save button |
| canvas-toolbox library design | Component becomes version anchor | Slot architecture: `#start`, `#center`, `#end` slots from day one |
| canvas-toolbox component styles | CSS class name leakage to shell | `<style scoped>` on every component + `ktb-` class prefix |
| canvas-toolbox API design | Hidden transitive dep on @vue-flow/core | Accept zoom/fit as props (callbacks), never import `useVueFlow` inside toolbox |
| Domain form component design | Shared Pinia store corrupts create/edit | Local `reactive()` state in component; Pinia only for saved list |
| Edit modal UX pattern | Optimistic update data flip | Confirmed-save pattern: spinner, await API, then update store |
| Modal v-if vs v-show | Stale validation state on re-open | Use `v-if` to unmount/remount form; never `v-show` for entity edit modals |
| First ontology API migration | JSONB schema drift | `schema_version: 1` in first write; `normalizeOntology()` on load |
| Ontology API design | Last-write-wins on concurrent PUT | `version` field in payload; HTTP 409 on conflict; check from day one |
| Alembic migration (domain_ontologies) | Full-table scan on future JSONB queries | GIN index in same migration as table creation |
| OntologySchema type definition | Position data in canonical ontology | Separate `nodes/edges` (semantic) from `layout` (positional) in schema |
| canvas-toolbox slot architecture | Toolbox accumulates editor-specific flags | Shared = structure only; semantics go into named slots |
| canvas-toolbox keyboard handler | Shortcut conflict with Vue Flow internals | Register on canvas element, not document; central `shortcuts.ts` registry |

---

## Confidence Notes

- **Vector store abstraction, LLM abstraction, Docker service discovery:** HIGH — these are well-documented failure modes in production RAG systems and microservice migrations.
- **Keycloak token propagation, API key security:** HIGH — standard OAuth2/OIDC security practices; Keycloak documentation is explicit about service-to-service token forwarding.
- **Async pipeline (Kafka/RabbitMQ poison pills, DLQ):** HIGH — documented in Kafka and RabbitMQ official documentation; standard distributed systems resilience patterns.
- **Module Federation Vue singletons:** HIGH — documented in Webpack Module Federation docs and Vue 3 ecosystem guides; common production issue.
- **FastMCP protocol constraints:** MEDIUM — FastMCP is emerging (MCP protocol is ~1 year old as of 2026-05); constraints are inferred from MCP spec and how LLM agent tool calls work; specific FastMCP server behavior should be validated against current docs.
- **MongoDB + PostgreSQL dual-write:** HIGH — standard distributed data consistency problem; outbox pattern is well-established.
- **Uv workspace / lockfile drift:** MEDIUM — uv workspace support exists but is relatively new; verify current workspace behavior in uv docs before implementing.
- **[v1.1] Vue Flow CSS import and height pitfalls:** HIGH — these are the two most-reported Vue Flow integration issues in community GitHub issues and Stack Overflow as of training cutoff (Aug 2025). Verify CSS import path against current `@vue-flow/core` npm package structure before implementing.
- **[v1.1] Vue Flow bundle size and MF sharing:** HIGH — this is a well-understood Module Federation tradeoff; the specific gzipped size (~45–60KB) should be verified with `rollup-plugin-visualizer` against the version actually installed.
- **[v1.1] Pinia/Vue Flow state sync at 60fps:** HIGH — standard reactive performance anti-pattern; applies to any Vue Flow integration with external state management.
- **[v1.1] canvas-toolbox slot architecture and CSS scoping:** HIGH — standard Vue 3 + Module Federation best practices; these are not library-specific claims.
- **[v1.1] JSONB schema versioning and GIN indexes:** HIGH — standard PostgreSQL JSONB best practices; well-documented in PostgreSQL official documentation.
- **[v1.1] Confirmed-save vs optimistic update for entity edits:** HIGH — standard UX engineering pattern; the recommendation is specific to the risk profile of domain metadata edits.
- **[v1.1] Toolbox divergence into god component:** HIGH — this is a well-known component design failure mode; the slot-based prevention is the standard Vue 3 solution.

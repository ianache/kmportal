# Features Research: Knowledge Management Platform

**Domain:** Internal enterprise knowledge management with semantic search and AI agent integration
**Researched:** 2026-05-02 (v1.0), updated 2026-05-03 (v1.1 — visual ontology editor addendum)
**Confidence:** MEDIUM (training data + full project context; WebSearch unavailable)

---

## TABLE OF CONTENTS

- [Original v1.0 Feature Research](#original-v10-feature-research)
- [v1.1 Addendum: Visual Ontology Editor](#v11-addendum-visual-ontology-editor)

---

## Original v1.0 Feature Research

*(Unchanged from prior milestone — reproduced for continuity)*

### Table Stakes (Must Have)

These are features users and integrators expect from any serious KM platform. Missing any of these causes abandonment or rejection during evaluation.

#### Domain Management

- **Domain CRUD (admin)** — Admins create, name, describe, and delete knowledge domains. Domains are the top-level organizational primitive; without them the platform has no structure. | Complexity: Low | v1
- **Domain access control** — Assign which users/roles can read which domains. A domain is useless if everyone sees everything or nothing. Depends on: Auth/AuthZ. | Complexity: Medium | v1
- **Domain listing and browsing** — Users see the list of domains they can access, with document counts and last-updated timestamps. Basic discoverability. | Complexity: Low | v1

#### Document Ingestion and Processing

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

#### Search

- **Semantic (vector) search** — Find documents by meaning, not just keywords. This is the primary value-add over a simple file share. | Complexity: Medium | v1
- **Hybrid search** — Combine vector similarity with keyword (BM25) scoring for better recall. Pure vector search misses exact-match queries (IDs, names, codes). | Complexity: Medium | v1
- **Domain-scoped search** — Search within one domain or across multiple authorized domains. Users must not get results from domains they cannot access. | Complexity: Low | v1
- **Metadata/filter search** — Filter results by file type, date range, source, domain. Required for power users working with large corpora. | Complexity: Low | v1
- **Search result ranking and relevance scores** — Return results with a relevance score, not just a list. Users need to trust and understand why a result ranked first. | Complexity: Low | v1
- **Snippet/excerpt in results** — Show the relevant text passage around the match, not just a filename. Critical for deciding which result to open. | Complexity: Low | v1
- **Pagination** — Handle large result sets without returning thousands of chunks at once. | Complexity: Low | v1

#### Authentication and Authorization

- **OAuth2/OIDC login via Keycloak** — Web users authenticate through the existing Keycloak instance. Non-negotiable given the project constraint and enterprise context. | Complexity: Medium | v1
- **Role-based access control (RBAC)** — At minimum: admin and reader roles. Admins manage domains/sources; readers search. | Complexity: Medium | v1
- **API Key issuance and management** — Create, revoke, and list API Keys for third-party callers. Without this, third parties cannot access the platform. | Complexity: Medium | v1
- **API Key scoping** — Keys scoped to specific domains or read-only operations. A key that accesses everything is a security liability. | Complexity: Medium | v1
- **Session management** — Token refresh, logout, and session expiry handled correctly. Standard OIDC requirement. | Complexity: Medium | v1

#### Core API

- **Document upload endpoint (REST async)** — Accept document uploads, return a job ID, process asynchronously. Synchronous processing blocks and times out for large files. | Complexity: Medium | v1
- **Job status polling endpoint** — Query ingestion job status by job ID. Needed because ingestion is async. | Complexity: Low | v1
- **Search endpoint** — Accept query + filters + domain, return ranked results. The primary read path. | Complexity: Low | v1
- **Domain management endpoints** — CRUD for domains over REST. Needed by admin UI and any programmatic domain setup. | Complexity: Low | v1
- **Health / readiness endpoints** — `/health` and `/ready` for load balancers and orchestration. Required for Docker Compose and Kubernetes deployments. | Complexity: Low | v1
- **Structured error responses** — Consistent JSON error format (code, message, detail). Without this, clients cannot handle errors reliably. | Complexity: Low | v1
- **API versioning** — Version prefix (`/v1/`) from day one. Retrofitting versioning is painful. | Complexity: Low | v1

#### Frontend (Web UI)

- **Login / auth flow** — Redirect to Keycloak, handle callback, store token, redirect to app. Required to enter the platform. | Complexity: Medium | v1
- **Domain browser** — List accessible domains with counts and metadata. Entry point for all users. | Complexity: Low | v1
- **Search interface** — Input field, filters panel, results list with snippets. Primary daily-use interface. | Complexity: Medium | v1
- **Document detail view** — View extracted text, metadata, and source information for a single document. | Complexity: Low | v1
- **Admin panel — domain management** — UI for creating/editing/deleting domains, assigning access. | Complexity: Medium | v1
- **Admin panel — ingestion sources** — UI for configuring and monitoring ingestion sources. | Complexity: Medium | v1
- **Ingestion status dashboard** — Real-time view of ingestion jobs via WebSocket notifications. | Complexity: Medium | v1

#### Infrastructure and Operations

- **Docker Compose deployment** — Full stack runnable locally and in staging with a single command. | Complexity: Medium | v1
- **Environment configuration** — All secrets and configuration via environment variables (12-factor). | Complexity: Low | v1
- **Logging** — Structured logs (JSON) for all services. Required to diagnose production issues. | Complexity: Low | v1

---

### Differentiators

*(Unchanged from prior milestone — see original document)*

### Anti-Features (v1.0)

*(Unchanged from prior milestone — see original document)*

### Feature Dependencies

*(Unchanged from prior milestone — see original document)*

---

---

## v1.1 Addendum: Visual Ontology Editor

**Scope:** Embedded canvas graph editor launched from the domain card (ontology icon), plus the shared CanvasToolbox component and the Domain Edit modal.

**Context:** This editor is not a standalone ontology tool like Protégé or WebOWL. It is a lightweight concept-map editor embedded inside a domain management UI. The bar for completeness is set by tools like Miro's "mind map" mode, Notion's database diagram, or Figma's simple shape/connection tools — not by academic ontology editors or full graph databases.

---

### Table Stakes: Node Operations

Features users expect in any canvas graph editor. Missing these makes the editor feel broken or unusable.

| Feature | Why Expected | Complexity | Notes |
|---------|--------------|------------|-------|
| Create node via double-click on empty canvas | Universal gesture in graph tools (Miro, draw.io, Lucidchart all use this) | Low | Alternatively: drag from a "New Node" button in the toolbox. Double-click is more discoverable. |
| Drag node to reposition | Nodes that cannot be moved are a broken canvas. This is a base expectation. | Low | Requires pointer-down + move detection on the node element; stop propagation from canvas pan. |
| Select node with single click | Selection precedes deletion, editing, or edge creation. Required for any operation. | Low | Highlight selected node with a ring/glow in primary color (`#0058bc`). |
| Delete selected node via Delete/Backspace key | Standard keyboard shortcut across all graph tools. Muscle memory for users. | Low | Must also remove edges connected to the deleted node (orphan-free cleanup). |
| Inline label edit on double-click of existing node | Fastest path to rename. Confirmed table stakes in Miro, Lucidchart, Figma, and draw.io. | Low | `contenteditable` or an input overlay on the node; commit on Enter/blur. |
| Node type field (plain text or small enum: Concept, Entity, Process, Term) | Ontologies are typed; even simple tools like CmapTools expose node type. Without it you have unnamed blobs. | Medium | Store as a string; show as a small label below the node name. No need for a type system — free-text or a short enum is sufficient. |
| Node description (optional, shown in a detail panel or tooltip on hover) | Users want to annotate nodes with context without cluttering the canvas. | Medium | Render in a floating side panel or popover when node is selected, not directly on the node. |
| Node color coding (pick from a palette of 6-8 preset colors) | Color is the primary visual grouping mechanism on any concept map. Even the simplest tools (Google Slides diagrams) offer this. | Low | Use the design system palette: primary, secondary, tertiary, error, plus 3-4 neutrals. No full color picker needed — a swatch row is sufficient. |

---

### Table Stakes: Edge/Relation Operations

| Feature | Why Expected | Complexity | Notes |
|---------|--------------|------------|-------|
| Draw edge by dragging from a node's connection point to another node | This is the universal graph-editor gesture. Every tool from draw.io to React Flow to Miro uses drag-from-port. | Medium | Show a connection port (small circle) on node hover; drag creates a temporary "ghost" edge that snaps to the nearest node on release. |
| Directed edge (arrow showing relationship direction) | Ontology relations are directed: "A relates-to B" is not the same as "B relates-to A". Arrow at target end is standard. | Low | SVG arrow marker at the target end of the edge path. |
| Edge label (inline text on the edge, e.g. "is a", "has part", "relates to") | Without labels, edges convey no semantic meaning — you just have a connected graph with no ontological content. This is the whole point of an ontology editor. | Medium | Small text centered on the edge path (SVG `<text>` element). Click the label to edit inline. |
| Delete edge (click edge to select, then Delete key or a trash icon) | Edges that cannot be removed make the graph unusable. | Low | Edge selection requires a click target slightly wider than the visible path (invisible wider hit area). |
| Self-loop prevention (block drawing an edge from a node to itself) | Meaningless in this domain and confusing to users. | Low | Validate source ≠ target on edge drop. |

---

### Table Stakes: Canvas Navigation

| Feature | Why Expected | Complexity | Notes |
|---------|--------------|------------|-------|
| Pan canvas by dragging on empty space | Every infinite-canvas tool pans by drag. Without this, the canvas is a fixed viewport. | Low | `mousedown` on canvas background (not on a node) initiates pan; update `transform: translate()` on `mousemove`. |
| Zoom In / Zoom Out (Toolbox buttons + mouse wheel) | Zoom is required as soon as the graph has more than ~5 nodes. Users expect both scroll-to-zoom and explicit buttons. | Low | Apply `transform: scale()` centered on the canvas midpoint. Toolbox buttons trigger fixed step increments (e.g., 25%). |
| Fit to Window / Fit All (Toolbox button) | Users lose nodes off-screen and need to reset the view. This is the most commonly used canvas reset in all graph tools. | Low | Calculate the bounding box of all nodes, then set scale and translate to fit with a small margin. |
| Snap to Grid (Toolbox toggle) | Snap-to-grid makes layouts cleaner when placing nodes. In graph editors (unlike grid editors), this means nodes snap to a configurable pixel grid (e.g., 20px) when dropped — not that edges follow grid lines. Confirmed behavior in draw.io, Miro, and Lucidchart. | Low | On node drag-end, round `x` and `y` to the nearest grid multiple. No visual grid lines required unless explicitly requested. Grid lines are optional visual aid; snapping behavior is the functional feature. |
| Zoom level indicator (read-only, e.g. "75%") | Users need to know current zoom to understand scale. Present in virtually all canvas tools. | Low | A small text label in the toolbox, updated reactively. |

**Note on "Snap to Grid" semantics for graph vs. grid editors:**
In a spreadsheet or grid editor, "snap to grid" means cells align to fixed rows/columns. In a graph/canvas editor, it means node positions are quantized to a background grid when dropped or dragged — edges connect wherever they are logically, not to grid intersections. The visual grid (dotted or line background) is cosmetic. The CanvasToolbox component should implement the quantized-position behavior; the visual grid dots are optional and should default to off.

---

### Table Stakes: Persistence

| Feature | Why Expected | Complexity | Notes |
|---------|--------------|------------|-------|
| Explicit "Save" button with loading state | Graph editors embedded in management UIs (not standalone design tools like Figma) use explicit save. Users editing an ontology definition are performing a deliberate, consequential action. Auto-save is appropriate for notes and documents, not for schema-like data. | Low | Save button in the editor header or toolbox. `PUT /v1/domains/:id/ontology`. Disable during save; show spinner. |
| Load existing ontology on editor open | Reopening the editor must restore the previously saved graph exactly. Without this, every session starts from scratch. | Low | `GET /v1/domains/:id/ontology` on mount. Render saved nodes and edges. Show empty-canvas placeholder if no ontology exists yet. |
| Unsaved changes warning (optional but valuable) | Alert the user if they close the editor with unsaved changes. Prevents accidental data loss. | Low | `beforeunload` event or a modal prompt before route/view change if `isDirty` is true. |

**Save UX verdict:** Use an explicit Save button, not auto-save. Reasons:
1. This is schema/taxonomy data that affects how documents are classified — accidental partial saves are dangerous.
2. The existing domain management UI (Create Domain form) uses explicit save — consistency matters.
3. The backend API is PUT-based (full replacement), not patch-based (incremental changes), so partial auto-saves would require careful debouncing logic that adds complexity for little value.
4. An explicit button gives the user a clear mental model: "I am committing this structure."

---

### Differentiators: Visual Ontology Editor

Features that would make this editor stand out without being expected by default. Build after table stakes are solid.

| Feature | Value Proposition | Complexity | Notes |
|---------|-------------------|------------|-------|
| Visual grid background (subtle dots or lines) | Makes layout alignment easier and the canvas feel intentional. Not required for functional snapping. | Low | CSS `background-image: radial-gradient(circle, #ccc 1px, transparent 1px)` at grid spacing. Toggle with snap. |
| Multi-select (Shift+click or drag-to-select rectangle) | Lets users move or delete multiple nodes at once. Valuable when reorganizing large ontologies. | Medium | Box-select: track drag on empty canvas, select all nodes whose bounding box intersects. Hold Shift for additive selection. |
| Minimap (small thumbnail of full graph in corner) | Navigation aid for large graphs. Familiar from draw.io, Miro, React Flow. | Medium | Rendered as a scaled-down SVG overlay showing node positions. Click to jump viewport. Only worthwhile when the ontology has 15+ nodes. |
| Undo / Redo (Ctrl+Z / Ctrl+Y) | Users restructure ontologies and make mistakes. Undo is expected in creative tools but not always in embedded admin forms. | High | Requires maintaining an operation history stack in the Pinia store. Every node/edge mutation pushes a snapshot or delta. Memory-bound: keep last N=50 states. |
| Node icon selection (pick from a small set of semantic icons: document, process, entity, concept) | Adds visual differentiation beyond color alone. Useful when printing or screenshotting the ontology. | Medium | A small icon library (8-12 icons from `lucide-vue-next`) rendered inside the node shape. |
| Export as PNG or SVG | Users want to share or document their ontology outside the platform. | Medium | Serialize the canvas to a static SVG; use `canvas.toBlob` for PNG. Available via a button in the toolbox. |
| Curved vs. straight edges toggle | Curved edges (Bezier or orthogonal) reduce visual crossings in dense graphs; straight edges are simpler for sparse graphs. | Low | A simple toggle per-graph or per-edge. Store `edgeType: 'straight' | 'curved'` in the ontology model. |

---

### Anti-Features: Visual Ontology Editor

Features to deliberately exclude. Each adds significant complexity with marginal value for this specific use case.

| Anti-Feature | Why Avoid | What to Do Instead |
|--------------|-----------|-------------------|
| OWL/RDF export or semantic web compatibility | This is a concept-map tool for organizing domain knowledge, not an academic ontology. OWL introduces class hierarchies, property axioms, and reasoners — a completely different product. No user in a KM platform admin UI needs Turtle serialization. | Persist as plain JSON nodes/edges; that is sufficient for all downstream uses in this platform. |
| Automatic layout algorithms (e.g., Dagre, ELK force-directed) | Auto-layout destroys manually arranged positions every time it runs. Users lose spatial memory. Auto-layout tools are appropriate for generated graphs (e.g., a dependency graph), not for intentionally authored ontologies. | Let users arrange manually with snap-to-grid. If requested later, offer it as a one-time "Reset layout" option, not on every edit. |
| Real-time collaborative editing (multi-user cursors) | Requires CRDTs or OT, WebSocket synchronization of cursor positions, conflict resolution, and a "who is editing" presence indicator. An order of magnitude more complex than single-user. There is no stated requirement for concurrent editing. | Single-user editing. The last explicit Save wins. Add a "locked by user X" indicator only if concurrent access becomes a real problem. |
| Hierarchical / tree layout mode | Ontologies are graphs, not trees. Forcing a hierarchy defeats the purpose of an ontology (which can have many-to-many and cyclic relations). A tree layout mode would constrain valid ontology structures. | Let users draw edges freely in both directions. |
| Node grouping / containers (subgraphs that visually contain other nodes) | Grouping requires hit-testing against nested bounding boxes, drag-in/drag-out behavior, resize handles on the group, and group-aware selection. Significant implementation complexity. | Use color coding and edge clusters to visually communicate groupings without nested containers. |
| Edge styling per-relationship type (dashes, colors, thickness per edge) | Fine-grained edge styling bloats the property panel, introduces choice paralysis, and creates visual inconsistency across ontologies. The label on the edge already conveys the relationship type semantically. | One edge style for all edges (directed, thin, neutral color). Labels carry the semantic distinction. |
| Property/attribute panel on nodes beyond name/type/description/color | OWL-style property ranges, cardinality constraints, domain/range declarations — these belong in a full ontology editor, not an embedded concept-map. They would never be consumed by the search or ingestion pipeline. | Keep node metadata to: name (required), type (optional enum), description (optional text), color (optional preset). |
| Version history of the ontology | Tracking diffs between saved versions is a documentation/audit feature. It requires storing multiple snapshots server-side, a UI to compare versions, and a rollback operation. The operational value in an internal KM tool is low. | Single latest version persisted via PUT. If history is needed, it belongs in source control or backup procedures, not in the UI. |
| Import from external ontology formats (OBO, SKOS, JSON-LD) | Importing foreign ontology formats requires parsers for each format, a mapping step to the internal model, and conflict resolution for overlapping node names. More work than building the ontology from scratch for most users. | Manual construction only. If import is genuinely needed, implement a separate CLI migration tool, not a UI uploader. |
| Full-screen modal vs. dedicated route for the editor | Opening the ontology editor in a full-page modal (overlaying the domain management view) is tempting for simplicity, but graph editors require maximum vertical and horizontal space. A modal constrained by viewport margins (typically 80-90% of screen) will make the canvas feel cramped as soon as the ontology has 8+ nodes. | Navigate to a dedicated route or view (e.g., a new `view = 'ontology'` state in domains-ui, full-width with the CanvasToolbox integrated). |

---

### Feature Dependencies: v1.1

```
Domain card (existing)
  └─ Ontology icon button on card (new: left of creation date)
      └─ Opens ontology editor view (full-width canvas)
          ├─ CanvasToolbox component (shared, embedded in editor)
          │   ├─ Zoom In / Zoom Out
          │   ├─ Fit to Window
          │   ├─ Snap to Grid toggle
          │   └─ Zoom level indicator (read-only)
          ├─ Node CRUD on canvas
          │   ├─ Create (double-click empty canvas)
          │   ├─ Select (single click)
          │   ├─ Move (drag)
          │   ├─ Edit label (double-click node)
          │   ├─ Edit type/description/color (selected node detail panel)
          │   └─ Delete (Delete/Backspace key)
          ├─ Edge CRUD on canvas
          │   ├─ Create (drag from connection port on node)
          │   ├─ Label (click label area → inline edit)
          │   ├─ Select (click edge)
          │   └─ Delete (Delete/Backspace key)
          ├─ Canvas pan/zoom
          │   ├─ Pan (drag on empty canvas)
          │   ├─ Zoom (mouse wheel + toolbox buttons)
          │   └─ Fit (toolbox button)
          └─ Save
              └─ PUT /v1/domains/:id/ontology (backend API)
                  └─ GET /v1/domains/:id/ontology (load on mount)

Domain card (existing)
  └─ Click domain card → opens Edit Domain modal (new behavior)
      └─ Reuses Create Domain form (pre-populated)
          └─ Title changes to "Editar Dominio"
              └─ Save via PUT /v1/domains/:id (already in store.updateDomain)
```

**Key integration note:** `store.updateDomain()` already exists in `useDomainsStore` (`domains.ts`). The Edit modal is a UI-only addition — no new store actions required, only routing/view-state changes and a mode prop to distinguish create vs. edit on the form component.

---

### Ontology Data Model (Backend Contract)

The frontend editor needs a wire format to save/load. Keep it minimal:

```json
{
  "nodes": [
    {
      "id": "uuid",
      "label": "Machine Learning",
      "type": "Concept",
      "description": "Optional free-text annotation",
      "color": "#0058bc",
      "x": 120,
      "y": 240
    }
  ],
  "edges": [
    {
      "id": "uuid",
      "source": "node-uuid-A",
      "target": "node-uuid-B",
      "label": "is a subfield of"
    }
  ]
}
```

Store this as a JSONB column on the `domains` table in PostgreSQL (add column `ontology_graph JSONB DEFAULT NULL`). No separate `ontologies` table needed at this scale — the ontology is a per-domain singleton. `GET /v1/domains/:id/ontology` returns this object; `PUT /v1/domains/:id/ontology` replaces it entirely.

---

### Confidence Assessment

| Area | Confidence | Basis |
|------|------------|-------|
| Node operations table stakes | HIGH | Consistent across draw.io, Miro, Lucidchart, React Flow docs, and CmapTools — all training-data verified, highly stable UX conventions |
| Edge operations table stakes | HIGH | Same — drag-from-port is universal; arrow+label is the minimum for a directed graph |
| Canvas navigation table stakes | HIGH | Pan/zoom/fit are universal — all major canvas tools implement these identically |
| Snap-to-grid semantics (graph vs. grid editors) | HIGH | The distinction between positional quantization and grid-line following is well-established in the draw.io and Figma documentation |
| Explicit save vs. auto-save recommendation | MEDIUM-HIGH | Rationale is based on UX principles for schema-like data and consistency with existing form patterns; no direct user research on this codebase |
| Anti-features list | HIGH | Each is grounded in a specific complexity argument, not preference |
| Ontology data model (JSONB) | MEDIUM | Appropriate for a per-domain singleton; would need reassessment if cross-domain ontology linking becomes a requirement |
| Vue 3 + SVG for canvas implementation (no separate graph library) | MEDIUM | Training data suggests VueFlow is the dominant Vue 3 graph library (port of React Flow); a hand-rolled SVG canvas is lower dependency but higher implementation effort. The recommendation to use VueFlow should be evaluated in the STACK.md for v1.1. |

---

### Implementation Note: Library vs. Hand-Rolled Canvas

The ontology editor requires a canvas with node-drag, edge-draw, and zoom/pan. Two approaches:

**VueFlow** (`@vue-flow/core`, Vue 3 port of React Flow): Provides nodes, edges, zoom/pan, and minimap out of the box. Reduces implementation effort significantly. Confidence: MEDIUM — this library existed and was actively maintained as of August 2025, but version status should be verified before adopting.

**Hand-rolled SVG canvas**: Full control, zero external dependency, fits within the existing domains-ui micro-frontend without adding a large dependency to the MF bundle. Requires implementing pointer event handling, SVG path calculation for edges, and zoom/pan transforms from scratch. Estimated 2-3x implementation time vs. VueFlow.

**Recommendation:** Verify VueFlow's current status (check npm, GitHub activity) before deciding. If active and compatible with Vue 3.4+ and Vite 5+, use it — the canvas primitives it provides are well-tested and the API is stable. If dormant or incompatible, implement a minimal SVG canvas; the feature set required (no minimap, no auto-layout, ~30-node scale) does not require a full graph library.

This decision belongs in STACK.md for the v1.1 milestone, not here.

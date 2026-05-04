# Architecture Patterns: Domain Edit + Visual Ontology Editor Integration

**Milestone:** v1.1 Domain Intelligence
**Researched:** 2026-05-03
**Confidence:** HIGH — all findings based on direct codebase reading
**Replaces:** Previous general architecture document (see git history for original system overview)

---

## Existing Architecture Baseline

### What Is Already Built (verified from code)

**Frontend — `domains-ui` remote (port 5101)**
- Single `App.vue` with internal view state: `'explorer' | 'create' | 'detail'`
- No sub-components extracted yet — entire UI is one monolithic SFC
- `useDomainsStore` (Pinia) already has `updateDomain` action and `isEditing` ref
- `domainsApi.ts` already has `updateDomain(id, data)` calling `PUT /api/v1/domains/:id`
- `types/index.ts` has `UpdateDomainRequest` already defined
- MF exposure: only `./App` is exposed via `@originjs/vite-plugin-federation`

**Frontend — shell (port 5100)**
- `domainsUi/App` is mounted at `/domains` route as a full-page component
- Shell has no modal layer; each micro-UI owns its own overlay rendering
- `frontend/packages` directory exists but is completely empty — no shared lib infrastructure

**Backend — FastAPI (`api/src`)**
- `PUT /v1/domains/{domain_id}` route already exists in `domains.py` — the edit endpoint is fully implemented
- `DomainUpdate` schema already covers all editable fields (name, description, name_en, description_en, tags, visibility, cover_image)
- `Domain` SQLAlchemy model uses `Column(JSON)` imported from `sqlalchemy` — PostgreSQL stores this as JSONB
- No Alembic setup found — schema is created via `init_db()` using `Base.metadata.create_all`
- No ontology column, model, or route exists yet

---

## Q1: OntologyEditor — Modal Overlay vs. Separate Route

**Decision: Full-screen overlay rendered inside `domains-ui`, controlled by internal view state. Not a shell route.**

### Rationale

The existing view machine in `App.vue` already transitions between `explorer`, `create`, and `detail` without touching the shell router. Adding `'ontology'` as a fourth value to the `View` type union is zero-friction and zero-risk.

A dedicated shell route like `/domains/:id/ontology` would require:
- Shell router to know about domain ID parameters (breaks micro-frontend independence)
- Cross-remote navigation (shell must know which remote handles which sub-path)
- Shell to forward the domain ID to the remote somehow (URL param, prop, or event bus)

None of that is in place and none of it is warranted for a canvas editor.

The canvas needs to fill the available viewport. A `position: fixed; inset: 0; z-index: 200` overlay inside domains-ui achieves a full-screen appearance within the shell layout. The shell layout does not clip fixed-positioned children.

### Implementation Sketch

```
App.vue view state:
type View = 'explorer' | 'create' | 'detail' | 'ontology'

New refs added to App.vue:
const ontologyDomainId = ref<string | null>(null)

// Ontology icon click in domain card footer:
function openOntology(d: Domain) {
  ontologyDomainId.value = d.id
  view.value = 'ontology'
}

// Close ontology editor:
function closeOntology() {
  ontologyDomainId.value = null
  view.value = 'explorer'
}
```

`OntologyEditor` renders as `<template v-else-if="view === 'ontology'">` — same pattern as `create` and `detail` views. It receives `domainId` as a prop. No routing involved.

---

## Q2: CanvasToolbox — Module Federation Sharing Strategy

**Decision: Keep `CanvasToolbox.vue` inside `domains-ui` for v1.1. Promote to shared npm workspace package when `ingestion-ui` actually needs it. Do NOT create a separate MF remote for it.**

### Rationale

`frontend/packages` is completely empty. No shared lib infrastructure exists. Creating `frontend/libs/canvas-toolbox` as a Vite lib + new MF remote adds:
- A new port (e.g. 5105) that must be running for `domains-ui` to build
- A new entry in `shell/vite.config.ts` `remotes` block
- Build order coupling: shell preview fails if canvas-toolbox remote is not running

For a single consumer in v1.1, that overhead is unjustified.

The correct promotion path when `ingestion-ui` needs it:
1. Create `frontend/packages/canvas-toolbox/` as a Vite lib project
2. Add `"workspaces": ["packages/*", "apps/*"]` to `frontend/package.json`
3. Both `domains-ui` and `ingestion-ui` add `"canvas-toolbox": "*"` to their `package.json` dependencies
4. The component is bundled into each remote at build time — no extra MF remote, no extra server

NPM workspace packages are bundled locally, not loaded at runtime via MF. This is the right pattern for utility UI components. MF remotes are for full application surfaces, not shared UI primitives.

### v1.1 File Location

```
frontend/apps/domains-ui/src/
  components/
    canvas/
      CanvasToolbox.vue    ← lives here for now
      OntologyEditor.vue
```

**Document the CanvasToolbox props contract now** to make future extraction mechanical:
```typescript
// Props that CanvasToolbox must expose (do not expand beyond this for v1.1)
interface CanvasToolboxProps {
  zoom: number          // current zoom level (1.0 = 100%)
  snapEnabled: boolean
}
interface CanvasToolboxEmits {
  'zoom-in': []
  'zoom-out': []
  'toggle-snap': []
  'fit-to-window': []
}
```

---

## Q3: Ontology Data Storage

**Decision: Add an `ontology` JSON column directly to the `domains` table in `models/base.py`.**

### Rationale

The `Domain` model already uses `Column(JSON)` from SQLAlchemy. PostgreSQL stores SQLAlchemy `JSON` columns as JSONB natively when using the `postgresql+asyncpg` driver. Adding one nullable column to the existing model is the minimal-change option.

A separate `ontology` table adds a JOIN for zero benefit — there is a strict 1:1 relationship between domain and ontology. Ontology data is domain-scoped and has no independent lifecycle.

JSONB is appropriate because:
- The graph structure (nodes + edges) is document-shaped, not relational
- Schema will evolve as node types are added (color, icon fields, custom types)
- Null by default — domains without ontologies carry no overhead
- GIN indexing on JSONB is available if cross-domain ontology querying is ever needed

### Column to Add

```python
# In api/src/models/base.py — Domain class
ontology = Column(JSON, nullable=True, default=None)
```

### Ontology Graph Schema (JSONB shape)

```json
{
  "nodes": [
    {
      "id": "uuid-string",
      "label": "Concept Name",
      "type": "concept",
      "description": "Optional description",
      "color": "#0058bc",
      "x": 120.0,
      "y": 80.0
    }
  ],
  "edges": [
    {
      "id": "uuid-string",
      "source": "node-uuid",
      "target": "node-uuid",
      "label": "relates-to"
    }
  ]
}
```

### Migration Note

`init_db()` calls `Base.metadata.create_all` — adding a column to the model is sufficient for the development database. For a pre-existing production database, an Alembic migration will be needed. No Alembic setup exists in the codebase yet; adding the column to a fresh DB via `create_all` is safe for v1.1.

---

## Q4: New API Routes

**Decision: Add two ontology routes to the existing `domains.py` router. One new service method pair in `domain_service.py`. Five new Pydantic schemas.**

### Routes

```
GET  /v1/domains/{domain_id}/ontology
PUT  /v1/domains/{domain_id}/ontology
```

These sit naturally inside the existing `/domains` prefix router alongside the existing `/{domain_id}/access` sub-routes.

GET uses `require_domain_access` (reader or admin can view). PUT uses `require_domain_admin` (only admins can modify the ontology). This mirrors the existing access management pattern.

Why separate endpoints rather than adding `ontology` to the domain PUT body:
- The ontology payload can be large (many nodes/edges). Keeping it out of the domain PATCH avoids sending large payloads on routine domain metadata edits.
- Future: ontology reads may be cached differently from domain metadata.
- Cleaner API surface — clients can subscribe to ontology changes independently.

### Schemas to Add to `schemas/__init__.py`

```python
class OntologyNode(BaseModel):
    id: str
    label: str
    type: str = "concept"
    description: Optional[str] = None
    color: Optional[str] = None
    x: float = 0.0
    y: float = 0.0

class OntologyEdge(BaseModel):
    id: str
    source: str
    target: str
    label: Optional[str] = None

class OntologyGraph(BaseModel):
    nodes: List[OntologyNode] = []
    edges: List[OntologyEdge] = []

class OntologyResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    domain_id: UUID
    ontology: Optional[OntologyGraph] = None

class OntologySave(BaseModel):
    nodes: List[OntologyNode] = []
    edges: List[OntologyEdge] = []
```

### Service Methods to Add to `domain_service.py`

```python
async def get_ontology(self, domain_id: UUID) -> Optional[dict]:
    domain = await self.get_domain(domain_id)
    if not domain:
        return None
    return domain.ontology  # returns None if never saved

async def save_ontology(self, domain_id: UUID, ontology_data: dict) -> dict:
    domain = await self.get_domain(domain_id)
    if not domain:
        return None
    domain.ontology = ontology_data
    await self.db.commit()
    return domain.ontology
```

### Route Handlers to Add to `domains.py`

```python
@router.get(
    "/{domain_id}/ontology",
    response_model=OntologyResponse,
    summary="Get domain ontology",
)
async def get_domain_ontology(
    domain_id: UUID,
    user: UserInToken = Depends(require_domain_access),
    db: AsyncSession = Depends(get_db)
):
    service = DomainService(db)
    ontology = await service.get_ontology(domain_id)
    if ontology is None:
        raise HTTPException(status_code=404, detail="Domain not found")
    return OntologyResponse(domain_id=domain_id, ontology=ontology)

@router.put(
    "/{domain_id}/ontology",
    response_model=OntologyResponse,
    summary="Save domain ontology",
)
async def save_domain_ontology(
    domain_id: UUID,
    ontology_data: OntologySave,
    user: UserInToken = Depends(require_domain_admin),
    db: AsyncSession = Depends(get_db)
):
    service = DomainService(db)
    saved = await service.save_ontology(domain_id, ontology_data.model_dump())
    if saved is None:
        raise HTTPException(status_code=404, detail="Domain not found")
    return OntologyResponse(domain_id=domain_id, ontology=OntologyGraph(**saved))
```

### BFF Impact

No BFF changes required. The shell's Vite dev server already proxies `'/api': 'http://localhost:3000'` to the BFF, and the BFF already proxies all `/api/v1/*` to the Core API. The new routes `/api/v1/domains/:id/ontology` will pass through transparently.

The `domainsApi.ts` client will call `/api/v1/domains/${domainId}/ontology` — matching the existing pattern where all other calls go through `/api/v1/domains`.

---

## Q5: Recommended Build Order

### Dependency Graph

```
Domain Edit Modal
  └── Depends on: existing PUT /v1/domains/:id (already exists)
  └── No new backend work

CanvasToolbox
  └── Depends on: nothing (pure UI component)

Backend Ontology (column + routes)
  └── Depends on: Domain model (exists)
  └── Blocks: OntologyEditor persistence

OntologyEditor
  └── Depends on: CanvasToolbox + GET/PUT /v1/domains/:id/ontology
```

### Step 1 — Domain Edit Modal (Frontend only, no backend changes)

**What:** Extract the create form into a reusable `DomainForm.vue` component. Build `DomainEditModal.vue` as a glassmorphism overlay containing `DomainForm` pre-populated with existing domain data. Add ontology icon to domain card footer (icon visible; click opens `view = 'ontology'` with a placeholder stub).

**Why first:** Zero backend risk. The store, API client, and backend PUT endpoint all exist. Only the UI layer is missing. This is the fastest value delivery and validates the form extraction refactor before ontology work begins.

**The key insight:** The existing create form is a 700-line monolith in `App.vue`. Extracting it now (required for the edit modal) also simplifies the file and makes Step 3 easier.

**Files modified:**
- `App.vue` — remove inline form template, add `DomainEditModal` usage, add ontology icon to card footer
- New: `src/components/DomainForm.vue` — extracted form, accepts `mode: 'create' | 'edit'` and `initialData?: Domain`
- New: `src/components/DomainEditModal.vue` — fixed overlay wrapping DomainForm in edit mode

**View state change:** No new view state for the edit modal. It renders as a fixed overlay on top of the current view, controlled by `editModalDomainId: ref<string | null>(null)`.

### Step 2 — Backend Ontology Column + Routes

**What:** Add `ontology` JSON column to `Domain` model. Add five Pydantic schemas. Add two service methods. Add two routes to `domains.py`.

**Why second:** Required for ontology persistence. Self-contained backend work. Frontend Step 3 can mock data locally while backend is being built.

**Files modified:**
- `api/src/models/base.py` — add `ontology = Column(JSON, nullable=True, default=None)`
- `api/src/schemas/__init__.py` — add `OntologyNode`, `OntologyEdge`, `OntologyGraph`, `OntologyResponse`, `OntologySave`
- `api/src/services/domain_service.py` — add `get_ontology`, `save_ontology`
- `api/src/api/domains.py` — add two route handlers + import new schemas

### Step 3 — OntologyEditor + CanvasToolbox (depends on Step 2)

**What:** Build `CanvasToolbox.vue` (Zoom In/Out, Snap to grid, Fit to window toolbar). Build `OntologyEditor.vue` (SVG/canvas for nodes and edges, drag positioning, node/edge CRUD). Wire GET/PUT `/v1/domains/:id/ontology` through `domainsApi.ts` and new store actions.

**Why last:** Highest complexity (canvas pointer events, SVG edge routing, node rendering). Depends on Step 2 for persistence. Step 2 can be in-progress while Step 3 is prototyped against local Pinia state.

**Files modified:**
- New: `src/components/canvas/CanvasToolbox.vue`
- New: `src/components/canvas/OntologyEditor.vue`
- `src/services/domainsApi.ts` — add `getOntology(domainId)`, `saveOntology(domainId, graph)`
- `src/stores/domains.ts` — add `ontology`, `isLoadingOntology`, `isSavingOntology` refs; add `fetchOntology`, `saveOntology` actions
- `src/types/index.ts` — add `OntologyNode`, `OntologyEdge`, `OntologyGraph` types
- `App.vue` — replace ontology stub with `OntologyEditor` component

---

## Complete Component Map

### New Components

| Component | Location in `domains-ui/src` | Responsibility |
|-----------|------------------------------|----------------|
| `DomainForm.vue` | `components/DomainForm.vue` | Reusable create/edit form, accepts `mode` + `initialData` |
| `DomainEditModal.vue` | `components/DomainEditModal.vue` | Fixed overlay containing DomainForm in edit mode |
| `CanvasToolbox.vue` | `components/canvas/CanvasToolbox.vue` | Zoom/snap/fit toolbar for canvas editors |
| `OntologyEditor.vue` | `components/canvas/OntologyEditor.vue` | Full-screen canvas editor for ontology nodes and edges |

### Modified Frontend Files

| File | Change |
|------|--------|
| `src/App.vue` | Remove inline form, add modal + ontology icon, add `'ontology'` view state |
| `src/types/index.ts` | Add `OntologyNode`, `OntologyEdge`, `OntologyGraph` |
| `src/services/domainsApi.ts` | Add `getOntology`, `saveOntology` |
| `src/stores/domains.ts` | Add ontology state + `fetchOntology`/`saveOntology` actions |

### Modified Backend Files

| File | Change |
|------|--------|
| `api/src/models/base.py` | Add `ontology = Column(JSON, nullable=True)` to `Domain` |
| `api/src/schemas/__init__.py` | Add 5 ontology schemas |
| `api/src/services/domain_service.py` | Add `get_ontology`, `save_ontology` |
| `api/src/api/domains.py` | Add GET + PUT `/{domain_id}/ontology` routes |

### Unchanged (No Work Required)

| Item | Why unchanged |
|------|---------------|
| `shell/vite.config.ts` | No new remotes, no new routes |
| `shell/src/router/index.ts` | No new shell routes |
| `domains-ui/vite.config.ts` | No new MF exposures needed |
| BFF (NodeJS) | Existing proxy config covers new routes transparently |
| `frontend/packages/` | Empty; CanvasToolbox stays in domains-ui for v1.1 |

---

## Design System Integration Points

The Luminous Knowledge design system (`DESIGN.md`) defines:
- Surface: `#f9f9ff`, containers: `#ecedf9` / `#e6e8f3`
- Primary: `#0058bc`, on-primary: `#ffffff`
- Outline: `#717786`, outline-variant: `#c1c6d7`

**DomainEditModal overlay backdrop:** `background: rgba(24, 28, 35, 0.4)` with `backdrop-filter: blur(20px)`. The modal card uses `background: #ffffff; border-radius: 16px` — matching the existing `.form-card` pattern already in App.vue.

**Ontology icon on domain card:** Position in `.card-footer` row between resource count and date. Use `cursor: pointer; color: var(--outline)` default, `color: var(--primary)` on hover. SVG graph icon (3 nodes connected).

**OntologyEditor canvas background:** `--surface-container: #ecedf9`. Node cards follow `.domain-card` pattern: white fill, `border: 1px solid #c1c6d7`, `border-radius: 12px`, `box-shadow: 0 1px 4px rgba(0,0,0,0.06)`.

**CanvasToolbox pill:** `background: rgba(255,255,255,0.85); backdrop-filter: blur(10px); border-radius: 10px; border: 1px solid #c1c6d7` — consistent with the glassmorphism identity. Position: bottom-center of canvas, `position: absolute; bottom: 16px; left: 50%; transform: translateX(-50%)`.

---

## Confidence Assessment

| Area | Confidence | Basis |
|------|------------|-------|
| Edit modal needs no new backend | HIGH | `updateDomain` verified in store, API client, and `domains.py` |
| Ontology as JSONB column on domains | HIGH | `Column(JSON)` pattern verified in `models/base.py` |
| New routes pattern in `domains.py` | HIGH | Existing access sub-routes verified as template |
| OntologyEditor as internal view state | HIGH | Shell router and MF config verified |
| CanvasToolbox stays internal v1.1 | HIGH | `frontend/packages` confirmed empty |
| Build order (edit first, then backend, then canvas) | HIGH | Dependency graph derived from actual code |
| BFF transparent proxy | HIGH | Shell proxy config verified in `shell/vite.config.ts` |

---

## Sources

All findings derived directly from codebase reading. No external sources required.

- `frontend/apps/domains-ui/src/App.vue` — existing view state machine, card-footer structure
- `frontend/apps/domains-ui/src/stores/domains.ts` — `updateDomain`, `isEditing` already present
- `frontend/apps/domains-ui/src/services/domainsApi.ts` — `updateDomain` method already present
- `frontend/apps/domains-ui/src/types/index.ts` — `UpdateDomainRequest` already defined
- `frontend/apps/domains-ui/vite.config.ts` — MF exposes only `./App`
- `frontend/apps/shell/src/router/index.ts` — shell routes, MF remote loading pattern
- `frontend/apps/shell/vite.config.ts` — MF host config, proxy config, remotes list
- `frontend/package.json` — workspace root, no workspace packages defined
- `frontend/packages/` — confirmed empty
- `api/src/models/base.py` — `Domain` model, `Column(JSON)` pattern confirmed
- `api/src/api/domains.py` — `PUT /{domain_id}` already implemented; access sub-routes as pattern
- `api/src/services/domain_service.py` — `update_domain` service method as pattern
- `api/src/schemas/__init__.py` — existing schema patterns
- `api/src/db/database.py` — `create_all` initialization; no Alembic migrations present
- `DESIGN.md` — Luminous Knowledge color tokens

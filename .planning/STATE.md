# Project State

## Project Reference

See: .planning/PROJECT.md (updated 2026-05-02)

**Core value:** Any authenticated user can find relevant knowledge within authorized domains in seconds, using semantic or hybrid search over indexed documents
**Current focus:** Phase 9 — MCP integration

## Current Position

Phase: Phase 9
Plan: TBD
Status: Ready to start
Last activity: 2026-05-09 — Phase 8 (Admin and API keys) COMPLETED

### Phase 8 Progress

| Plan | Status | Notes |
|------|--------|-------|
| Plan 08-01: Admin UI + API Key Management | ✅ Complete | Frontend admin-ui MF remote (port 5104), API key CRUD with SHA-256, rate limiting (per-key + Redis middleware), domain access management |

Progress: [██████████] 100%

## Performance Metrics

**Velocity:**
- Total plans completed: 8
- Average duration: -
- Total execution time: 0 hours

**By Phase:**

| Phase | Plans | Total | Avg/Plan |
|-------|-------|-------|----------|
| 06 | 3 | 3 | - |
| 07 | 4 | 4 | - |
| 08 | 1 | 1 | - |

**Recent Trend:**
- Last 5 plans: 08-01, 07-04, 07-03, 07-02, 07-01
- Trend: Stable

*Updated after each plan completion*

## Accumulated Context

### Decisions

Decisions are logged in PROJECT.md Key Decisions table.
Recent decisions affecting current work:

- Init: VectorStorePort and EmbeddingPort abstractions must be defined in Phase 1 before any ingestion code (prevents tight-coupling rewrite)
- Init: FastMCP mounts as ASGI sub-app on Core API — no separate process
- Init: BFF uses HttpOnly session cookies — JWT never exposed to browser JS
- Init: Vue, Pinia, Vue Router declared singleton:true across all Module Federation apps
- Phase 7: bffClient and UI components exposed from shell to all micro-UIs via Module Federation
- Phase 7: Shared WebSocket singleton in shell for all notifications and real-time updates
- Phase 8: API keys stored as SHA-256 hash (never plaintext); plain key returned only once on create
- Phase 8: Two-layer rate limiting: per-key in-memory sliding window (dependencies.py) + global Redis fixed-window middleware
- Phase 8: DomainAccess has UniqueConstraint(user_id, domain_id); grant_access upserts role on duplicate
- Phase 8: MCP server stub mounted at /mcp as ASGI sub-app — ready for Phase 9 implementation

### Pending Todos

None.

### Blockers/Concerns

- [Pre-Phase 9] Pin FastMCP exact version; verify ASGI mount API and SSE vs Streamable HTTP transport against current docs
- [Pre-Phase 9] MCP server stub exists (api/src/mcp_server/); needs full tool implementation (search_knowledge, list_domains)

## Session Continuity

Last session: 2026-05-09
Stopped at: Phase 8 COMPLETE — Admin UI, API keys, domain access management, FEAT4 login page
Resume file: .planning/phases/08-admin-api-keys/08-01-PLAN.md

### Phase 8 Plans

| Plan | Description | Status |
|------|-------------|--------|
| 08-01 | Admin UI + API Key Management | ✅ COMPLETE |

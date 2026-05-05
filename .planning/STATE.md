# Project State

## Project Reference

See: .planning/PROJECT.md (updated 2026-05-02)

**Core value:** Any authenticated user can find relevant knowledge within authorized domains in seconds, using semantic or hybrid search over indexed documents
**Current focus:** Phase 8 — Admin and API keys

## Current Position

Phase: Phase 8
Plan: 08-01
Status: Starting Phase 8
Last activity: 2026-05-04 — Phase 7 (Core micro UIs) COMPLETED

### Phase 7 Progress

| Plan | Status | Notes |
|------|--------|-------|
| Plan 07-01: Search Micro UI | ✅ Complete | Real API integration, highlighting, filters |
| Plan 07-02: Domain Explorer Micro UI | ✅ Complete | Domain list, document browsing, metadata |
| Plan 07-03: Ingestion Status Micro UI | ✅ Complete | WebSocket-powered real-time job updates |
| Plan 07-04: Shell Notifications | ✅ Complete | Global toast and bell notifications via WS |

Progress: [██████████] 100%

## Performance Metrics

**Velocity:**
- Total plans completed: 7
- Average duration: -
- Total execution time: 0 hours

**By Phase:**

| Phase | Plans | Total | Avg/Plan |
|-------|-------|-------|----------|
| 06 | 3 | 3 | - |
| 07 | 4 | 4 | - |

**Recent Trend:**
- Last 5 plans: 07-04, 07-03, 07-02, 07-01, 06-03
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

### Pending Todos

None yet.

### Blockers/Concerns

- [Pre-Phase 2] Keycloak `kmplatform` client readiness: confirm confidential client is configured in realm=Apps with km-admin/km-reader roles and correct redirect URIs
- [Pre-Phase 2] Deployment hostnames needed (bff.kmp.local, shell.kmp.local) before CORS and Keycloak redirect URI config
- [Pre-Phase 3] Verify Gemini text-embedding-004 batch size limits and rate limits before implementing ingestion batching
- [Pre-Phase 3] Verify ChromaDB 0.5 collection API for breaking changes from 0.4
- [Pre-Phase 6] Evaluate @originjs/vite-plugin-federation vs @module-federation/vite current maturity; pin exact version before scaffolding
- [Pre-Phase 9] Pin FastMCP exact version; verify ASGI mount API and SSE vs Streamable HTTP transport against current docs

## Session Continuity

Last session: 2026-05-04
Stopped at: Phase 7 COMPLETE - Search, Domain Explorer, Ingestion Status, Notifications
Resume file: .planning/phases/07-micro-uis/07-04-SUMMARY.md

### Phase 7 Plans

| Plan | Description | Status |
|------|-------------|--------|
| 07-01 | Search Micro UI | ✅ COMPLETE |
| 07-02 | Domain Explorer Micro UI | ✅ COMPLETE |
| 07-03 | Ingestion Status Micro UI | ✅ COMPLETE |
| 07-04 | Shell Notifications | ✅ COMPLETE |

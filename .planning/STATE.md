# Project State

## Project Reference

See: .planning/PROJECT.md (updated 2026-05-02)

**Core value:** Any authenticated user can find relevant knowledge within authorized domains in seconds, using semantic or hybrid search over indexed documents
**Current focus:** Phase 10 — Production hardening

## Current Position

Phase: Phase 10
Plan: TBD
Status: Ready to start
Last activity: 2026-05-09 — Phase 9 (MCP integration) COMPLETED

### Phase 9 Progress

| Plan | Status | Notes |
|------|--------|-------|
| Plan 09-01: FastMCP MCP Server | ✅ Complete | search_knowledge, list_domains, get_domain_info, get_document_status; Streamable HTTP transport; X-API-Key auth middleware; domain scoping via allowed_domains |

Progress: [██████████] 100%

## Performance Metrics

**Velocity:**
- Total plans completed: 9
- Average duration: -
- Total execution time: 0 hours

**By Phase:**

| Phase | Plans | Total | Avg/Plan |
|-------|-------|-------|----------|
| 06 | 3 | 3 | - |
| 07 | 4 | 4 | - |
| 08 | 1 | 1 | - |
| 09 | 1 | 1 | - |

**Recent Trend:**
- Last 5 plans: 09-01, 08-01, 07-04, 07-03, 07-02
- Trend: Stable

## Accumulated Context

### Decisions

- Init: FastMCP mounts as ASGI sub-app on Core API — no separate process
- Init: BFF uses HttpOnly session cookies — JWT never exposed to browser JS
- Phase 7: Shared WebSocket singleton in shell for all notifications
- Phase 8: API keys stored as SHA-256 hash; plain key returned only once on create
- Phase 8: Two-layer rate limiting: per-key in-memory + global Redis middleware
- Phase 9: FastMCP 3.2.4 uses Streamable HTTP (SSE deprecated); transport=mcp.http_app()
- Phase 9: MCP tools are stateless (fresh DB session per call); ContextVar threads auth from middleware
- Phase 9: Rate limiting for MCP handled by main app's RateLimitMiddleware — no duplicate needed

### Pending Todos

None.

### Blockers/Concerns

- [Phase 10] Structured JSON logging needs `trace_id` and `service` fields on all log lines
- [Phase 10] Docker Compose health checks need to be verified for all services
- [Phase 10] End-to-end smoke test: admin login → domain → ingest PDF → search → MCP query

## Session Continuity

Last session: 2026-05-09
Stopped at: Phase 9 COMPLETE — FastMCP server with 4 tools + MCPAuthMiddleware
Resume file: .planning/phases/09-mcp-integration/09-01-PLAN.md

### Phase 9 Plans

| Plan | Description | Status |
|------|-------------|--------|
| 09-01 | FastMCP MCP Server | ✅ COMPLETE |

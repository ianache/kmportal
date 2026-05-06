---
name: Key Architectural Decisions
description: Core design decisions that constrain how the system is built — must not be violated in later phases
type: project
---

**These decisions are locked and affect all future phases.**

| Decision | Rationale |
|----------|-----------|
| `VectorStorePort` and `EmbeddingPort` abstract base classes defined in Phase 1 | Prevents tight-coupling rewrite; no concrete ChromaDB/Gemini imports outside designated adapters |
| FastMCP mounts as ASGI sub-app on Core API | No separate process needed |
| BFF uses HttpOnly session cookies — JWT never exposed to browser JS | Security: prevents XSS token theft |
| Vue, Pinia, Vue Router declared `singleton: true` across all Module Federation apps | Prevents duplicate instances crashing the shell |
| `bffClient` and shared UI components exposed from shell to all micro-UIs via Module Federation | Single source of truth for API communication |
| Shared WebSocket singleton lives in shell | One persistent WS connection; all micro-UIs subscribe to it for real-time events |
| Ollama used for embeddings (with Gemini adapter as fallback) | Local-first embeddings; Gemini for production |
| Collection ID (not collection name) used for ChromaDB operations | Avoids stale-name bugs after collection updates |
| Role Casing: Uppercase `KM_ADMIN`, `KM_MANAGER`, `KM_VIEWER` standardized across all tiers | Prevents authorization failures (403 Forbidden) due to case-sensitivity in RBAC checks |

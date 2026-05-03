---
type: concept
name: 09-01-PLAN.md
created: 2026-05-03T11:25:00Z
updated: 2026-05-03T11:25:00Z
confidence: 0.90
---

# Plan 09-01: FastMCP Server for AI Agent Integration

## Goal
Integrate FastMCP (Model Context Protocol) server to expose knowledge base functionality to external AI agents, mounted as an ASGI sub-app on the Core API.

## Background
Phase 9 implements the AI agent integration layer using FastMCP, following Decision D002 to mount it as an ASGI sub-app within the Core API process. This allows external AI agents (Claude, GPT, etc.) to query the knowledge base using standardized tools.

## Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                    Core API (FastAPI)                       │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────────┐  │
│  │ /v1/domains  │  │ /v1/search   │  │ /mcp (MCP Server)│  │
│  └──────────────┘  └──────────────┘  └──────────────────┘  │
│                                               │             │
│                                    ┌──────────▼──────────┐  │
│                                    │ SSE Endpoint        │  │
│                                    │ /mcp/sse            │  │
│                                    │ /mcp/messages       │  │
│                                    └─────────────────────┘  │
└─────────────────────────────────────────────────────────────┘
                              │
                    ┌─────────▼──────────┐
                    │  AI Agent Clients  │
                    │  (Claude, GPT, etc)│
                    └────────────────────┘
```

## Implementation Steps

### 1. MCP Server (`mcp/server.py`)
Create FastMCP server instance with tools:

**Tools:**
- `search_knowledge(query, domain_ids, top_k, search_mode)` - Search documents
  - semantic, keyword, or hybrid search
  - Returns: chunk_id, document_id, title, content, score, metadata
  
- `list_domains()` - List all knowledge domains
  - Returns: id, name, description, document_count
  
- `get_domain_info(domain_id)` - Get domain details
  - Returns: full domain metadata
  
- `get_document_status(document_id)` - Check ingestion status
  - Returns: status, progress, error_message

### 2. Authentication (`mcp/auth.py`)
API Key authentication middleware:
- Validates X-API-Key header
- Checks API key against database
- Attaches scopes and allowed domains to request state
- Rejects requests with invalid/expired keys

### 3. Integration (`main.py`)
Mount MCP as ASGI sub-app:
```python
mcp_app = get_mcp_app()
mcp_app.add_middleware(MCPAuthMiddleware)
app.mount("/mcp", mcp_app)
```

### 4. Module exports (`mcp/__init__.py`)
Export MCP components for external use.

## API Endpoints

### MCP Endpoints
```
GET  /mcp/sse       - SSE endpoint for real-time communication
POST /mcp/messages  - Message endpoint for tool calls
```

### Authentication
- Header: `X-API-Key: <api_key>`
- API keys managed via `/v1/api-keys` endpoints
- Scopes control access (read, write, admin)
- Domain restrictions supported

## Usage Example

```python
from fastmcp import Client

# Connect to MCP server
client = Client("http://localhost:8000/mcp")

# Authenticate
client.headers["X-API-Key"] = "km_api_..."

# Search knowledge base
results = client.call_tool("search_knowledge", {
    "query": "machine learning best practices",
    "top_k": 5,
    "search_mode": "hybrid"
})

# List domains
domains = client.call_tool("list_domains")
```

## Dependencies
- `fastmcp>=0.4.0` - Already in pyproject.toml
- Existing services: SearchService, DomainService, IngestionService

## Security Considerations
- API key authentication required for all MCP endpoints
- API keys validated against database on each request
- Domain restrictions enforced based on API key configuration
- Rate limiting supported via API key rate_limit field

## Testing
1. Start Core API: `uvicorn main:app --reload`
2. Create API key via admin UI or `/v1/api-keys`
3. Connect MCP client to `http://localhost:8000/mcp`
4. Test tool calls with valid API key

## Success Criteria
- [x] MCP server mounted at `/mcp`
- [x] API key authentication working
- [x] search_knowledge tool functional
- [x] list_domains tool functional
- [x] get_domain_info tool functional
- [x] get_document_status tool functional
- [x] SSE endpoint accessible
- [x] Proper error handling and validation

## References
- Decision D002: FastMCP mounts as ASGI sub-app
- FastMCP documentation: https://github.com/jlowin/fastmcp
- MCP Protocol: https://modelcontextprotocol.io/

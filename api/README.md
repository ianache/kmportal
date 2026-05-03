# Knowledge Management Center - Core API

Python FastAPI application providing REST API for the knowledge management platform.

## Architecture

This service follows **Clean Architecture** principles with **Ports & Adapters** pattern:

```
┌─────────────────────────────────────┐
│           API Layer                 │
│    (Routers, Pydantic Models)       │
├─────────────────────────────────────┤
│         Service Layer               │
│    (Business Logic, Domain)         │
├─────────────────────────────────────┤
│          Port Interfaces            │
│   (VectorStorePort, EmbeddingPort)  │
├─────────────────────────────────────┤
│         Adapter Implementations     │
│  (ChromaDBAdapter, GeminiAdapter)   │
└─────────────────────────────────────┘
```

**Key Principle**: Business logic only knows about Ports (abstract interfaces). 
Adapters implement these ports using concrete technologies (ChromaDB, Gemini, etc.).
This allows swapping implementations without changing business logic.

## Project Structure

```
api/
├── src/
│   ├── main.py              # FastAPI app entry point
│   ├── ports/               # Abstract interfaces
│   │   ├── __init__.py
│   │   ├── vector_store.py  # VectorStorePort ABC
│   │   └── embedding.py     # EmbeddingPort ABC
│   ├── adapters/            # Concrete implementations
│   │   ├── __init__.py
│   │   ├── vector_store/
│   │   │   ├── __init__.py
│   │   │   └── chroma_db.py     # ChromaDBAdapter
│   │   └── embedding/
│   │       ├── __init__.py
│   │       └── gemini.py        # GeminiAdapter
│   ├── routers/             # API route handlers
│   ├── models/              # Pydantic models
│   └── services/            # Business logic
├── tests/                   # Test suite
├── pyproject.toml          # Project configuration
└── Dockerfile              # Container image
```

## Getting Started

### Prerequisites

- Python 3.13+
- uv (Python package manager)
- Docker & Docker Compose (for infrastructure)

### Installation

1. **Install dependencies**:
```bash
uv sync
```

2. **Set up environment**:
```bash
cp ../.env.example ../.env
# Edit ../.env with your actual values
```

3. **Start infrastructure**:
```bash
cd ..
docker compose up -d postgres mongodb chromadb redis kafka rabbitmq
```

4. **Run the API**:
```bash
uv run uvicorn src.main:app --reload --host 0.0.0.0 --port 8000
```

5. **Verify**:
```bash
curl http://localhost:8000/health
```

### Development

**Run tests**:
```bash
uv run pytest
```

**Run linting**:
```bash
uv run ruff check .
uv run ruff format .
```

**Type checking**:
```bash
uv run mypy src/
```

## API Documentation

Once running, visit:
- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc
- OpenAPI Schema: http://localhost:8000/openapi.json

## Ports & Adapters

### VectorStorePort

Abstract interface for vector databases:

```python
from ports.vector_store import VectorStorePort, Chunk

async def search_documents(
    store: VectorStorePort,
    query_embedding: list[float],
    domain_id: str
):
    results = await store.search(
        collection=domain_id,
        query_vector=query_embedding,
        top_k=10
    )
    return results
```

**Implementations**:
- `ChromaDBAdapter` - ChromaDB (MVP)
- `QdrantAdapter` - Qdrant (v2)

### EmbeddingPort

Abstract interface for embedding providers:

```python
from ports.embedding import EmbeddingPort

async def embed_texts(embedder: EmbeddingPort, texts: list[str]):
    embeddings = await embedder.embed(texts)
    return embeddings
```

**Implementations**:
- `GeminiAdapter` - Google Gemini (MVP)
- `OpenAIAdapter` - OpenAI (v2)
- `OllamaAdapter` - Local embeddings (v2)

## Environment Variables

See `../.env.example` for all required variables. Key ones:

- `POSTGRES_*` - PostgreSQL connection
- `MONGO_*` - MongoDB connection
- `CHROMA_*` - ChromaDB connection
- `REDIS_*` - Redis connection
- `KAFKA_*` - Kafka connection
- `RABBITMQ_*` - RabbitMQ connection
- `GEMINI_API_KEY` - Google AI API key
- `KEYCLOAK_*` - OAuth2/OIDC configuration

## Testing Strategy

- **Unit tests**: Mock ports to test business logic
- **Integration tests**: Use test containers for real databases
- **Contract tests**: Verify adapters implement ports correctly

Example test with mocked port:

```python
import pytest
from unittest.mock import AsyncMock

async def test_search_service():
    mock_store = AsyncMock(spec=VectorStorePort)
    mock_store.search.return_value = [
        SearchResult(chunk_id="1", score=0.9, text="result", metadata={})
    ]
    
    service = SearchService(vector_store=mock_store)
    results = await service.search("query", "domain-123")
    
    assert len(results) == 1
    mock_store.search.assert_called_once()
```

## Contributing

1. Never import concrete implementations (ChromaDB, Gemini) in domain code
2. Always use Ports (abstract interfaces) in business logic
3. Add tests for new adapters
4. Update this README when adding new ports or adapters

## License

MIT

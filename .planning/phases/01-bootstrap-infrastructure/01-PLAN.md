# Plan: Phase 1 — Bootstrap Infrastructure

**Phase:** 1 of 10  
**Status:** In Progress  
**Started:** 2026-05-02  
**Goal:** The full local development environment runs with one command and all services are reachable; port abstractions are in place before any ingestion code is written

---

## Overview

Phase 1 establece la fundación del proyecto. Sin esta fase completa, ninguna otra fase puede avanzar de manera efectiva. El enfoque está en:

1. **Infraestructura como código:** Docker Compose con todas las bases de datos y servicios
2. **Abstracciones críticas:** VectorStorePort y EmbeddingPort para evitar tight coupling
3. **Estructura del monorepo:** Organización clara para equipos paralelos
4. **Configuración externalizada:** Variables de entorno para todo; sin hardcoding

---

## Success Criteria

1. ✅ `docker compose up` inicia PostgreSQL, MongoDB, ChromaDB, Redis, Kafka y RabbitMQ sin pasos manuales
2. ✅ `VectorStorePort` y `EmbeddingPort` existen como clases abstractas; sin imports de ChromaDB o Gemini fuera de adapters
3. ✅ Todas las URLs y credenciales desde variables de entorno; sin hostnames o secrets hardcodeados
4. ✅ Cada servicio expone `/health` retornando 200 con nombre y estado
5. ✅ Estructura de monorepo con paquetes independientes: `api/`, `ingestion/`, `bff/`, `frontend/shell/`, `micro-uis/`

---

## Tasks

### Task 1.1: Monorepo Structure
**Priority:** High  
**Est. Time:** 30 min

Create directory structure:
```
25-KnowledgeManagement/
├── api/                       # Core API Python (FastAPI)
│   ├── src/
│   ├── tests/
│   └── pyproject.toml
├── ingestion/                 # Ingestion worker Python
│   ├── src/
│   ├── tests/
│   └── pyproject.toml
├── bff/                       # Backend for Frontend Node.js
│   ├── src/
│   ├── tests/
│   └── package.json
├── frontend/
│   ├── shell/                 # Module Federation host
│   │   ├── src/
│   │   └── package.json
│   └── micro-uis/             # Micro UIs independientes
│       ├── domains-ui/
│       ├── search-ui/
│       ├── ingestion-ui/
│       └── admin-ui/
├── shared/                    # Shared packages
│   ├── types/                 # TypeScript types
│   └── ui-components/         # Vue components
├── docker-compose.yml
├── .env.example
└── README.md
```

### Task 1.2: Docker Compose Infrastructure
**Priority:** High  
**Est. Time:** 45 min

Create `docker-compose.yml` with:
- **PostgreSQL 16** (port 5432) - metadata, domains, users, API keys
- **MongoDB 7** (port 27017) - raw documents, chunks
- **ChromaDB 0.5** (port 8000) - vector store (MVP)
- **Redis 7** (port 6379) - sessions, pub/sub, cache
- **Kafka + Zookeeper** (port 9092) - message broker
- **RabbitMQ 4** (port 5672 + 15672 UI) - message broker

All services with:
- Health checks
- Persistent volumes
- Environment variables from .env
- Internal networking

### Task 1.3: Environment Configuration
**Priority:** High  
**Est. Time:** 30 min

Create `.env.example` with all required variables:
```bash
# PostgreSQL
POSTGRES_USER=knowledge
POSTGRES_PASSWORD=change_me
POSTGRES_DB=knowledge_db
POSTGRES_HOST=postgres
POSTGRES_PORT=5432

# MongoDB
MONGO_USER=knowledge
MONGO_PASSWORD=change_me
MONGO_DB=knowledge_db
MONGO_HOST=mongodb
MONGO_PORT=27017

# ChromaDB
CHROMA_HOST=chromadb
CHROMA_PORT=8000

# Redis
REDIS_HOST=redis
REDIS_PORT=6379

# Kafka
KAFKA_HOST=kafka
KAFKA_PORT=9092

# RabbitMQ
RABBITMQ_USER=knowledge
RABBITMQ_PASSWORD=change_me
RABBITMQ_HOST=rabbitmq
RABBITMQ_PORT=5672

# Keycloak (external)
KEYCLOAK_URL=https://oauth2.qa.comsatel.com.pe
KEYCLOAK_REALM=Apps
KEYCLOAK_CLIENT_ID=kmplatform

# Gemini API
GEMINI_API_KEY=your_gemini_key
GEMINI_EMBEDDING_MODEL=text-embedding-004
```

### Task 1.4: VectorStorePort Abstraction
**Priority:** High  
**Est. Time:** 60 min  
**Critical:** Esto evita tight coupling con ChromaDB

Create `api/src/ports/vector_store.py`:
```python
from abc import ABC, abstractmethod
from typing import List, Dict, Any, Optional
from dataclasses import dataclass

@dataclass
class Chunk:
    id: str
    text: str
    embedding: Optional[List[float]] = None
    metadata: Dict[str, Any] = None

@dataclass
class SearchResult:
    chunk_id: str
    score: float
    text: str
    metadata: Dict[str, Any]

class VectorStorePort(ABC):
    """
    Abstract port for vector store operations.
    Implementations: ChromaDBAdapter (v1), QdrantAdapter (v2)
    """
    
    @abstractmethod
    async def upsert(self, collection: str, chunks: List[Chunk]) -> None:
        """Insert or update chunks with embeddings"""
        pass
    
    @abstractmethod
    async def search(
        self, 
        collection: str, 
        query_vector: List[float], 
        top_k: int = 10,
        filters: Optional[Dict] = None
    ) -> List[SearchResult]:
        """Semantic search with optional filters"""
        pass
    
    @abstractmethod
    async def delete(self, collection: str, chunk_ids: List[str]) -> None:
        """Delete chunks by IDs"""
        pass
    
    @abstractmethod
    async def create_collection(self, name: str, dimension: int) -> None:
        """Create a new collection with specified embedding dimension"""
        pass
    
    @abstractmethod
    async def delete_collection(self, name: str) -> None:
        """Delete a collection"""
        pass
```

### Task 1.5: EmbeddingPort Abstraction
**Priority:** High  
**Est. Time:** 45 min  
**Critical:** Esto permite cambiar de provider (Gemini → OpenAI → Local)

Create `api/src/ports/embedding.py`:
```python
from abc import ABC, abstractmethod
from typing import List
from dataclasses import dataclass

@dataclass
class EmbeddingConfig:
    model: str
    dimension: int
    batch_size: int = 100

class EmbeddingPort(ABC):
    """
    Abstract port for embedding generation.
    Implementations: GeminiAdapter, OpenAIAdapter, OllamaAdapter
    """
    
    @property
    @abstractmethod
    def dimension(self) -> int:
        """Return the embedding dimension for this provider"""
        pass
    
    @property
    @abstractmethod
    def model_name(self) -> str:
        """Return the model identifier"""
        pass
    
    @abstractmethod
    async def embed(self, texts: List[str]) -> List[List[float]]:
        """
        Generate embeddings for a list of texts.
        Returns list of embedding vectors (dimension per provider)
        """
        pass
    
    @abstractmethod
    async def embed_query(self, text: str) -> List[float]:
        """Generate embedding for a single query"""
        pass
```

### Task 1.6: ChromaDB Adapter (VectorStore Implementation)
**Priority:** Medium  
**Est. Time:** 45 min

Create `api/src/adapters/vector_store/chroma_db.py`:
- Implements VectorStorePort
- Uses chromadb.HttpClient
- One collection per domain
- Stores embedding dimension as collection metadata

### Task 1.7: Gemini Adapter (Embedding Implementation)
**Priority:** Medium  
**Est. Time:** 45 min

Create `api/src/adapters/embedding/gemini.py`:
- Implements EmbeddingPort
- Uses Google Generative AI API
- text-embedding-004 model (768 dimensions)
- Batch processing with configurable size

### Task 1.8: Health Check Endpoints
**Priority:** Medium  
**Est. Time:** 30 min

Create basic FastAPI app structure with:
- `GET /health` → {"service": "api", "status": "healthy", "version": "0.1.0"}
- Similar for other services (ingestion worker, BFF)

### Task 1.9: Documentation
**Priority:** Low  
**Est. Time:** 30 min

Update README.md with:
- Cómo levantar el entorno: `docker compose up`
- Estructura del monorepo
- Cómo ejecutar tests (placeholder)
- Guía de contribución

---

## Dependencies

- Docker & Docker Compose instalados
- Python 3.13+ (para validar sintaxis de adapters)
- Acceso a Gemini API (para Task 1.7)

---

## Risks & Mitigation

| Risk | Impact | Mitigation |
|------|--------|------------|
| ChromaDB 0.5 API breaking changes | High | Verify API before implementing; have migration path ready |
| Gemini API rate limits | Medium | Implement batching; configurable batch_size in EmbeddingPort |
| Port conflicts | Low | Document all ports; use .env for overrides |
| Team unfamiliar with ABC pattern | Medium | Code review required; documentation in port interfaces |

---

## Definition of Done

- [ ] `docker compose up` starts all 6 services successfully
- [ ] All health endpoints return 200
- [ ] VectorStorePort and EmbeddingPort abstractions are code-reviewed
- [ ] No ChromaDB or Gemini imports exist outside adapter directories
- [ ] .env.example is complete and committed
- [ ] Monorepo structure is documented
- [ ] Phase 1 VERIFICATION.md shows all success criteria met

---

**Next Phase:** Phase 2 — Core API Foundation (depends on this phase)

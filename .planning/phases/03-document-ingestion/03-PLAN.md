# Plan: Phase 3 — Document Ingestion Pipeline

**Phase:** 3 of 10  
**Status:** In Progress  
**Started:** 2026-05-03  
**Goal:** Documents submitted from any supported source (local folder, REST, S3, Kafka, RabbitMQ) are chunked, embedded, and stored across all three stores with job-status tracking

**Depends on:** Phase 2 ✅

---

## Overview

Phase 3 implementa el pipeline completo de ingestión de documentos. El flujo es:

1. **Recepción:** Documentos llegan vía REST API, carpeta local, S3, Kafka o RabbitMQ
2. **Registro:** Se crea documento en PostgreSQL y job de ingestión
3. **Procesamiento:** 
   - Extracción de texto (PDF, TXT, DOCX, etc.)
   - Chunking inteligente
   - Generación de embeddings
4. **Almacenamiento:**
   - Metadata en PostgreSQL
   - Contenido raw en MongoDB
   - Embeddings en ChromaDB
5. **Tracking:** Job status (pending → processing → done/failed)

---

## Success Criteria

1. ✅ A PDF uploaded via `POST /v1/ingest` returns a `job_id`; polling `GET /v1/ingest/{job_id}` transitions through `pending → processing → done`; the document's metadata is queryable in PostgreSQL, raw content in MongoDB, and embeddings in ChromaDB
2. ✅ Placing a file in the watched local folder triggers automatic ingestion without manual API call
3. ✅ A document submitted via S3 prefix, Kafka topic, or RabbitMQ queue is ingested and reachable through the same job-status API
4. ✅ A malformed or unprocessable document fails after 5 retries and lands in the Dead Letter Queue, not blocking other documents
5. ✅ Embedding dimension is stored as collection metadata in ChromaDB and as `embedding_dimension` in the PostgreSQL domain record

---

## Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                      Ingestion Sources                       │
├─────────────┬─────────────┬─────────────┬───────────────────┤
│   REST API  │    S3       │   Kafka     │    RabbitMQ       │
│  /v1/ingest │   Events    │   Topic     │     Queue         │
└──────┬──────┴──────┬──────┴──────┬──────┴─────────┬─────────┘
       │             │             │                │
       └─────────────┴─────────────┴────────────────┘
                          │
                          ▼
┌─────────────────────────────────────────────────────────────┐
│                   Ingestion Service                          │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐      │
│  │   Validate   │  │   Extract    │  │    Chunk     │      │
│  │   Document   │→ │    Text      │→ │   Content    │      │
│  └──────────────┘  └──────────────┘  └──────────────┘      │
│         │                                        │          │
│         ▼                                        ▼          │
│  ┌──────────────┐                       ┌──────────────┐    │
│  │ Create Job   │                       │   Embed      │    │
│  │  (Pending)   │                       │   Chunks     │    │
│  └──────────────┘                       └──────────────┘    │
└─────────────────────────────────────────────────────────────┘
                          │
           ┌──────────────┼──────────────┐
           ▼              ▼              ▼
┌─────────────────┐ ┌────────────┐ ┌─────────────────┐
│   PostgreSQL    │ │  MongoDB   │ │    ChromaDB     │
│    (Metadata)   │ │  (Content) │ │  (Embeddings)   │
└─────────────────┘ └────────────┘ └─────────────────┘
```

---

## Tasks

### Task 3.1: Document Processing Pipeline
**Priority:** High  
**Est. Time:** 90 min

Implement document processing steps:

1. **Text Extraction**
   - PDF: PyMuPDF (fitz)
   - TXT: Direct read
   - DOCX: python-docx
   - MD: Direct read
   - Fallback: Plain text extraction

2. **Chunking Strategy**
   ```python
   class ChunkingConfig:
       chunk_size: int = 1000  # tokens/characters
       chunk_overlap: int = 200
       strategy: str = "semantic"  # semantic, fixed, recursive
   ```

3. **Semantic Chunking**
   - Split by paragraphs first
   - Merge small paragraphs
   - Respect sentence boundaries
   - Configurable max chunk size

### Task 3.2: MongoDB Integration
**Priority:** High  
**Est. Time:** 45 min

- Setup Motor (async MongoDB driver)
- Store raw document content
- Store chunks with metadata
- Document versioning support

```python
# MongoDB collections
documents_collection: {
    "_id": ObjectId,
    "document_id": UUID,  # Links to PostgreSQL
    "domain_id": UUID,
    "content": str,  # Full text
    "chunks": [
        {
            "chunk_id": str,
            "text": str,
            "index": int,
            "metadata": dict
        }
    ],
    "metadata": dict,
    "created_at": datetime
}
```

### Task 3.3: Ingestion Service
**Priority:** High  
**Est. Time:** 90 min

Core ingestion business logic:

```python
class IngestionService:
    async def ingest_document(
        self,
        domain_id: UUID,
        source_type: str,
        content: bytes | str,
        metadata: dict
    ) -> IngestionJob:
        # 1. Validate domain exists
        # 2. Create document record (pending)
        # 3. Create ingestion job
        # 4. Queue for processing
        pass
    
    async def process_job(self, job_id: UUID):
        # 1. Extract text
        # 2. Chunk content
        # 3. Generate embeddings
        # 4. Store in ChromaDB
        # 5. Update job status
        pass
```

### Task 3.4: REST API Endpoints
**Priority:** High  
**Est. Time:** 60 min

```
POST /v1/ingest
- Upload document (multipart/form-data)
- Returns job_id

GET /v1/ingest/{job_id}
- Get job status and progress

POST /v1/ingest/text
- Ingest inline text (JSON)

GET /v1/documents/{document_id}/status
- Get document processing status
```

### Task 3.5: Async Workers
**Priority:** High  
**Est. Time:** 90 min

Implement async task processing:

1. **ARQ Worker Setup**
   - Redis as broker
   - Worker pool configuration
   - Job retry logic

2. **Background Tasks**
   ```python
   @job
   async def process_document_job(job_id: UUID):
       # Process with retries
       pass
   ```

3. **Job Status Updates**
   - pending → processing → done
   - Progress tracking (0-100%)
   - Error messages

### Task 3.6: Error Handling & DLQ
**Priority:** Medium  
**Est. Time:** 60 min

1. **Retry Logic**
   - Max 5 retries
   - Exponential backoff
   - Retry on transient errors only

2. **Dead Letter Queue**
   ```python
   class DeadLetterQueue:
       # Store failed jobs
       # Error details
       # Original payload
       # Retry count
   ```

3. **Error Types**
   - Transient: Retry (network, timeout)
   - Permanent: DLQ (malformed, unsupported format)

### Task 3.7: Vector Store Integration
**Priority:** High  
**Est. Time:** 60 min

- Use existing VectorStorePort (ChromaDBAdapter)
- One collection per domain
- Store embedding dimension in collection metadata
- Upsert chunks with embeddings

### Task 3.8: Multi-Source Connectors (MVP)
**Priority:** Medium  
**Est. Time:** 90 min

1. **REST API** (Primary)
   - File upload endpoint
   - Text ingestion endpoint

2. **Local Folder** (Watcher)
   - File system watcher
   - Auto-ingest on file creation

3. **S3, Kafka, RabbitMQ** (Framework)
   - Interface definitions
   - Placeholder implementations
   - Full implementation in Phase 4/5

### Task 3.9: Testing
**Priority:** Medium  
**Est. Time:** 60 min

- Unit tests for chunking
- Integration tests for full pipeline
- Mock embeddings for tests
- Error scenario tests

### Task 3.10: Documentation
**Priority:** Low  
**Est. Time:** 30 min

- API documentation
- Ingestion flow diagrams
- Error handling guide

---

## Data Flow

### Successful Ingestion

```
1. Client → POST /v1/ingest (PDF file)
2. API → Validate auth & domain access
3. API → Create Document record (status: pending)
4. API → Create IngestionJob (status: pending)
5. API → Queue job in Redis/ARQ
6. Worker → Pick up job (status: processing)
7. Worker → Extract text from PDF
8. Worker → Chunk content
9. Worker → Generate embeddings (Gemini)
10. Worker → Store in ChromaDB (domain collection)
11. Worker → Store chunks in MongoDB
12. Worker → Update Document (status: done)
13. Worker → Update Job (status: done, progress: 100%)
14. Client → GET /v1/ingest/{job_id} → status: done
```

### Failed Ingestion (Retry)

```
... (steps 1-9)
10. Worker → Embedding service timeout
11. Worker → Retry (1/5)
12. Worker → Success on retry
... (continue)
```

### Failed Ingestion (DLQ)

```
... (steps 1-7)
8. Worker → Corrupted PDF, extraction fails
9. Worker → Retry (1/5) → Fail
10. Worker → Retry (2/5) → Fail
...
11. Worker → Max retries exceeded
12. Worker → Move to DLQ
13. Worker → Update Job (status: failed)
14. Client → GET /v1/ingest/{job_id} → status: failed
```

---

## Dependencies

- Phase 2 complete ✅
- PyMuPDF (PDF extraction)
- python-docx (DOCX extraction)
- Motor (async MongoDB)
- ARQ (async task queue)
- Redis (job broker)

---

## Definition of Done

- [ ] PDF, TXT, DOCX ingestion working via REST API
- [ ] Document chunked and embedded
- [ ] Metadata in PostgreSQL, content in MongoDB, embeddings in ChromaDB
- [ ] Job status tracking with progress
- [ ] Retry logic with 5 attempts
- [ ] Dead Letter Queue for permanent failures
- [ ] Tests passing
- [ ] Documentation complete
- [ ] Phase 3 VERIFICATION.md

---

**Next Phase:** Phase 4 — Search Engine
# Plan: Phase 4 — Search Engine

**Phase:** 4 of 10  
**Status:** In Progress  
**Started:** 2026-05-03  
**Goal:** Authenticated users can run semantic, hybrid, and filtered searches over documents in their authorized domains and receive ranked, paginated results with relevance scores

**Depends on:** Phase 3 ✅

---

## Overview

Phase 4 implementa el motor de búsqueda que permite a los usuarios encontrar información relevante en sus documentos ingestados. Características principales:

1. **Semantic Search** — Búsqueda por similitud de embeddings
2. **Hybrid Search** — Combinación vectorial + BM25 keyword
3. **Filtered Search** — Filtros por metadatos (fecha, tipo, fuente)
4. **Domain Scoping** — Resultados limitados a dominios autorizados
5. **Ranking** — Scores de relevancia y paginación

---

## Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                         Search Request                           │
│  query: "cómo implementar autenticación"                        │
│  domain_ids: ["uuid-1", "uuid-2"]                               │
│  filters: {type: "pdf", date_from: "2024-01-01"}               │
└─────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│                      Search Pipeline                             │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│  ┌──────────────┐    ┌──────────────┐    ┌──────────────┐      │
│  │   Embed      │    │   Vector     │    │   BM25       │      │
│  │   Query      │───→│   Search     │    │   Keyword    │      │
│  │              │    │   (ChromaDB) │    │   Search     │      │
│  └──────────────┘    └──────┬───────┘    └──────┬───────┘      │
│                             │                    │              │
│                             └────────┬───────────┘              │
│                                      ▼                          │
│                           ┌──────────────────┐                  │
│                           │  RRF Fusion      │                  │
│                           │  (Reciprocal     │                  │
│                           │   Rank Fusion)   │                  │
│                           └────────┬─────────┘                  │
│                                    │                            │
│                                    ▼                            │
│                           ┌──────────────────┐                  │
│                           │  Filter & Rank   │                  │
│                           │  - Metadata      │                  │
│                           │  - Permissions   │                  │
│                           │  - Relevance     │                  │
│                           └────────┬─────────┘                  │
│                                    │                            │
└────────────────────────────────────┼────────────────────────────┘
                                     ▼
┌─────────────────────────────────────────────────────────────────┐
│                      Search Response                             │
│  {                                                              │
│    "query": "cómo implementar autenticación",                  │
│    "results": [                                                 │
│      {                                                          │
│        "chunk_id": "doc-123_0",                                │
│        "score": 0.89,                                          │
│        "text": "Para implementar autenticación...",            │
│        "document_id": "doc-123",                               │
│        "document_title": "Guía de Auth",                       │
│        "domain_id": "uuid-1",                                  │
│        "metadata": {...}                                       │
│      }                                                          │
│    ],                                                           │
│    "total": 42,                                                │
│    "search_time_ms": 125                                       │
│  }                                                              │
└─────────────────────────────────────────────────────────────────┘
```

---

## Success Criteria

1. ✅ A query to `GET /v1/search?q=...&domain=...` returns semantically relevant chunks with `score`, `chunk_text`, `source`, `domain`, and `document_id` fields
2. ✅ Hybrid search (vector + BM25) returns results that include both semantic matches and exact-keyword matches, combined via Reciprocal Rank Fusion
3. ✅ Search results filtered by `type`, `date_from`, `date_to`, or `source` return only documents matching those metadata filters
4. ✅ A user with access to Domain A cannot receive results from Domain B — the domain-scope enforcement is validated by attempting a cross-domain query with a Domain A token
5. ✅ Result sets are paginated; `page=2` returns the next set of results without duplicates from page 1

---

## Tasks

### Task 4.1: Search Service
**Priority:** High  
**Est. Time:** 90 min

Implement core search service:

```python
class SearchService:
    async def semantic_search(
        self,
        query: str,
        domain_ids: List[UUID],
        top_k: int = 10,
        filters: Optional[dict] = None
    ) -> List[SearchResult]:
        # 1. Embed query
        # 2. Search vector store per domain
        # 3. Aggregate results
        # 4. Apply filters
        pass
    
    async def hybrid_search(
        self,
        query: str,
        domain_ids: List[UUID],
        top_k: int = 10,
        filters: Optional[dict] = None,
        vector_weight: float = 0.7,
        keyword_weight: float = 0.3
    ) -> List[SearchResult]:
        # 1. Run semantic search
        # 2. Run BM25 keyword search (PostgreSQL)
        # 3. RRF fusion
        # 4. Return combined results
        pass
```

### Task 4.2: BM25 Keyword Search
**Priority:** High  
**Est. Time:** 60 min

Implement BM25 search in PostgreSQL:

```sql
-- Full-text search using PostgreSQL tsvector
CREATE INDEX idx_documents_fts ON documents 
USING gin(to_tsvector('english', title || ' ' || coalesce(metadata->>'content', '')));
```

```python
async def keyword_search(
    self,
    query: str,
    domain_ids: List[UUID],
    limit: int = 100
) -> List[KeywordResult]:
    # Use PostgreSQL full-text search
    # ts_rank for scoring
    pass
```

### Task 4.3: RRF Fusion
**Priority:** High  
**Est. Time:** 45 min

Implement Reciprocal Rank Fusion:

```python
def reciprocal_rank_fusion(
    vector_results: List[SearchResult],
    keyword_results: List[KeywordResult],
    k: int = 60,
    vector_weight: float = 0.7,
    keyword_weight: float = 0.3
) -> List[FusionResult]:
    """
    RRF score = Σ(1 / (k + rank)) for each result in each list
    """
    pass
```

### Task 4.4: Search API Endpoints
**Priority:** High  
**Est. Time:** 60 min

```python
@router.get("/search")
async def search(
    q: str = Query(..., description="Search query"),
    domains: List[UUID] = Query(..., description="Domain IDs to search"),
    mode: str = Query("hybrid", description="Search mode: semantic, keyword, hybrid"),
    top_k: int = Query(10, ge=1, le=100),
    type: Optional[str] = Query(None, description="Filter by document type"),
    date_from: Optional[datetime] = Query(None),
    date_to: Optional[datetime] = Query(None),
    source: Optional[str] = Query(None),
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
):
    pass
```

### Task 4.5: Domain Access Enforcement
**Priority:** High  
**Est. Time:** 45 min

- Validate user has access to all requested domains
- Filter results to authorized domains only
- Return 403 if user tries to search unauthorized domain

### Task 4.6: Highlighting & Snippets
**Priority:** Medium  
**Est. Time:** 45 min

- Highlight matching keywords in results
- Generate context snippets around matches
- Show why result is relevant

### Task 4.7: Suggestions & Autocomplete
**Priority:** Low  
**Est. Time:** 30 min

- Query suggestions based on popular searches
- Autocomplete from document titles/keywords

### Task 4.8: Search Analytics
**Priority:** Low  
**Est. Time:** 30 min

- Log searches (query, results count, latency)
- Popular queries tracking
- Zero-results tracking

### Task 4.9: Tests
**Priority:** Medium  
**Est. Time:** 60 min

- Unit tests for RRF fusion
- Integration tests for search pipeline
- Permission tests
- Performance tests

### Task 4.10: Documentation
**Priority:** Low  
**Est. Time:** 30 min

- API documentation
- Search examples
- Ranking explanation

---

## BM25 Implementation

PostgreSQL native full-text search with BM25-like ranking:

```sql
-- Search query
SELECT 
    d.id,
    d.title,
    d.domain_id,
    ts_rank_cd(
        to_tsvector('english', d.title || ' ' || COALESCE(d.metadata->>'content', '')),
        plainto_tsquery('english', 'search query'),
        32 -- normalization option
    ) AS rank
FROM documents d
WHERE 
    d.domain_id = ANY($1)
    AND to_tsvector('english', d.title || ' ' || COALESCE(d.metadata->>'content', '')) 
        @@ plainto_tsquery('english', 'search query')
ORDER BY rank DESC
LIMIT $2;
```

---

## RRF Formula

```
RRF_score(d) = Σ (1 / (k + rank_i(d)) * weight_i)

Where:
- k = 60 (constant, prevents dominance of top ranks)
- rank_i(d) = rank of document d in list i
- weight_i = weight for list i (vector: 0.7, keyword: 0.3)

Example:
Document A: rank 1 in vector, rank 5 in keyword
RRF(A) = 1/(60+1)*0.7 + 1/(60+5)*0.3
       = 0.0115 + 0.0046
       = 0.0161
```

---

## Search Modes

### Semantic Only
- Embed query → vector search → return top_k
- Best for: conceptual queries, synonyms

### Keyword Only
- BM25 search on title/content
- Best for: exact terms, proper nouns

### Hybrid (Default)
- Run both → RRF fusion → return combined
- Best for: general queries, balance precision/recall

---

## Performance Considerations

1. **Vector Search:** ~50-100ms per domain
2. **BM25 Search:** ~10-20ms (PostgreSQL index)
3. **RRF Fusion:** ~1-5ms
4. **Total Target:** <200ms for hybrid search

**Optimizations:**
- Cache query embeddings
- Parallel domain searches
- PostgreSQL indexes on metadata
- Redis caching for popular queries

---

## Definition of Done

- [ ] Semantic search returns relevant chunks
- [ ] Hybrid search combines vector + keyword
- [ ] RRF fusion implemented correctly
- [ ] Domain access enforced
- [ ] Metadata filters working
- [ ] Results paginated
- [ ] Highlighting implemented
- [ ] Tests passing
- [ ] Documentation complete
- [ ] Phase 4 VERIFICATION.md

---

**Next Phase:** Phase 5 — BFF Layer (Node.js proxy with WebSocket)
"""Search API endpoints."""

import os
from datetime import datetime
from typing import List
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from adapters import get_embedding_adapter
from adapters.vector_store.chroma_db import ChromaDBAdapter
from core.dependencies import get_current_user, require_domain_access
from db.database import get_db
from db.neo4j_client import get_neo4j
from ports.vector_store import CollectionNotFoundError
from schemas import (
    GraphEdge,
    GraphNode,
    HybridSearchResult,
    IngestionPayload,
    SearchRequest,
    SearchResponse,
    SemanticIngestionResponse,
    SemanticProvenance,
    UserInToken,
)
from services.search_service import SearchService
from services.semantic_ingestion_service import IngestionCoordinator

router = APIRouter(prefix="/v1", tags=["Search"])


async def get_search_service(db: AsyncSession = Depends(get_db)) -> SearchService:
    """Factory to create search service with dependencies."""
    # Create vector store adapter
    vector_store = ChromaDBAdapter(
        host=os.getenv("CHROMA_HOST", "localhost"),
        port=int(os.getenv("CHROMA_PORT", "8000"))
    )

    # Create embedding adapter using factory (handles missing API key gracefully)
    embedding_provider = await get_embedding_adapter()

    return SearchService(
        db=db,
        vector_store=vector_store,
        embedding_provider=embedding_provider
    )


@router.get(
    "/search",
    response_model=SearchResponse,
    summary="Search documents",
    description="""
    Search documents using semantic, keyword, or hybrid search.

    **Search Modes:**
    - `semantic` — Vector similarity search (best for conceptual queries)
    - `keyword` — BM25 keyword search (best for exact terms)
    - `hybrid` — Combines both using RRF fusion (default, recommended)

    **Examples:**
    - `GET /v1/search?q=authentication&domains=uuid1,uuid2`
    - `GET /v1/search?q=machine learning&mode=semantic&top_k=20`
    - `GET /v1/search?q=API&domains=uuid1&type=pdf`
    """
)
async def search_documents(
    q: str = Query(..., min_length=1, max_length=1000, description="Search query"),
    domains: list[UUID] = Query(default=[], description="Domain IDs to search (comma-separated)"),
    mode: str = Query("hybrid", pattern="^(semantic|keyword|hybrid)$", description="Search mode"),
    top_k: int = Query(10, ge=1, le=100, description="Number of results"),
    type: str | None = Query(None, description="Filter by document type (pdf, txt, etc.)"),
    date_from: datetime | None = Query(None, description="Filter by date from (ISO format)"),
    date_to: datetime | None = Query(None, description="Filter by date to (ISO format)"),
    source: str | None = Query(None, description="Filter by source type"),
    user: UserInToken = Depends(get_current_user),
    search_service: SearchService = Depends(get_search_service),
    db: AsyncSession = Depends(get_db)
):
    """
    Search documents across authorized domains.

    Returns ranked results with relevance scores.
    """
    # Validate user has access to all requested domains
    from sqlalchemy import select

    from models import DomainAccess

    is_admin = "KM_ADMIN" in user.roles

    if not is_admin:
        # Check domain access
        for domain_id in domains:
            result = await db.execute(
                select(DomainAccess).where(
                    DomainAccess.user_id == user.id,
                    DomainAccess.domain_id == domain_id
                )
            )
            access = result.scalar_one_or_none()

            if not access:
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail=f"Access denied to domain {domain_id}"
                )

    # Build filters
    filters = {}
    if type:
        filters['type'] = type
    if source:
        filters['source'] = source
    if date_from or date_to:
        filters['date_range'] = {'from': date_from, 'to': date_to}

    # Create search request
    request = SearchRequest(
        query=q,
        domain_ids=domains,
        mode=mode,
        top_k=top_k,
        filters=filters if filters else None
    )

    try:
        # Execute search
        response = await search_service.search(
            request=request,
            domain_ids=domains
        )

        return response

    except Exception as e:
        from core.logging_config import get_logger
        logger = get_logger(__name__)
        logger.error(f"Search failed for query '{q}' in domains {domains}: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Search failed: {str(e)}"
        )


@router.post(
    "/search",
    response_model=SearchResponse,
    summary="Advanced search",
    description="Search with advanced options via POST request."
)
async def search_documents_post(
    request: SearchRequest,
    user: UserInToken = Depends(get_current_user),
    search_service: SearchService = Depends(get_search_service),
    db: AsyncSession = Depends(get_db)
):
    """
    Advanced search with full request body.

    Use this for complex queries with multiple filters.
    """
    # Validate domain access (same as GET endpoint)
    from sqlalchemy import select

    from models import DomainAccess

    is_admin = "KM_ADMIN" in user.roles

    if not is_admin:
        for domain_id in request.domain_ids:
            result = await db.execute(
                select(DomainAccess).where(
                    DomainAccess.user_id == user.id,
                    DomainAccess.domain_id == domain_id
                )
            )
            access = result.scalar_one_or_none()

            if not access:
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail=f"Access denied to domain {domain_id}"
                )

    try:
        response = await search_service.search(
            request=request,
            domain_ids=request.domain_ids
        )

        return response

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Search failed: {str(e)}"
        )


@router.get(
    "/search/suggest",
    summary="Search suggestions",
    description="Get search suggestions based on partial query."
)
async def get_search_suggestions(
    q: str = Query(..., min_length=2, max_length=100, description="Partial query"),
    domains: list[UUID] = Query(default=[], description="Domain IDs"),
    user: UserInToken = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Get search suggestions for autocomplete.

    Returns document titles and keywords that match the partial query.
    """
    from sqlalchemy import select

    from models import Document

    # Simple implementation: suggest document titles
    query = select(Document).where(
        Document.title.ilike(f"%{q}%"),
        Document.status == 'done'
    )

    if domains:
        query = query.where(Document.domain_id.in_(domains))

    query = query.limit(5)

    result = await db.execute(query)
    documents = result.scalars().all()

    suggestions = [doc.title for doc in documents]

    return {
        "query": q,
        "suggestions": suggestions
    }


# ──────────────────────────── Semantic / FEAT6 ───────────────────────────────

def _make_vector_store() -> ChromaDBAdapter:
    return ChromaDBAdapter(
        host=os.getenv("CHROMA_HOST", "localhost"),
        port=int(os.getenv("CHROMA_PORT", "8000")),
    )


@router.post(
    "/search/semantic-ingest",
    response_model=SemanticIngestionResponse,
    status_code=status.HTTP_202_ACCEPTED,
    summary="Atomic semantic ingestion (Neo4j + ChromaDB)",
    description=(
        "Writes a KnowledgeItem to Neo4j (Phase 1) then embeds and indexes the "
        "content in the domain's cosine-distance ChromaDB collection (Phase 2). "
        "If Phase 2 fails the Neo4j node is rolled back automatically."
    ),
)
async def semantic_ingest(
    payload: IngestionPayload,
    domain_id: UUID = Query(..., description="Target domain ID"),
    user: UserInToken = Depends(require_domain_access),
    driver=Depends(get_neo4j),
) -> SemanticIngestionResponse:
    embedding_provider = await get_embedding_adapter()
    coordinator = IngestionCoordinator(
        driver=driver,
        vector_store=_make_vector_store(),
        embedding_provider=embedding_provider,
    )
    try:
        return await coordinator.execute_atomic_ingestion(payload, str(domain_id))
    except RuntimeError as exc:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(exc))


@router.get(
    "/search/hybrid",
    response_model=List[HybridSearchResult],
    summary="Hybrid semantic search with ontology provenance",
    description=(
        "Queries the domain's semantic ChromaDB collection using a cosine-distance "
        "embedding, then enriches each hit with its ontological provenance from Neo4j. "
        "Score = 1.0 - cosine_distance (clamped to [0, 1])."
    ),
)
async def hybrid_search(
    q: str = Query(..., min_length=1, max_length=1000, description="Search query"),
    domain_id: UUID = Query(..., description="Domain to search"),
    limit: int = Query(5, ge=1, le=100, description="Maximum results"),
    user: UserInToken = Depends(require_domain_access),
    driver=Depends(get_neo4j),
) -> List[HybridSearchResult]:
    collection_name = f"semantic_{domain_id}"
    vector_store = _make_vector_store()

    # 1. Embed the query
    embedding_provider = await get_embedding_adapter()
    query_embeddings = await embedding_provider.embed([q])
    query_vector = query_embeddings[0]

    # 2. Vector search — request raw distances for cosine scoring
    try:
        raw_hits = await vector_store.search(
            collection=collection_name,
            query_vector=query_vector,
            top_k=limit,
            as_distances=True,
        )
    except CollectionNotFoundError:
        return []
    except Exception as exc:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"ChromaDB query failed: {exc}",
        )

    # 3. Enrich each hit with Neo4j provenance
    results: List[HybridSearchResult] = []

    for hit in raw_hits:
        link_id_str = hit.metadata.get("link_id") or hit.chunk_id
        score = max(0.0, 1.0 - hit.score)  # cosine: distance ∈ [0, 2]

        # 4. Neo4j provenance query (spec Cypher)
        try:
            async with driver.session() as session:
                neo4j_result = await session.run(
                    """
                    MATCH (n:KnowledgeItem {id: $link_id})-[:INSTANCE_OF]->(c:OWLClass)
                    OPTIONAL MATCH (n)-[r]->(related:KnowledgeItem)
                    RETURN c.name AS owl_class,
                           collect(DISTINCT {id: related.id, label: labels(related)[0], name: related.name}) AS related_nodes,
                           collect(DISTINCT {source: $link_id, target: related.id, type: type(r)}) AS relations
                    """,
                    link_id=link_id_str,
                )
                record = await neo4j_result.single()
        except Exception as exc:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Neo4j provenance query failed: {exc}",
            )

        if not record:
            continue

        nodes = [
            GraphNode(id=n["id"], label=n["label"] or "", name=n["name"] or "")
            for n in (record["related_nodes"] or [])
            if n.get("id")
        ]
        edges = [
            GraphEdge(source=e["source"], target=e["target"], relation_type=e["type"] or "")
            for e in (record["relations"] or [])
            if e.get("target")
        ]

        provenance = SemanticProvenance(
            owl_class=record["owl_class"],
            iso_compliance="ISO_27001",
            nodes=nodes,
            edges=edges,
        )

        results.append(
            HybridSearchResult(
                link_id=UUID(link_id_str),
                content=hit.text,
                score=score,
                source_file=hit.metadata.get("source", ""),
                provenance=provenance,
            )
        )

    return results

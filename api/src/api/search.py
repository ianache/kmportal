"""Search API endpoints."""

from datetime import datetime
from typing import List, Optional
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession

from db.database import get_db
from core.dependencies import get_current_user
from schemas import (
    SearchRequest,
    SearchResponse,
    UserInToken,
)
from services.search_service import SearchService
from adapters.vector_store.chroma_db import ChromaDBAdapter
from adapters.embedding.gemini import GeminiAdapter
import os

router = APIRouter(prefix="/v1", tags=["Search"])


def get_search_service(db: AsyncSession = Depends(get_db)) -> SearchService:
    """Factory to create search service with dependencies."""
    # Create vector store adapter
    vector_store = ChromaDBAdapter(
        host=os.getenv("CHROMA_HOST", "localhost"),
        port=int(os.getenv("CHROMA_PORT", "8000"))
    )
    
    # Create embedding adapter
    embedding_provider = GeminiAdapter(
        api_key=os.getenv("GEMINI_API_KEY", ""),
        model=os.getenv("GEMINI_EMBEDDING_MODEL", "text-embedding-004")
    )
    
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
    domains: List[UUID] = Query(..., description="Domain IDs to search (comma-separated)"),
    mode: str = Query("hybrid", pattern="^(semantic|keyword|hybrid)$", description="Search mode"),
    top_k: int = Query(10, ge=1, le=100, description="Number of results"),
    type: Optional[str] = Query(None, description="Filter by document type (pdf, txt, etc.)"),
    date_from: Optional[datetime] = Query(None, description="Filter by date from (ISO format)"),
    date_to: Optional[datetime] = Query(None, description="Filter by date to (ISO format)"),
    source: Optional[str] = Query(None, description="Filter by source type"),
    user: UserInToken = Depends(get_current_user),
    search_service: SearchService = Depends(get_search_service),
    db: AsyncSession = Depends(get_db)
):
    """
    Search documents across authorized domains.
    
    Returns ranked results with relevance scores.
    """
    # Validate user has access to all requested domains
    from models import DomainAccess, DomainAccessRole
    from sqlalchemy import select
    
    is_admin = "km-admin" in user.roles
    
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
    from models import DomainAccess
    from sqlalchemy import select
    
    is_admin = "km-admin" in user.roles
    
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
    domains: List[UUID] = Query(default=[], description="Domain IDs"),
    user: UserInToken = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Get search suggestions for autocomplete.
    
    Returns document titles and keywords that match the partial query.
    """
    from sqlalchemy import select, func
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
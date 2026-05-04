"""MCP (Model Context Protocol) Server for AI Agent Integration.

This module provides an MCP server that exposes knowledge base functionality
to external AI agents via the Model Context Protocol.

Usage:
    The MCP server is mounted as an ASGI sub-app on the Core API at /mcp.
    
    AI agents can connect via SSE (Server-Sent Events) at:
    - GET /mcp/sse - SSE endpoint for receiving messages
    - POST /mcp/messages - Endpoint for sending messages
"""

from fastmcp import FastMCP
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List, Optional
from uuid import UUID

from db.database import AsyncSessionLocal
from services.search_service import SearchService
from services.api_key_service import APIKeyService
from schemas import SearchRequest
from core.auth import verify_api_key


# Create MCP server instance
mcp = FastMCP(
    "Knowledge Management Center",
    instructions="""
    You are an AI assistant with access to a Knowledge Management Center.
    
    Available tools:
    - search_knowledge: Search documents using semantic and keyword search
    - list_domains: List available knowledge domains
    - get_domain_info: Get information about a specific domain
    
    Use these tools to help users find relevant information from the knowledge base.
    """
)


# Dependency injection for database session
async def get_db() -> AsyncSession:
    """Get database session for MCP tools."""
    async with AsyncSessionLocal() as session:
        try:
            yield session
        finally:
            await session.close()


@mcp.tool()
async def search_knowledge(
    query: str,
    domain_ids: Optional[List[str]] = None,
    top_k: int = 10,
    search_mode: str = "hybrid"
) -> dict:
    """
    Search the knowledge base for relevant documents.
    
    Args:
        query: Search query string
        domain_ids: Optional list of domain IDs to search within
        top_k: Number of results to return (default: 10)
        search_mode: Search mode - "semantic", "keyword", or "hybrid" (default: hybrid)
    
    Returns:
        Dictionary containing search results with title, content, score, and metadata
    """
    async with AsyncSessionLocal() as session:
        search_service = SearchService(session)
        
        # Parse domain_ids if provided
        domain_uuids = []
        if domain_ids:
            domain_uuids = [UUID(did) for did in domain_ids]
        
        # Create search request
        search_request = SearchRequest(
            query=query,
            top_k=top_k,
            mode=search_mode
        )
        
        # Perform search
        response = await search_service.search(
            request=search_request,
            domain_ids=domain_uuids
        )
        
        # Format results
        formatted_results = []
        for result in response.results:
            formatted_results.append({
                "chunk_id": result.chunk_id,
                "document_id": str(result.document_id),
                "title": result.document_title,
                "content": result.text,
                "score": result.score,
                "domain_id": str(result.domain_id),
                "metadata": result.metadata
            })
        
        return {
            "query": query,
            "total_results": len(formatted_results),
            "search_time_ms": response.search_time_ms,
            "results": formatted_results
        }


@mcp.tool()
async def list_domains() -> dict:
    """
    List all available knowledge domains.
    
    Returns:
        Dictionary containing list of domains with id, name, and description
    """
    from services.domain_service import DomainService
    from sqlalchemy import select
    from models.domain import Domain
    
    async with AsyncSessionLocal() as session:
        # Query all domains directly (MCP access is controlled by API key scopes)
        result = await session.execute(select(Domain))
        domains = result.scalars().all()
        
        formatted_domains = []
        for domain in domains:
            formatted_domains.append({
                "id": str(domain.id),
                "name": domain.name,
                "description": domain.description or "",
                "document_count": getattr(domain, "document_count", 0)
            })
        
        return {
            "total": len(formatted_domains),
            "domains": formatted_domains
        }


@mcp.tool()
async def get_domain_info(domain_id: str) -> dict:
    """
    Get detailed information about a specific domain.
    
    Args:
        domain_id: UUID of the domain
    
    Returns:
        Dictionary containing domain details
    """
    from services.domain_service import DomainService
    
    async with AsyncSessionLocal() as session:
        domain_service = DomainService(session)
        domain = await domain_service.get_domain(UUID(domain_id))
        
        if not domain:
            return {"error": f"Domain {domain_id} not found"}
        
        return {
            "id": str(domain.id),
            "name": domain.name,
            "description": domain.description or "",
            "created_at": domain.created_at.isoformat() if domain.created_at else None,
            "updated_at": domain.updated_at.isoformat() if domain.updated_at else None,
            "document_count": getattr(domain, "document_count", 0),
            "embedding_model": getattr(domain, "embedding_model", "default")
        }


@mcp.tool()
async def get_document_status(document_id: str) -> dict:
    """
    Get the status of a document ingestion job.
    
    Args:
        document_id: UUID of the document
    
    Returns:
        Dictionary containing document status and progress
    """
    from services.ingestion_service import IngestionService
    
    async with AsyncSessionLocal() as session:
        ingestion_service = IngestionService(session)
        document = await ingestion_service.get_document_status(UUID(document_id))
        
        if not document:
            return {"error": f"Document {document_id} not found"}
        
        return {
            "document_id": str(document.id),
            "title": document.title,
            "status": document.status.value if hasattr(document.status, 'value') else str(document.status),
            "source_type": document.source_type,
            "chunk_count": document.chunk_count,
            "error_message": document.error_message,
            "created_at": document.created_at.isoformat() if document.created_at else None,
            "updated_at": document.updated_at.isoformat() if document.updated_at else None
        }


def get_mcp_app():
    """
    Get the MCP server as an ASGI application.
    
    Returns:
        ASGI app that can be mounted on the main FastAPI application
    """
    return mcp.http_app(transport="sse")

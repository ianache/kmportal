"""MCP (Model Context Protocol) Server for AI Agent Integration.

This module provides an MCP server that exposes knowledge base functionality
to external AI agents via the Model Context Protocol.

Usage:
    The MCP server is mounted as an ASGI sub-app on the Core API at /mcp.

    AI agents can connect via SSE (Server-Sent Events) at:
    - GET /mcp/sse - SSE endpoint for receiving messages
    - POST /mcp/messages - Endpoint for sending messages
"""

from uuid import UUID

from fastmcp import FastMCP
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from db.database import AsyncSessionLocal
from schemas import SearchRequest
from services.search_service import SearchService

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


from .auth import mcp_user_context


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
    domain_ids: list[str] | None = None,
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
    user = mcp_user_context.get()
    if not user:
        return {"error": "Authentication required"}

    # Check scopes
    if "read" not in user.scopes and "admin" not in user.scopes:
        return {"error": "Insufficient permissions (require 'read' scope)"}

    # Handle domain restrictions
    allowed_domains = user.allowed_domains

    async with AsyncSessionLocal() as session:
        search_service = SearchService(session)

        # Parse domain_ids if provided
        domain_uuids = []
        if domain_ids:
            for did in domain_ids:
                try:
                    duid = UUID(did)
                    # If API key restricted, check if this domain is allowed
                    if allowed_domains and duid not in allowed_domains:
                        return {"error": f"Access denied to domain {did}"}
                    domain_uuids.append(duid)
                except ValueError:
                    return {"error": f"Invalid domain ID format: {did}"}
        elif allowed_domains:
            # If no domains specified but key is restricted, search all allowed domains
            domain_uuids = allowed_domains

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
    from sqlalchemy import select

    from models.base import Domain

    user = mcp_user_context.get()
    if not user:
        return {"error": "Authentication required"}

    async with AsyncSessionLocal() as session:
        # Query domains
        query = select(Domain)

        # Apply domain restrictions from API key
        if user.allowed_domains:
            query = query.where(Domain.id.in_(user.allowed_domains))
        elif "KM_ADMIN" not in user.roles:
            # If not admin and no specific allowed_domains, check user's assigned domains
            from models.base import DomainAccess
            access_q = select(DomainAccess.domain_id).where(DomainAccess.user_id == user.id)
            access_result = await session.execute(access_q)
            user_domain_ids = [r for (r,) in access_result.all()]

            if not user_domain_ids:
                return {"total": 0, "domains": []}

            query = query.where(Domain.id.in_(user_domain_ids))

        result = await session.execute(query)
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

    user = mcp_user_context.get()
    if not user:
        return {"error": "Authentication required"}

    try:
        duid = UUID(domain_id)
    except ValueError:
        return {"error": f"Invalid domain ID format: {domain_id}"}

    # Check API key restrictions
    if user.allowed_domains and duid not in user.allowed_domains:
        return {"error": f"Access denied to domain {domain_id}"}

    async with AsyncSessionLocal() as session:
        # Check user domain access if not admin
        if "KM_ADMIN" not in user.roles:
            from models.base import DomainAccess
            access_q = select(DomainAccess).where(
                DomainAccess.user_id == user.id,
                DomainAccess.domain_id == duid
            )
            access_result = await session.execute(access_q)
            if not access_result.scalar_one_or_none():
                return {"error": f"Access denied to domain {domain_id}"}

        domain_service = DomainService(session)
        domain = await domain_service.get_domain(duid)

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

    user = mcp_user_context.get()
    if not user:
        return {"error": "Authentication required"}

    try:
        doc_id = UUID(document_id)
    except ValueError:
        return {"error": f"Invalid document ID format: {document_id}"}

    async with AsyncSessionLocal() as session:
        ingestion_service = IngestionService(session)
        document = await ingestion_service.get_document_status(doc_id)

        if not document:
            return {"error": f"Document {document_id} not found"}

        # Check access to document's domain
        if user.allowed_domains and document.domain_id not in user.allowed_domains:
            return {"error": "Access denied to this document's domain"}

        if "KM_ADMIN" not in user.roles:
            from models.base import DomainAccess
            access_q = select(DomainAccess).where(
                DomainAccess.user_id == user.id,
                DomainAccess.domain_id == document.domain_id
            )
            access_result = await session.execute(access_q)
            if not access_result.scalar_one_or_none():
                return {"error": "Access denied to this document's domain"}

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
    Get the MCP server as an ASGI application (Streamable HTTP transport).

    Returns:
        ASGI app that can be mounted on the main FastAPI application
    """
    return mcp.http_app()

"""Authentication middleware for MCP server.

Provides API key authentication for MCP endpoints, allowing external
AI agents to authenticate using API keys.
"""

from fastapi import Request, HTTPException, status
from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.types import ASGIApp

from services.api_key_service import APIKeyService
from db.database import AsyncSessionLocal


class MCPAuthMiddleware(BaseHTTPMiddleware):
    """
    Middleware to authenticate MCP requests using API keys.
    
    Expects API key in the X-API-Key header.
    """
    
    def __init__(self, app: ASGIApp):
        super().__init__(app)
    
    async def dispatch(self, request: Request, call_next):
        """
        Process request and validate API key if present.
        
        For SSE endpoint, API key is optional in initial request
        but required for message endpoints.
        """
        # Skip auth for health checks
        if request.url.path.endswith("/health"):
            return await call_next(request)
        
        # Get API key from header
        api_key = request.headers.get("X-API-Key")
        
        if not api_key:
            return JSONResponse(
                status_code=status.HTTP_401_UNAUTHORIZED,
                content={"error": "Missing X-API-Key header"}
            )
        
        # Validate API key
        async with AsyncSessionLocal() as session:
            api_key_service = APIKeyService(session)
            valid_key = await api_key_service.validate_api_key(api_key)
            
            if not valid_key:
                return JSONResponse(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    content={"error": "Invalid or expired API key"}
                )
            
            # Add API key info to request state
            request.state.api_key = valid_key
            request.state.scopes = valid_key.scopes
            request.state.allowed_domains = valid_key.domain_ids
        
        return await call_next(request)


async def require_scope(request: Request, scope: str) -> bool:
    """
    Check if the authenticated API key has the required scope.
    
    Args:
        request: FastAPI request object
        scope: Required scope (e.g., "read", "write", "admin")
    
    Returns:
        True if scope is allowed, raises HTTPException otherwise
    """
    scopes = getattr(request.state, "scopes", [])
    
    if "admin" in scopes:
        return True
    
    if scope not in scopes:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=f"Required scope '{scope}' not granted to this API key"
        )
    
    return True


async def check_domain_access(request: Request, domain_id: str) -> bool:
    """
    Check if the API key has access to a specific domain.
    
    Args:
        request: FastAPI request object
        domain_id: Domain UUID string
    
    Returns:
        True if access is allowed, raises HTTPException otherwise
    """
    allowed_domains = getattr(request.state, "allowed_domains", [])
    
    # If no domains specified, allow all
    if not allowed_domains:
        return True
    
    # Check if domain is in allowed list
    if domain_id not in [str(d) for d in allowed_domains]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=f"API key does not have access to domain {domain_id}"
        )
    
    return True

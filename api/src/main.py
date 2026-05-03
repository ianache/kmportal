"""Knowledge Management Center - Core API

FastAPI application providing REST API for the knowledge management platform.

Usage:
    uvicorn main:app --reload --host 0.0.0.0 --port 8000

Endpoints:
    - GET /health - Health check
    - GET /docs - Swagger UI documentation
    - GET /openapi.json - OpenAPI schema
"""

import os
from contextlib import asynccontextmanager

from fastapi import FastAPI, status
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from db.database import init_db, close_db
from api import domains_router, api_keys_router, ingestion_router, search_router
from mcp import get_mcp_app, MCPAuthMiddleware


# Models
class HealthResponse(BaseModel):
    """Health check response model."""
    service: str
    status: str
    version: str
    environment: str


class Config:
    """Application configuration from environment."""
    ENVIRONMENT = os.getenv("ENVIRONMENT", "development")
    VERSION = os.getenv("VERSION", "0.2.0")
    CORS_ORIGINS = os.getenv("CORS_ORIGINS", "http://localhost:3000,http://localhost:5100").split(",")


# Lifecycle management
@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Application lifespan manager.
    
    Handles startup and shutdown events:
    - Startup: Initialize connections to databases
    - Shutdown: Close connections gracefully
    """
    # Startup
    print(f"🚀 Starting Knowledge Management API v{Config.VERSION}")
    print(f"   Environment: {Config.ENVIRONMENT}")
    
    # Initialize database
    print("   Initializing database...")
    await init_db()
    print("   ✅ Database initialized")
    
    # TODO: Verify vector store connectivity
    # TODO: Verify embedding provider connectivity
    
    yield
    
    # Shutdown
    print("🛑 Shutting down API")
    await close_db()


# Create FastAPI app
app = FastAPI(
    title="Knowledge Management Center API",
    description="""
    API for the Knowledge Management Center platform.
    
    ## Features
    
    - **Domain Management**: Create and manage knowledge domains
    - **Document Ingestion**: Upload and process documents from multiple sources
    - **Semantic Search**: Search documents using vector similarity
    - **API Keys**: Manage access for third-party integrations
    - **MCP**: Model Context Protocol for AI agent integration
    
    ## Authentication
    
    - Web users: OAuth2/OIDC via Keycloak (JWT Bearer token)
    - API clients: API Key in X-API-Key header
    """,
    version=Config.VERSION,
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url="/openapi.json",
    lifespan=lifespan
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=Config.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(domains_router, prefix="/v1")
app.include_router(api_keys_router, prefix="/v1")
app.include_router(ingestion_router, prefix="/v1")
app.include_router(search_router)

# Mount MCP server as ASGI sub-app
mcp_app = get_mcp_app()
mcp_app.add_middleware(MCPAuthMiddleware)
app.mount("/mcp", mcp_app)


@app.get(
    "/health",
    response_model=HealthResponse,
    status_code=status.HTTP_200_OK,
    tags=["Health"],
    summary="Health check endpoint",
    description="Returns service health status. Used by Docker and Kubernetes for health probes."
)
async def health_check() -> HealthResponse:
    """
    Health check endpoint.
    
    Returns basic health information about the service.
    In Phase 2, this checks database connectivity.
    
    Returns:
        HealthResponse with service status
    """
    return HealthResponse(
        service="knowledge-api",
        status="healthy",
        version=Config.VERSION,
        environment=Config.ENVIRONMENT
    )


@app.get(
    "/",
    tags=["Root"],
    summary="API root",
    include_in_schema=False
)
async def root():
    """Redirect root to docs."""
    return {
        "message": "Knowledge Management Center API",
        "version": Config.VERSION,
        "docs": "/docs",
        "health": "/health"
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=Config.ENVIRONMENT == "development"
    )
"""Knowledge Management Center - Core API

FastAPI application providing REST API for the knowledge management platform.

Usage:
    uvicorn main:app --reload --host 0.0.0.0 --port 8000

Endpoints:
    - GET /health - Health check
    - GET /docs - Swagger UI documentation
    - GET /openapi.json - OpenAPI schema
"""

# Load .env file before anything else reads env vars
from pathlib import Path

from dotenv import load_dotenv

_env_file = Path(__file__).resolve().parent.parent / ".env"
if _env_file.exists():
    load_dotenv(_env_file, override=False)

import os
import time
from contextlib import asynccontextmanager
from datetime import datetime

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.gzip import GZipMiddleware

from api import api_keys_router, domains_router, health_router, ingestion_router, ontology_router, search_router
from core.logging_config import configure_logging, get_logger
from core.logging_middleware import LoggingMiddleware
from core.rate_limit_middleware import RateLimitMiddleware
from db.database import close_db, init_db
from db.neo4j_client import close_neo4j
from mcp_server import MCPAuthMiddleware, get_mcp_app

# Initialize logger
logger = get_logger(__name__)

# Track application start time
_start_time = time.time()


class Config:
    """Application configuration from environment."""
    ENVIRONMENT = os.getenv("ENVIRONMENT", "development")
    VERSION = os.getenv("VERSION", "0.2.0")
    LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")
    JSON_LOGS = os.getenv("JSON_LOGS", "false").lower() == "true"
    CORS_ORIGINS = os.getenv("CORS_ORIGINS", "http://localhost:3000,http://localhost:5100").split(",")

    @classmethod
    def is_production(cls) -> bool:
        """Check if running in production environment."""
        return cls.ENVIRONMENT == "production"


# Configure structured logging on module load
configure_logging(
    log_level=Config.LOG_LEVEL,
    json_format=Config.JSON_LOGS or Config.is_production()
)


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
    logger.info(
        "application_startup",
        version=Config.VERSION,
        environment=Config.ENVIRONMENT,
        log_level=Config.LOG_LEVEL,
        structured_logging=Config.JSON_LOGS or Config.is_production()
    )

    try:
        # Initialize database
        logger.info("database_initialization_start")
        await init_db()
        logger.info("database_initialization_complete")

        # Calculate startup time
        startup_time = time.time() - _start_time
        logger.info("application_startup_complete", startup_time_ms=round(startup_time * 1000, 2))

    except Exception as e:
        logger.error("application_startup_failed", error=str(e), error_type=type(e).__name__)
        raise

    yield

    # Shutdown
    logger.info("application_shutdown_start")
    try:
        await close_db()
        await close_neo4j()
        logger.info("application_shutdown_complete")
    except Exception as e:
        logger.error("application_shutdown_error", error=str(e))


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

    ## Health Endpoints

    - `GET /health` - Basic health check
    - `GET /health/detailed` - Comprehensive health check
    - `GET /health/ready` - Kubernetes readiness probe
    - `GET /health/live` - Kubernetes liveness probe
    - `GET /metrics` - Prometheus metrics
    """,
    version=Config.VERSION,
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url="/openapi.json",
    lifespan=lifespan
)

# Add middleware (order matters - first added is first processed)

# 1. GZip compression for responses
app.add_middleware(GZipMiddleware, minimum_size=1000)

# 2. CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=Config.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 3. Request logging middleware (must be after CORS to log all requests)
app.add_middleware(LoggingMiddleware)

# 4. API Key Rate Limiting
app.add_middleware(RateLimitMiddleware)

# Include routers
app.include_router(domains_router, prefix="/v1")
app.include_router(api_keys_router, prefix="/v1")
app.include_router(ingestion_router, prefix="/v1")
app.include_router(ontology_router, prefix="/v1")
app.include_router(search_router)
app.include_router(health_router)

# Mount MCP server as ASGI sub-app
mcp_app = get_mcp_app()
mcp_app.add_middleware(MCPAuthMiddleware)
app.mount("/mcp", mcp_app)


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
        "environment": Config.ENVIRONMENT,
        "docs": "/docs",
        "health": "/health",
        "metrics": "/metrics"
    }


@app.get("/version", tags=["System"])
async def version():
    """Get API version information."""
    return {
        "version": Config.VERSION,
        "environment": Config.ENVIRONMENT,
        "timestamp": datetime.utcnow().isoformat(),
        "uptime_seconds": int(time.time() - _start_time)
    }



if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=Config.ENVIRONMENT == "development",
        access_log=False  # We use structured logging instead
    )

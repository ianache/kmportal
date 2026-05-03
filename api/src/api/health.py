"""Enhanced health checks and metrics for production monitoring.

Provides comprehensive health checks for all service dependencies
and Prometheus-compatible metrics endpoint.
"""

import time
from typing import Any

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, Field
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

from db.database import get_db, AsyncSessionLocal
from core.logging_config import get_logger

logger = get_logger(__name__)
router = APIRouter(tags=["Health"])


# In-memory metrics storage (replace with Prometheus in production)
_request_count = 0
_request_duration_total = 0.0
_error_count = 0
_last_check_time = 0


class HealthCheck(BaseModel):
    """Individual health check result."""
    name: str
    status: str = Field(..., pattern="^(healthy|unhealthy|degraded)$")
    response_time_ms: float
    message: str | None = None
    details: dict[str, Any] | None = None


class HealthResponse(BaseModel):
    """Comprehensive health check response."""
    status: str = Field(..., pattern="^(healthy|unhealthy|degraded)$")
    version: str
    environment: str
    timestamp: str
    checks: list[HealthCheck]
    uptime_seconds: float


class MetricsResponse(BaseModel):
    """Prometheus-style metrics response."""
    metrics: str


async def check_database() -> HealthCheck:
    """Check database connectivity."""
    start_time = time.time()
    
    try:
        async with AsyncSessionLocal() as session:
            # Simple query to verify connection
            result = await session.execute(text("SELECT 1"))
            await result.scalar()
        
        response_time = (time.time() - start_time) * 1000
        
        return HealthCheck(
            name="database",
            status="healthy",
            response_time_ms=round(response_time, 2),
            message="Database connection successful"
        )
        
    except Exception as e:
        response_time = (time.time() - start_time) * 1000
        logger.error("health_check_database_failed", error=str(e))
        
        return HealthCheck(
            name="database",
            status="unhealthy",
            response_time_ms=round(response_time, 2),
            message=f"Database connection failed: {str(e)}"
        )


async def check_vector_store() -> HealthCheck:
    """Check vector store connectivity."""
    start_time = time.time()
    
    try:
        # Check if vector store adapter is configured
        from adapters import get_vector_store_adapter
        
        adapter = await get_vector_store_adapter()
        
        # Try to get collections count as health check
        collections = await adapter.list_collections()
        
        response_time = (time.time() - start_time) * 1000
        
        return HealthCheck(
            name="vector_store",
            status="healthy",
            response_time_ms=round(response_time, 2),
            message="Vector store connection successful",
            details={"collections_count": len(collections)}
        )
        
    except Exception as e:
        response_time = (time.time() - start_time) * 1000
        logger.error("health_check_vector_store_failed", error=str(e))
        
        return HealthCheck(
            name="vector_store",
            status="degraded",  # Degraded, not unhealthy - app can still work
            response_time_ms=round(response_time, 2),
            message=f"Vector store check failed: {str(e)}"
        )


async def check_embedding_provider() -> HealthCheck:
    """Check embedding provider connectivity."""
    start_time = time.time()
    
    try:
        from adapters import get_embedding_adapter
        
        adapter = await get_embedding_adapter()
        
        # Get configuration info (don't actually call API to save costs)
        response_time = (time.time() - start_time) * 1000
        
        return HealthCheck(
            name="embedding_provider",
            status="healthy",
            response_time_ms=round(response_time, 2),
            message="Embedding provider configured",
            details={
                "model": adapter.model_name,
                "dimension": adapter.dimension
            }
        )
        
    except Exception as e:
        response_time = (time.time() - start_time) * 1000
        logger.error("health_check_embedding_failed", error=str(e))
        
        return HealthCheck(
            name="embedding_provider",
            status="degraded",
            response_time_ms=round(response_time, 2),
            message=f"Embedding provider check failed: {str(e)}"
        )


@router.get(
    "/health",
    response_model=HealthResponse,
    summary="Basic health check",
    description="Returns basic service health status."
)
async def basic_health() -> HealthResponse:
    """Basic health endpoint for load balancers."""
    return HealthResponse(
        status="healthy",
        version="0.2.0",
        environment="production",
        timestamp=time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        checks=[],
        uptime_seconds=time.time() - _last_check_time
    )


@router.get(
    "/health/detailed",
    response_model=HealthResponse,
    summary="Detailed health check",
    description="Comprehensive health check including all dependencies."
)
async def detailed_health() -> HealthResponse:
    """Detailed health check for monitoring systems."""
    import os
    
    # Run all health checks concurrently
    checks = await asyncio.gather(
        check_database(),
        check_vector_store(),
        check_embedding_provider(),
        return_exceptions=True
    )
    
    # Filter out exceptions and convert to HealthCheck objects
    valid_checks = []
    for check in checks:
        if isinstance(check, Exception):
            valid_checks.append(HealthCheck(
                name="unknown",
                status="unhealthy",
                response_time_ms=0,
                message=f"Check failed with exception: {str(check)}"
            ))
        else:
            valid_checks.append(check)
    
    # Determine overall status
    if any(c.status == "unhealthy" for c in valid_checks):
        overall_status = "unhealthy"
    elif any(c.status == "degraded" for c in valid_checks):
        overall_status = "degraded"
    else:
        overall_status = "healthy"
    
    return HealthResponse(
        status=overall_status,
        version=os.getenv("VERSION", "0.2.0"),
        environment=os.getenv("ENVIRONMENT", "production"),
        timestamp=time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        checks=valid_checks,
        uptime_seconds=time.time() - _last_check_time
    )


@router.get(
    "/health/ready",
    status_code=status.HTTP_200_OK,
    summary="Readiness probe",
    description="Kubernetes readiness probe endpoint."
)
async def readiness_probe() -> dict[str, str]:
    """Kubernetes readiness probe."""
    # Check if service is ready to accept traffic
    try:
        async with AsyncSessionLocal() as session:
            await session.execute(text("SELECT 1"))
        
        return {"status": "ready"}
        
    except Exception as e:
        logger.error("readiness_check_failed", error=str(e))
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Service not ready"
        )


@router.get(
    "/health/live",
    status_code=status.HTTP_200_OK,
    summary="Liveness probe",
    description="Kubernetes liveness probe endpoint."
)
async def liveness_probe() -> dict[str, str]:
    """Kubernetes liveness probe."""
    # Simple check that process is running
    return {"status": "alive"}


@router.get(
    "/metrics",
    response_class=MetricsResponse,
    summary="Prometheus metrics",
    description="Prometheus-compatible metrics endpoint."
)
async def prometheus_metrics() -> MetricsResponse:
    """Prometheus metrics endpoint."""
    global _request_count, _request_duration_total, _error_count
    
    # Build Prometheus-style metrics
    metrics_lines = [
        "# HELP http_requests_total Total HTTP requests",
        "# TYPE http_requests_total counter",
        f'http_requests_total{{service="knowledge-api"}} {_request_count}',
        "",
        "# HELP http_request_duration_seconds Total HTTP request duration",
        "# TYPE http_request_duration_seconds counter",
        f'http_request_duration_seconds{{service="knowledge-api"}} {_request_duration_total}',
        "",
        "# HELP http_errors_total Total HTTP errors",
        "# TYPE http_errors_total counter",
        f'http_errors_total{{service="knowledge-api"}} {_error_count}',
        "",
        "# HELP process_uptime_seconds Process uptime in seconds",
        "# TYPE process_uptime_seconds gauge",
        f'process_uptime_seconds{{service="knowledge-api"}} {time.time() - _last_check_time}',
    ]
    
    return MetricsResponse(metrics="\n".join(metrics_lines))


# Import asyncio at the end to avoid circular imports
import asyncio

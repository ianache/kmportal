"""Logging middleware for request/response logging.

Provides middleware to automatically log all HTTP requests with structured data
including timing, status codes, and request metadata.
"""

import time
from typing import Callable

from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.types import ASGIApp

from core.logging_config import get_logger, bind_request_context

logger = get_logger(__name__)


class LoggingMiddleware(BaseHTTPMiddleware):
    """
    Middleware to log all HTTP requests with structured data.
    
    Logs request method, path, status code, duration, and client information.
    Also binds request context for correlation across log entries.
    """
    
    def __init__(
        self,
        app: ASGIApp,
        exclude_paths: list[str] | None = None
    ):
        super().__init__(app)
        self.exclude_paths = exclude_paths or ["/health", "/metrics", "/docs", "/redoc", "/openapi.json"]
    
    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        """Process request and log details."""
        # Skip logging for excluded paths
        if any(request.url.path.startswith(path) for path in self.exclude_paths):
            return await call_next(request)
        
        # Generate request ID if not present
        request_id = request.headers.get("X-Request-ID", self._generate_request_id())
        
        # Extract user info if available
        user_id = None
        if hasattr(request.state, "user") and request.state.user:
            user_id = str(getattr(request.state.user, "id", None))
        
        # Bind request context for all logs in this request
        bind_request_context(
            request_id=request_id,
            user_id=user_id,
            client_ip=self._get_client_ip(request),
            method=request.method,
            path=request.url.path,
        )
        
        # Record start time
        start_time = time.time()
        
        try:
            # Process request
            response = await call_next(request)
            
            # Calculate duration
            duration_ms = (time.time() - start_time) * 1000
            
            # Log successful request
            logger.info(
                "http_request",
                status_code=response.status_code,
                duration_ms=round(duration_ms, 2),
                content_length=response.headers.get("content-length"),
                user_agent=request.headers.get("user-agent"),
            )
            
            # Add request ID to response headers
            response.headers["X-Request-ID"] = request_id
            
            return response
            
        except Exception as e:
            # Calculate duration even for failed requests
            duration_ms = (time.time() - start_time) * 1000
            
            # Log error
            logger.error(
                "http_request_error",
                error_type=type(e).__name__,
                error_message=str(e),
                duration_ms=round(duration_ms, 2),
            )
            raise
    
    def _generate_request_id(self) -> str:
        """Generate a unique request ID."""
        import uuid
        return str(uuid.uuid4())[:8]
    
    def _get_client_ip(self, request: Request) -> str:
        """Extract client IP from request."""
        # Check for forwarded headers (when behind proxy)
        forwarded = request.headers.get("X-Forwarded-For")
        if forwarded:
            return forwarded.split(",")[0].strip()
        
        real_ip = request.headers.get("X-Real-IP")
        if real_ip:
            return real_ip
        
        # Fall back to direct connection
        if request.client:
            return request.client.host
        
        return "unknown"

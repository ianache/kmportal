"""Request/response logging middleware — implemented as pure ASGI to avoid
the BaseHTTPMiddleware exception-propagation bug present in Starlette >= 0.36.

With BaseHTTPMiddleware, when ExceptionMiddleware catches a route exception and
produces an error response, the original exception is sometimes also re-raised
through call_next, reaching ServerErrorMiddleware and returning plain-text
"Internal Server Error" instead of the structured JSON response.  Pure ASGI
middleware does not have this issue.
"""

import time
import uuid

import structlog
from starlette.types import ASGIApp, Receive, Scope, Send

from core.logging_config import get_logger

logger = get_logger(__name__)

_DEFAULT_EXCLUDE = frozenset(["/health", "/metrics", "/docs", "/redoc", "/openapi.json"])


class LoggingMiddleware:
    def __init__(self, app: ASGIApp, exclude_paths: list[str] | None = None) -> None:
        self.app = app
        self.exclude_paths: frozenset[str] = frozenset(exclude_paths or _DEFAULT_EXCLUDE)

    async def __call__(self, scope: Scope, receive: Receive, send: Send) -> None:
        if scope["type"] != "http":
            await self.app(scope, receive, send)
            return

        path: str = scope.get("path", "")

        if any(path.startswith(p) for p in self.exclude_paths):
            await self.app(scope, receive, send)
            return

        headers: list[tuple[bytes, bytes]] = scope.get("headers", [])
        request_id = self._extract_header(headers, b"x-request-id") or str(uuid.uuid4())[:8]
        client_ip = self._client_ip(scope, headers)
        method: str = scope.get("method", "")

        # Bind request-scoped structured logging context for all log entries in
        # this request, then clear it once the request completes.
        structlog.contextvars.clear_contextvars()
        structlog.contextvars.bind_contextvars(
            request_id=request_id,
            client_ip=client_ip,
            method=method,
            path=path,
        )

        status_code = 500
        start = time.perf_counter()

        async def send_wrapper(message: dict) -> None:
            nonlocal status_code
            if message["type"] == "http.response.start":
                status_code = message.get("status", 500)
                extra_headers = list(message.get("headers", []))
                extra_headers.append((b"x-request-id", request_id.encode()))
                message = {**message, "headers": extra_headers}
            await send(message)

        try:
            await self.app(scope, receive, send_wrapper)
        except Exception as exc:
            duration_ms = round((time.perf_counter() - start) * 1000, 2)
            logger.error(
                "http_request_error",
                error_type=type(exc).__name__,
                error_message=str(exc),
                duration_ms=duration_ms,
            )
            raise
        else:
            duration_ms = round((time.perf_counter() - start) * 1000, 2)
            logger.info(
                "http_request",
                status_code=status_code,
                duration_ms=duration_ms,
            )
        finally:
            structlog.contextvars.clear_contextvars()

    @staticmethod
    def _extract_header(headers: list[tuple[bytes, bytes]], name: bytes) -> str | None:
        for h_name, h_value in headers:
            if h_name.lower() == name:
                return h_value.decode()
        return None

    @staticmethod
    def _client_ip(scope: Scope, headers: list[tuple[bytes, bytes]]) -> str:
        for name, value in headers:
            if name.lower() == b"x-forwarded-for":
                return value.decode().split(",")[0].strip()
            if name.lower() == b"x-real-ip":
                return value.decode()
        client = scope.get("client")
        return client[0] if client else "unknown"

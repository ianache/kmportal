"""API key rate limiting middleware — implemented as pure ASGI to avoid
the BaseHTTPMiddleware exception-propagation bug present in Starlette >= 0.36."""

import json
import time

import redis.asyncio as redis
from starlette.types import ASGIApp, Receive, Scope, Send

from core.auth import hash_api_key
from core.config import settings
from core.logging_config import get_logger

logger = get_logger(__name__)

_429_BODY = json.dumps({"detail": "Rate limit exceeded. Please try again later."}).encode()


class RateLimitMiddleware:
    def __init__(self, app: ASGIApp) -> None:
        self.app = app
        self._redis: redis.Redis | None = None
        self._redis_url = f"redis://{settings.redis_host}:{settings.redis_port}"

    async def _get_redis(self) -> redis.Redis:
        if self._redis is None:
            self._redis = redis.from_url(
                self._redis_url,
                encoding="utf-8",
                decode_responses=True,
            )
        return self._redis

    async def __call__(self, scope: Scope, receive: Receive, send: Send) -> None:
        if scope["type"] != "http":
            await self.app(scope, receive, send)
            return

        api_key: str | None = None
        for name, value in scope.get("headers", []):
            if name.lower() == b"x-api-key":
                api_key = value.decode()
                break

        if not api_key:
            await self.app(scope, receive, send)
            return

        try:
            client = await self._get_redis()
            key_hash = hash_api_key(api_key)
            limit = settings.api_key_rate_limit
            window = int(time.time() / 3600)
            redis_key = f"rate_limit:{key_hash}:{window}"

            pipe = client.pipeline()
            pipe.incr(redis_key)
            pipe.ttl(redis_key)
            results = await pipe.execute()

            count: int = results[0]
            ttl: int = results[1]

            if ttl == -1:
                await client.expire(redis_key, 3600)
                ttl = 3600

            if count > limit:
                logger.warning(
                    "api_key_rate_limit_exceeded",
                    key_hash=key_hash,
                    count=count,
                    limit=limit,
                    path=scope.get("path", ""),
                )
                retry_after = str(max(0, ttl)).encode()
                await send({
                    "type": "http.response.start",
                    "status": 429,
                    "headers": [
                        (b"content-type", b"application/json"),
                        (b"retry-after", retry_after),
                    ],
                })
                await send({"type": "http.response.body", "body": _429_BODY})
                return

        except Exception as exc:
            logger.error("rate_limit_middleware_error", error=str(exc))
            # Fail open — let the request through

        await self.app(scope, receive, send)

"""Middleware for API key rate limiting using Redis."""

import time

import redis.asyncio as redis
from fastapi import Request, Response, status
from starlette.middleware.base import BaseHTTPMiddleware

from core.auth import hash_api_key
from core.config import settings
from core.logging_config import get_logger

logger = get_logger(__name__)


class RateLimitMiddleware(BaseHTTPMiddleware):
    """
    Middleware to enforce rate limits on API keys.

    Uses Redis to track request counts in fixed hourly windows.
    """

    def __init__(self, app):
        super().__init__(app)
        self.redis_client = None
        self.redis_url = f"redis://{settings.redis_host}:{settings.redis_port}"

    async def _get_redis(self):
        """Lazy initialization of Redis client."""
        if self.redis_client is None:
            self.redis_client = redis.from_url(
                self.redis_url,
                encoding="utf-8",
                decode_responses=True
            )
        return self.redis_client

    async def dispatch(self, request: Request, call_next):
        """Process the request and enforce rate limits."""
        api_key = request.headers.get("X-API-Key")

        # Only apply rate limiting to requests with API keys
        if not api_key:
            return await call_next(request)

        # Hash the key for privacy and consistent indexing
        key_hash = hash_api_key(api_key)

        # In a more advanced implementation, we would fetch the specific
        # rate limit for this key from the database and cache it in Redis.
        # For this version, we use the global setting.
        limit = settings.api_key_rate_limit

        # Fixed window: current hour
        current_hour_timestamp = int(time.time() / 3600)
        redis_key = f"rate_limit:{key_hash}:{current_hour_timestamp}"

        try:
            client = await self._get_redis()

            # Increment and set expiration if it's a new key
            pipe = client.pipeline()
            pipe.incr(redis_key)
            pipe.ttl(redis_key)
            results = await pipe.execute()

            count = results[0]
            ttl = results[1]

            if ttl == -1:  # No expiration set
                await client.expire(redis_key, 3600)
                ttl = 3600

            if count > limit:
                logger.warning(
                    "api_key_rate_limit_exceeded",
                    key_hash=key_hash,
                    count=count,
                    limit=limit,
                    path=request.url.path
                )

                # Return 429 Too Many Requests
                retry_after = max(0, ttl)
                return Response(
                    content='{"detail": "Rate limit exceeded. Please try again later."}',
                    status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                    media_type="application/json",
                    headers={"Retry-After": str(retry_after)}
                )

        except Exception as e:
            # Log error but allow request through (fail-open)
            logger.error("rate_limit_middleware_error", error=str(e))
            return await call_next(request)

        return await call_next(request)

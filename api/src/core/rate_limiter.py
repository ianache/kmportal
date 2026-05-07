"""In-memory sliding-window rate limiter for API key requests."""

import time
from collections import defaultdict
from threading import Lock


class RateLimiter:
    def __init__(self) -> None:
        self._window: dict[str, list[float]] = defaultdict(list)
        self._lock = Lock()

    def check(self, key: str, limit: int, window_seconds: int = 3600) -> tuple[bool, int]:
        """
        Returns (allowed, retry_after_seconds).
        retry_after_seconds is 0 when allowed.
        """
        now = time.time()
        cutoff = now - window_seconds

        with self._lock:
            timestamps = self._window[key]
            # Evict expired entries
            self._window[key] = [t for t in timestamps if t > cutoff]

            if len(self._window[key]) >= limit:
                oldest = self._window[key][0]
                retry_after = max(1, int(oldest + window_seconds - now) + 1)
                return False, retry_after

            self._window[key].append(now)
            return True, 0


rate_limiter = RateLimiter()

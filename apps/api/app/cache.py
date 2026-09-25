"""Read-through cache for hot recommendation reads.

Redis when ``REDIS_URL`` is set, otherwise an in-memory TTL cache (default).
Both backends share ``get`` / ``setex`` / ``delete_pattern`` so invalidation
(on new ratings) works identically.
"""

from __future__ import annotations

import fnmatch
import os
import time


class MemoryCache:
    def __init__(self) -> None:
        self._data: dict[str, tuple[str, float]] = {}

    def get(self, key: str) -> str | None:
        item = self._data.get(key)
        if item is None:
            return None
        value, expires = item
        if expires < time.monotonic():
            del self._data[key]
            return None
        return value

    def setex(self, key: str, ttl_seconds: int, value: str) -> None:
        self._data[key] = (value, time.monotonic() + ttl_seconds)

    def delete_pattern(self, pattern: str) -> None:
        for key in [k for k in self._data if fnmatch.fnmatch(k, pattern)]:
            del self._data[key]


class RedisCache:
    def __init__(self, url: str):
        try:
            import redis
        except ImportError as exc:
            raise RuntimeError(
                "Redis cache needs: pip install recommender[redis]"
            ) from exc
        self._client = redis.Redis.from_url(url, decode_responses=True)

    def get(self, key: str) -> str | None:
        return self._client.get(key)

    def setex(self, key: str, ttl_seconds: int, value: str) -> None:
        self._client.setex(key, ttl_seconds, value)

    def delete_pattern(self, pattern: str) -> None:
        for key in self._client.scan_iter(match=pattern):
            self._client.delete(key)


def get_cache() -> MemoryCache | RedisCache:
    url = os.getenv("REDIS_URL")
    return RedisCache(url) if url else MemoryCache()

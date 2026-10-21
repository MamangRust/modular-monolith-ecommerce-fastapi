"""Generic Redis cache store."""

from __future__ import annotations

import json
from typing import Any

from pkg.logger.logger import Logger


class CacheStore:
    def __init__(self, redis: Any, logger: Logger, prefix: str = "") -> None:
        if redis is None:
            raise ValueError("cache store redis is nil")
        self._redis = redis
        self._logger = logger
        self._prefix = prefix

    @property
    def redis(self) -> Any:
        return self._redis

    def _key(self, key: str) -> str:
        return f"{self._prefix}{key}" if self._prefix else key

    def key(self, key: str) -> str:
        """Public form of `_key` for caches that talk to Redis directly (counters such as the login lockout)."""
        return self._key(key)

    async def get(self, key: str) -> str | None:
        try:
            return await self._redis.get(self._key(key))
        except Exception as exc:
            self._logger.warn("cache get failed", key=key, error=str(exc))
            return None

    async def set(self, key: str, value: str, ttl_seconds: int) -> bool:
        try:
            await self._redis.set(self._key(key), value, ex=ttl_seconds)
            return True
        except Exception as exc:
            self._logger.warn("cache set failed", key=key, error=str(exc))
            return False

    async def delete(self, key: str) -> int:
        try:
            return int(await self._redis.delete(self._key(key)))
        except Exception as exc:
            self._logger.warn("cache delete failed", key=key, error=str(exc))
            return 0

    async def get_json(self, key: str) -> Any | None:
        raw = await self.get(key)
        if raw is None:
            return None
        try:
            return json.loads(raw)
        except ValueError as exc:
            self._logger.warn("cache payload is not valid JSON", key=key, error=str(exc))
            return None

    async def set_json(self, key: str, value: Any, ttl_seconds: int) -> bool:
        try:
            payload = json.dumps(value, default=str)
        except (TypeError, ValueError) as exc:
            self._logger.warn("cache payload is not JSON serialisable", key=key, error=str(exc))
            return False
        return await self.set(key, payload, ttl_seconds)

    async def invalidate(self, pattern: str) -> int:
        """SCAN + DEL every key matching `pattern` (never KEYS)."""
        deleted = 0
        try:
            async for key in self._redis.scan_iter(match=self._key(pattern), count=100):
                deleted += int(await self._redis.delete(key))
        except Exception as exc:
            self._logger.warn("cache invalidate failed", pattern=pattern, error=str(exc))
        return deleted

    async def clear_expired(self) -> int:
        """No-op: Redis expires keys natively via TTL. the reference tracked expiry in a side structure; here TTL is authoritative, so there is nothing to sweep. Kept for interface periodic cleanup task."""
        return 0

    async def stats(self) -> dict[str, Any]:
        stats: dict[str, Any] = {"total_keys": 0, "memory_used": 0, "memory_used_human": ""}
        try:
            stats["total_keys"] = int(await self._redis.dbsize())
            info = await self._redis.info("memory")
            used = int(info.get("used_memory", 0))
            stats["memory_used"] = used
            stats["memory_used_human"] = info.get("used_memory_human", "")
        except Exception as exc:
            self._logger.warn("cache stats failed", error=str(exc))
        return stats

    async def close(self) -> None:
        from pkg.redis.redis import close_redis

        await close_redis(self._redis, self._logger)


__all__ = ["CacheStore"]

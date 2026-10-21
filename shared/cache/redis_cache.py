"""Generic Redis cache store. Values are JSON-serialized; cache failures never raise — they log, record a miss, and let the caller fall through to the source of truth. Generic helpers mirror GetFromCache/SetToCache with model_validate / model_dump for pydantic payloads, or plain JSON round-trips otherwise."""

from __future__ import annotations

import json
from typing import Any, TypeVar

import redis.asyncio as aioredis

from pkg.logger.logger import Logger

T = TypeVar("T")

DEFAULT_TTL = 300  # 5 minutes (ttlDefault)


class CacheStore:
    def __init__(self, redis_client: aioredis.Redis, logger: Logger) -> None:
        self._redis = redis_client
        self._logger = logger

    @property
    def client(self) -> aioredis.Redis:
        return self._redis

    async def get(self, key: str) -> Any | None:
        try:
            raw = await self._redis.get(key)
        except Exception as exc:
            self._logger.error("redis get error", cache_key=key, error=str(exc))
            return None
        if raw is None:
            return None
        try:
            return json.loads(raw)
        except (ValueError, TypeError) as exc:
            self._logger.error("failed to unmarshal cache", cache_key=key, error=str(exc))
            return None

    async def set(self, key: str, value: Any, ttl_seconds: int = DEFAULT_TTL) -> None:
        try:
            await self._redis.set(key, json.dumps(value, default=str), ex=ttl_seconds)
            self._logger.debug("cached data", cache_key=key, ttl=ttl_seconds)
        except Exception as exc:
            self._logger.error("failed to set cache", cache_key=key, error=str(exc))

    async def delete(self, *keys: str) -> None:
        try:
            if keys:
                await self._redis.delete(*keys)
        except Exception as exc:
            self._logger.error("failed to delete cache", error=str(exc))

    async def invalidate(self, pattern: str) -> int:
        """Delete all keys matching a glob pattern (SCAN-based)."""
        deleted = 0
        try:
            async for key in self._redis.scan_iter(match=pattern, count=1000):
                await self._redis.delete(key)
                deleted += 1
        except Exception as exc:
            self._logger.error("cache invalidate error", pattern=pattern, error=str(exc))
            return deleted
        self._logger.info("invalidated cache keys", pattern=pattern, count=deleted)
        return deleted

    async def clear_expired(self) -> int:
        """Best-effort sweep of expired keys (ClearExpired)."""
        swept = 0
        try:
            async for key in self._redis.scan_iter(match="*", count=1000):
                ttl = await self._redis.ttl(key)
                if ttl is not None and ttl < 0:
                    has_persist = await self._redis.persist(key)
                    if has_persist:  # key existed but had no TTL: leave it
                        continue
                swept += 1
        except Exception as exc:
            self._logger.error("cache sweep error", error=str(exc))
        return swept

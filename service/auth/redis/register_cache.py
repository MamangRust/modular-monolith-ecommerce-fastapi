"""Verification-code cache."""

from __future__ import annotations

from pkg.logger.logger import Logger
from service.auth.redis.common import register_verify_code_key
from shared.cache import CacheStore


class RegisterCacheImpl:
    def __init__(self, store: CacheStore, logger: Logger) -> None:
        self._store = store
        self._logger = logger

    async def set_verification_code_cache(
        self, email: str, code: str, ttl_seconds: int
    ) -> None:
        if not code:
            return
        await self._store.set_json(register_verify_code_key(email), code, ttl_seconds)


__all__ = ["RegisterCacheImpl"]

"""Review detail command cache invalidation. flushes the entire `review_detail:*` namespace on every mutation, so single wildcard invalidation."""

from __future__ import annotations

from pkg.logger.logger import Logger
from service.review_detail.redis.common import REVIEW_DETAIL_ALL_PATTERN
from shared.cache import CacheStore


class ReviewDetailCommandCacheImpl:
    def __init__(self, store: CacheStore, logger: Logger) -> None:
        self._store = store
        self._logger = logger

    async def delete_review_detail_cache(self, review_detail_id: int) -> int:
        return await self._store.invalidate(REVIEW_DETAIL_ALL_PATTERN)

    async def invalidate_review_detail_cache(self) -> int:
        return await self._store.invalidate(REVIEW_DETAIL_ALL_PATTERN)


__all__ = ["ReviewDetailCommandCacheImpl"]

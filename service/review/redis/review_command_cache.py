"""review command cache invalidation. NORMALISATION: deletes `review:%d`, `reviews:all`, `reviews:active` and `reviews:trashed`, none of which match the keys the query cache writes (`review:all:page:...`, `review:id:%d`,...), so the invalidation is a silent no-op. invalidates the whole `review:*` namespace on every mutation instead (matching the product repository's normalisation). The `review_id` argument is kept for signature."""

from __future__ import annotations

from pkg.logger.logger import Logger
from service.review.redis.common import REVIEW_NAMESPACE_PATTERN
from shared.cache import CacheStore


class ReviewCommandCacheImpl:
    def __init__(self, store: CacheStore, logger: Logger) -> None:
        self._store = store
        self._logger = logger

    async def delete_cached_review(self, review_id: int) -> int:
        return await self._store.invalidate(REVIEW_NAMESPACE_PATTERN)


__all__ = ["ReviewCommandCacheImpl"]

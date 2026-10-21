"""review cache bundle."""

from __future__ import annotations

from dataclasses import dataclass

from pkg.logger.logger import Logger
from service.review.redis.interfaces import ReviewCommandCache, ReviewQueryCache
from service.review.redis.review_command_cache import ReviewCommandCacheImpl
from service.review.redis.review_query_cache import ReviewQueryCacheImpl
from shared.cache import CacheStore


@dataclass(frozen=True)
class Mencache:
    review_query: ReviewQueryCache
    review_command: ReviewCommandCache


def new_mencache(store: CacheStore, logger: Logger) -> Mencache:
    return Mencache(
        review_query=ReviewQueryCacheImpl(store, logger),
        review_command=ReviewCommandCacheImpl(store, logger),
    )


__all__ = [
    "Mencache",
    "ReviewCommandCache",
    "ReviewQueryCache",
    "new_mencache",
]

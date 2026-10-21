"""Review detail service composition."""

from __future__ import annotations

from dataclasses import dataclass

from pkg.logger.logger import Logger
from service.review_detail.redis.review_detail_command_cache import (
    ReviewDetailCommandCacheImpl,
)
from service.review_detail.redis.review_detail_query_cache import (
    ReviewDetailQueryCacheImpl,
)
from service.review_detail.repository.repository import Repositories
from service.review_detail.service.interfaces import (
    ReviewDetailCommandService,
    ReviewDetailQueryService,
)
from service.review_detail.service.review_detail_command_service import (
    ReviewDetailCommandServiceImpl,
)
from service.review_detail.service.review_detail_query_service import (
    ReviewDetailQueryServiceImpl,
)
from shared.cache import CacheStore
from shared.observability import Observability

SERVICE_NAME = "review_detail-service"


@dataclass(frozen=True)
class Service:
    review_detail_query: ReviewDetailQueryService
    review_detail_command: ReviewDetailCommandService


def new_service(
    repos: Repositories,
    cache_store: CacheStore,
    logger: Logger,
) -> Service:
    obs = Observability(SERVICE_NAME, logger)
    return Service(
        review_detail_query=ReviewDetailQueryServiceImpl(
            repos.query, ReviewDetailQueryCacheImpl(cache_store, logger), logger, obs
        ),
        review_detail_command=ReviewDetailCommandServiceImpl(
            repos.command,
            repos.query,
            ReviewDetailCommandCacheImpl(cache_store, logger),
            logger,
            obs,
        ),
    )


__all__ = ["SERVICE_NAME", "Service", "new_service"]

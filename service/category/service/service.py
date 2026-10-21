"""Category service composition."""

from __future__ import annotations

from dataclasses import dataclass

from pkg.logger.logger import Logger
from service.category.redis.category_command_cache import CategoryCommandCacheImpl
from service.category.redis.category_query_cache import CategoryQueryCacheImpl
from service.category.redis.category_stats_by_id_cache import (
    CategoryStatsByIdCacheImpl,
)
from service.category.redis.category_stats_by_merchant_cache import (
    CategoryStatsByMerchantCacheImpl,
)
from service.category.redis.category_stats_cache import CategoryStatsCacheImpl
from service.category.repository.repository import Repositories
from service.category.service.category_command_service import CategoryCommandServiceImpl
from service.category.service.category_query_service import CategoryQueryServiceImpl
from service.category.service.category_stats_by_id_service import (
    CategoryStatsByIdServiceImpl,
)
from service.category.service.category_stats_by_merchant_service import (
    CategoryStatsByMerchantServiceImpl,
)
from service.category.service.category_stats_service import CategoryStatsServiceImpl
from service.category.service.interfaces import (
    CategoryCommandService,
    CategoryQueryService,
    CategoryStatsByIdService,
    CategoryStatsByMerchantService,
    CategoryStatsService,
)
from shared.cache import CacheStore
from shared.observability import Observability

SERVICE_NAME = "category-service"


@dataclass(frozen=True)
class Service:
    category_query: CategoryQueryService
    category_command: CategoryCommandService
    category_stats: CategoryStatsService
    category_stats_by_id: CategoryStatsByIdService
    category_stats_by_merchant: CategoryStatsByMerchantService


def new_service(
    repos: Repositories,
    cache_store: CacheStore,
    logger: Logger,
) -> Service:
    obs = Observability(SERVICE_NAME, logger)
    return Service(
        category_query=CategoryQueryServiceImpl(
            repos.query, CategoryQueryCacheImpl(cache_store, logger), logger, obs
        ),
        category_command=CategoryCommandServiceImpl(
            repos.command,
            repos.query,
            CategoryCommandCacheImpl(cache_store, logger),
            logger,
            obs,
        ),
        category_stats=CategoryStatsServiceImpl(
            repos.stats, CategoryStatsCacheImpl(cache_store, logger), logger, obs
        ),
        category_stats_by_id=CategoryStatsByIdServiceImpl(
            repos.stats_by_id,
            CategoryStatsByIdCacheImpl(cache_store, logger),
            logger,
            obs,
        ),
        category_stats_by_merchant=CategoryStatsByMerchantServiceImpl(
            repos.stats_by_merchant,
            CategoryStatsByMerchantCacheImpl(cache_store, logger),
            logger,
            obs,
        ),
    )


__all__ = ["SERVICE_NAME", "Service", "new_service"]

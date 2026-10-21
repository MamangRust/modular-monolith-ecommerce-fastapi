"""Banner service composition."""

from __future__ import annotations

from dataclasses import dataclass

from pkg.logger.logger import Logger
from service.banner.redis.banner_command_cache import BannerCommandCacheImpl
from service.banner.redis.banner_query_cache import BannerQueryCacheImpl
from service.banner.repository.repository import Repositories
from service.banner.service.banner_command_service import BannerCommandServiceImpl
from service.banner.service.banner_query_service import BannerQueryServiceImpl
from service.banner.service.interfaces import BannerCommandService, BannerQueryService
from shared.cache import CacheStore
from shared.observability import Observability

SERVICE_NAME = "banner-service"


@dataclass(frozen=True)
class Service:
    banner_query: BannerQueryService
    banner_command: BannerCommandService


def new_service(
    repos: Repositories,
    cache_store: CacheStore,
    logger: Logger,
) -> Service:
    obs = Observability(SERVICE_NAME, logger)
    return Service(
        banner_query=BannerQueryServiceImpl(
            repos.query, BannerQueryCacheImpl(cache_store, logger), logger, obs
        ),
        banner_command=BannerCommandServiceImpl(
            repos.command, BannerCommandCacheImpl(cache_store, logger), logger, obs
        ),
    )


__all__ = ["SERVICE_NAME", "Service", "new_service"]

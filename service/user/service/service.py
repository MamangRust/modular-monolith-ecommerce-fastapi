"""User service composition."""

from __future__ import annotations

from dataclasses import dataclass

from pkg.hash import Hasher
from pkg.logger.logger import Logger
from service.user.redis.user_command_cache import UserCommandCacheImpl
from service.user.redis.user_query_cache import UserQueryCacheImpl
from service.user.repository.repository import Repositories
from service.user.service.interfaces import UserCommandService, UserQueryService
from service.user.service.user_command_service import UserCommandServiceImpl
from service.user.service.user_query_service import UserQueryServiceImpl
from shared.cache import CacheStore
from shared.observability import Observability

SERVICE_NAME = "user-service"


@dataclass(frozen=True)
class Service:
    user_query: UserQueryService
    user_command: UserCommandService


def new_service(
    repos: Repositories,
    cache_store: CacheStore,
    logger: Logger,
    hasher: Hasher | None = None,
) -> Service:
    obs = Observability(SERVICE_NAME, logger)
    return Service(
        user_query=UserQueryServiceImpl(
            repos.query, UserQueryCacheImpl(cache_store, logger), logger, obs
        ),
        user_command=UserCommandServiceImpl(
            repos.query,
            repos.command,
            UserCommandCacheImpl(cache_store, logger),
            hasher or Hasher(),
            logger,
            obs,
        ),
    )


__all__ = ["SERVICE_NAME", "Service", "new_service"]

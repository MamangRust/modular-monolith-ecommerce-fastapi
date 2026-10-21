"""Role service composition."""

from __future__ import annotations

from dataclasses import dataclass

from pkg.logger.logger import Logger
from service.role.redis.role_command_cache import RoleCommandCacheImpl
from service.role.redis.role_query_cache import RoleQueryCacheImpl
from service.role.repository.repository import Repositories
from service.role.service.interfaces import RoleCommandService, RoleQueryService
from service.role.service.role_command_service import RoleCommandServiceImpl
from service.role.service.role_query_service import RoleQueryServiceImpl
from shared.cache import CacheStore
from shared.observability import Observability

SERVICE_NAME = "role-service"


@dataclass(frozen=True)
class Service:
    role_query: RoleQueryService
    role_command: RoleCommandService


def new_service(repos: Repositories, cache_store: CacheStore, logger: Logger) -> Service:
    obs = Observability(SERVICE_NAME, logger)
    return Service(
        role_query=RoleQueryServiceImpl(
            repos.query, RoleQueryCacheImpl(cache_store, logger), logger, obs
        ),
        role_command=RoleCommandServiceImpl(
            repos.command, RoleCommandCacheImpl(cache_store, logger), logger, obs
        ),
    )


__all__ = ["SERVICE_NAME", "Service", "new_service"]

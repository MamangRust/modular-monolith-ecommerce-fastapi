"""Order item service composition."""

from __future__ import annotations

from dataclasses import dataclass

from pkg.logger.logger import Logger
from service.order_item.redis.redis import new_mencache
from service.order_item.repository.repository import Repositories
from service.order_item.service.interfaces import (
    OrderItemCommandService,
    OrderItemQueryService,
)
from service.order_item.service.order_item_command_service import (
    OrderItemCommandServiceImpl,
)
from service.order_item.service.order_item_query_service import (
    OrderItemQueryServiceImpl,
)
from shared.cache import CacheStore
from shared.observability import Observability

# Underscore (not hyphen): `RedisSettings.resolve_for_service` strips the
# "-service" suffix and upper-cases the rest, so this resolves REDIS_DB_ORDER_ITEM.
SERVICE_NAME = "order_item-service"


@dataclass(frozen=True)
class Service:
    order_item_query: OrderItemQueryService
    order_item_command: OrderItemCommandService


def new_service(
    repos: Repositories,
    cache_store: CacheStore,
    logger: Logger,
) -> Service:
    obs = Observability(SERVICE_NAME, logger)
    mencache = new_mencache(cache_store, logger)
    return Service(
        order_item_query=OrderItemQueryServiceImpl(
            repos.query, mencache.query, logger, obs
        ),
        order_item_command=OrderItemCommandServiceImpl(
            repos.command, mencache.command, logger, obs
        ),
    )


__all__ = ["SERVICE_NAME", "Service", "new_service"]

"""Shipping address service composition."""

from __future__ import annotations

from dataclasses import dataclass

from pkg.logger.logger import Logger
from service.shipping_address.redis.redis import new_mencache
from service.shipping_address.repository.repository import Repositories
from service.shipping_address.service.interfaces import (
    ShippingAddressCommandService,
    ShippingAddressQueryService,
)
from service.shipping_address.service.shipping_address_command_service import (
    ShippingAddressCommandServiceImpl,
)
from service.shipping_address.service.shipping_address_query_service import (
    ShippingAddressQueryServiceImpl,
)
from shared.cache import CacheStore
from shared.observability import Observability

# Underscore (not hyphen): `RedisSettings.resolve_for_service` strips the
# "-service" suffix and upper-cases the rest, resolving REDIS_DB_SHIPPING_ADDRESS.
SERVICE_NAME = "shipping_address-service"


@dataclass(frozen=True)
class Service:
    shipping_address_query: ShippingAddressQueryService
    shipping_address_command: ShippingAddressCommandService


def new_service(
    repos: Repositories,
    cache_store: CacheStore,
    logger: Logger,
) -> Service:
    obs = Observability(SERVICE_NAME, logger)
    mencache = new_mencache(cache_store, logger)
    return Service(
        shipping_address_query=ShippingAddressQueryServiceImpl(
            repos.query, mencache.query, logger, obs
        ),
        shipping_address_command=ShippingAddressCommandServiceImpl(
            repos.command, mencache.command, logger, obs
        ),
    )


__all__ = ["SERVICE_NAME", "Service", "new_service"]

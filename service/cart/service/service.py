"""cart service composition."""

from __future__ import annotations

from dataclasses import dataclass

from pkg.logger.logger import Logger
from service.cart.redis import Mencache
from service.cart.repository.repository import Repositories
from service.cart.service.cart_command_service import CartCommandServiceImpl
from service.cart.service.cart_query_service import CartQueryServiceImpl
from service.cart.service.interfaces import (
    CartCommandService,
    CartQueryService,
)
from shared.observability import Observability

SERVICE_NAME = "cart-service"


@dataclass(frozen=True)
class Service:
    cart_query: CartQueryService
    cart_command: CartCommandService


def new_service(
    repos: Repositories,
    mencache: Mencache,
    logger: Logger,
) -> Service:
    obs = Observability(SERVICE_NAME, logger)
    return Service(
        cart_query=CartQueryServiceImpl(
            repos.cart_query,
            mencache.cart_query,
            logger,
            obs,
        ),
        cart_command=CartCommandServiceImpl(
            repos.cart_command,
            repos.product_query,
            repos.user_query,
            mencache.cart_command,
            logger,
            obs,
        ),
    )


__all__ = ["SERVICE_NAME", "Service", "new_service"]

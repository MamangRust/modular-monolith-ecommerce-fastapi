"""product service composition."""

from __future__ import annotations

from dataclasses import dataclass

from pkg.logger.logger import Logger
from service.product.redis import Mencache
from service.product.repository.repository import Repositories
from service.product.service.interfaces import (
    ProductCommandService,
    ProductQueryService,
)
from service.product.service.product_command_service import (
    ProductCommandServiceImpl,
)
from service.product.service.product_query_service import (
    ProductQueryServiceImpl,
)
from shared.observability import Observability

SERVICE_NAME = "product-service"


@dataclass(frozen=True)
class Service:
    product_query: ProductQueryService
    product_command: ProductCommandService


def new_service(
    repos: Repositories,
    mencache: Mencache,
    logger: Logger,
) -> Service:
    obs = Observability(SERVICE_NAME, logger)
    return Service(
        product_query=ProductQueryServiceImpl(
            repos.product_query,
            mencache.product_query,
            logger,
            obs,
        ),
        product_command=ProductCommandServiceImpl(
            repos.product_command,
            repos.product_query,
            repos.category_query,
            repos.merchant_query,
            mencache.product_command,
            logger,
            obs,
        ),
    )


__all__ = ["SERVICE_NAME", "Service", "new_service"]

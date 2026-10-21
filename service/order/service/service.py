"""order service composition."""

from __future__ import annotations

from dataclasses import dataclass

from pkg.logger.logger import Logger
from service.order.redis import Mencache
from service.order.repository.repository import Repositories
from service.order.service.interfaces import (
    OrderCommandService,
    OrderQueryService,
    OrderStatsByMerchantService,
    OrderStatsService,
)
from service.order.service.order_command_service import OrderCommandServiceImpl
from service.order.service.order_query_service import OrderQueryServiceImpl
from service.order.service.order_stats_by_merchant_service import (
    OrderStatsByMerchantServiceImpl,
)
from service.order.service.order_stats_service import OrderStatsServiceImpl
from shared.observability import Observability

SERVICE_NAME = "order-service"


@dataclass(frozen=True)
class Service:
    order_query: OrderQueryService
    order_command: OrderCommandService
    order_stats: OrderStatsService
    order_stats_by_merchant: OrderStatsByMerchantService


def new_service(
    repos: Repositories,
    mencache: Mencache,
    logger: Logger,
) -> Service:
    obs = Observability(SERVICE_NAME, logger)
    return Service(
        order_query=OrderQueryServiceImpl(
            repos.order_query,
            mencache.order_query,
            logger,
            obs,
        ),
        order_command=OrderCommandServiceImpl(
            user_query=repos.user_query,
            merchant_query=repos.merchant_query,
            product_query=repos.product_query,
            product_command=repos.product_command,
            order_query=repos.order_query,
            order_command=repos.order_command,
            order_item_query=repos.order_item_query,
            order_item_command=repos.order_item_command,
            shipping_address=repos.shipping_address,
            transaction_command=repos.transaction_command,
            shipping_query=repos.shipping_query,
            stock_reservation=repos.stock_reservation,
            cache=mencache.order_command,
            logger=logger,
            obs=obs,
        ),
        order_stats=OrderStatsServiceImpl(
            repos.order_stats,
            mencache.order_stats,
            logger,
            obs,
        ),
        order_stats_by_merchant=OrderStatsByMerchantServiceImpl(
            repos.order_stats_by_merchant,
            mencache.order_stats_by_merchant,
            logger,
            obs,
        ),
    )


__all__ = ["SERVICE_NAME", "Service", "new_service"]

"""order handler composition."""

from __future__ import annotations

from dataclasses import dataclass

from pkg.logger.logger import Logger
from service.order.handler.order_command import OrderCommandHandler
from service.order.handler.order_query import OrderQueryHandler
from service.order.handler.order_stats import OrderStatsHandler
from service.order.service.service import Service


@dataclass(frozen=True)
class Handler:
    order_query: OrderQueryHandler
    order_command: OrderCommandHandler
    order_stats: OrderStatsHandler


def new_handler(service: Service, logger: Logger) -> Handler:
    return Handler(
        order_query=OrderQueryHandler(service.order_query, logger),
        order_command=OrderCommandHandler(service.order_command, logger),
        order_stats=OrderStatsHandler(
            service.order_stats, service.order_stats_by_merchant, logger
        ),
    )


__all__ = ["Handler", "new_handler"]

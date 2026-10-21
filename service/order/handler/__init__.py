"""order handler layer."""

from __future__ import annotations

from service.order.handler.handler import Handler, new_handler
from service.order.handler.order_command import OrderCommandHandler
from service.order.handler.order_query import OrderQueryHandler
from service.order.handler.order_stats import OrderStatsHandler

__all__ = [
    "Handler",
    "OrderCommandHandler",
    "OrderQueryHandler",
    "OrderStatsHandler",
    "new_handler",
]

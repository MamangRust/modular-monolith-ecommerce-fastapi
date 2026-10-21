"""Order item handler composition."""

from __future__ import annotations

from dataclasses import dataclass

from pkg.logger.logger import Logger
from service.order_item.handler.command import OrderItemCommandHandler
from service.order_item.handler.query import OrderItemQueryHandler
from service.order_item.service.service import Service


@dataclass(frozen=True)
class Handler:
    order_item_query: OrderItemQueryHandler
    order_item_command: OrderItemCommandHandler


def new_handler(service: Service, logger: Logger) -> Handler:
    return Handler(
        order_item_query=OrderItemQueryHandler(service.order_item_query, logger),
        order_item_command=OrderItemCommandHandler(service.order_item_command, logger),
    )


__all__ = ["Handler", "new_handler"]

"""product handler composition."""

from __future__ import annotations

from dataclasses import dataclass

from pkg.logger.logger import Logger
from service.product.handler.product_command import ProductCommandHandler
from service.product.handler.product_query import ProductQueryHandler
from service.product.service.service import Service


@dataclass(frozen=True)
class Handler:
    product_query: ProductQueryHandler
    product_command: ProductCommandHandler


def new_handler(service: Service, logger: Logger) -> Handler:
    return Handler(
        product_query=ProductQueryHandler(service.product_query, logger),
        product_command=ProductCommandHandler(service.product_command, logger),
    )


__all__ = ["Handler", "new_handler"]

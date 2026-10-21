"""product handler layer."""

from __future__ import annotations

from service.product.handler.handler import Handler, new_handler
from service.product.handler.product_command import ProductCommandHandler
from service.product.handler.product_query import ProductQueryHandler

__all__ = [
    "Handler",
    "ProductCommandHandler",
    "ProductQueryHandler",
    "new_handler",
]

"""Shipping address handler package."""

from service.shipping_address.handler.command import ShippingCommandHandler
from service.shipping_address.handler.handler import Handler, new_handler
from service.shipping_address.handler.query import ShippingQueryHandler

__all__ = [
    "Handler",
    "ShippingCommandHandler",
    "ShippingQueryHandler",
    "new_handler",
]

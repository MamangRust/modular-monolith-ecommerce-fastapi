"""Gateway shipping address routes."""

from service.apigateway.handler.shipping_address.command import (
    router as command_router,
)
from service.apigateway.handler.shipping_address.handler import (
    ShippingAddressHandler,
)
from service.apigateway.handler.shipping_address.query import router as query_router

__all__ = ["ShippingAddressHandler", "command_router", "query_router"]

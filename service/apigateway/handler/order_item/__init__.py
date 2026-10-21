"""Gateway order item routes."""

from service.apigateway.handler.order_item.command import router as command_router
from service.apigateway.handler.order_item.handler import OrderItemHandler
from service.apigateway.handler.order_item.query import router as query_router

__all__ = ["OrderItemHandler", "command_router", "query_router"]

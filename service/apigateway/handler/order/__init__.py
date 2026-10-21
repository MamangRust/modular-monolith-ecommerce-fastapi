"""Gateway order routes."""

from service.apigateway.handler.order.command import router as command_router
from service.apigateway.handler.order.handler import OrderHandler
from service.apigateway.handler.order.query import router as query_router
from service.apigateway.handler.order.stats import router as stats_router

__all__ = ["OrderHandler", "command_router", "query_router", "stats_router"]

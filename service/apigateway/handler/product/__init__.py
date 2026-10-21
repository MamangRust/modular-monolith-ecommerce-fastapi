"""Gateway product routes."""

from service.apigateway.handler.product.command import router as command_router
from service.apigateway.handler.product.handler import ProductHandler
from service.apigateway.handler.product.query import router as query_router

__all__ = ["ProductHandler", "command_router", "query_router"]

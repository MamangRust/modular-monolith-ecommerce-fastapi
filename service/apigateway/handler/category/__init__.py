"""Gateway category routes."""

from service.apigateway.handler.category.command import router as command_router
from service.apigateway.handler.category.handler import CategoryHandler
from service.apigateway.handler.category.query import router as query_router
from service.apigateway.handler.category.stats import router as stats_router

__all__ = ["CategoryHandler", "command_router", "query_router", "stats_router"]

"""Gateway user routes."""

from service.apigateway.handler.user.command import router as command_router
from service.apigateway.handler.user.handler import UserHandler
from service.apigateway.handler.user.query import router as query_router

__all__ = ["UserHandler", "command_router", "query_router"]

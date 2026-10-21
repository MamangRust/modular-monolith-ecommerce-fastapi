"""Gateway role routes."""

from service.apigateway.handler.role.command import ROLE_COMMAND_ADMIN
from service.apigateway.handler.role.command import router as command_router
from service.apigateway.handler.role.handler import RoleHandler
from service.apigateway.handler.role.query import ROLE_QUERY_ADMIN
from service.apigateway.handler.role.query import router as query_router

__all__ = [
    "ROLE_COMMAND_ADMIN",
    "ROLE_QUERY_ADMIN",
    "RoleHandler",
    "command_router",
    "query_router",
]

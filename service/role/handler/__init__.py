"""Role gRPC handlers."""

from service.role.handler.command import RoleCommandHandler
from service.role.handler.handler import Handler, new_handler
from service.role.handler.interfaces import RoleCommandHandlerPort, RoleQueryHandlerPort
from service.role.handler.query import RoleQueryHandler

__all__ = [
    "Handler",
    "RoleCommandHandler",
    "RoleCommandHandlerPort",
    "RoleQueryHandler",
    "RoleQueryHandlerPort",
    "new_handler",
]

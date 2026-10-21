"""Role handler composition."""

from __future__ import annotations

from dataclasses import dataclass

from pkg.logger.logger import Logger
from service.role.handler.command import RoleCommandHandler
from service.role.handler.query import RoleQueryHandler
from service.role.service.service import Service


@dataclass(frozen=True)
class Handler:
    role_query: RoleQueryHandler
    role_command: RoleCommandHandler


def new_handler(service: Service, logger: Logger) -> Handler:
    return Handler(
        role_query=RoleQueryHandler(service.role_query, logger),
        role_command=RoleCommandHandler(service.role_command, logger),
    )


__all__ = ["Handler", "new_handler"]

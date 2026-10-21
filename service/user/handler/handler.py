"""User handler composition."""

from __future__ import annotations

from dataclasses import dataclass

from pkg.logger.logger import Logger
from service.user.handler.command import UserCommandHandler
from service.user.handler.query import UserQueryHandler
from service.user.service.service import Service


@dataclass(frozen=True)
class Handler:
    user_query: UserQueryHandler
    user_command: UserCommandHandler


def new_handler(service: Service, logger: Logger) -> Handler:
    return Handler(
        user_query=UserQueryHandler(service.user_query, logger),
        user_command=UserCommandHandler(service.user_command, logger),
    )


__all__ = ["Handler", "new_handler"]

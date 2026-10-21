"""Auth handler composition."""

from __future__ import annotations

from dataclasses import dataclass

from pkg.logger.logger import Logger
from service.auth.handler.auth import AuthHandler
from service.auth.service.service import Service


@dataclass(frozen=True)
class Handler:
    auth: AuthHandler


def new_handler(service: Service, logger: Logger) -> Handler:
    return Handler(
        auth=AuthHandler(
            service.register,
            service.login,
            service.password_reset,
            service.identify,
            logger,
        )
    )


__all__ = ["Handler", "new_handler"]

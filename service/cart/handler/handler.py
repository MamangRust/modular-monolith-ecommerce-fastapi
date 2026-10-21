"""cart handler composition."""

from __future__ import annotations

from dataclasses import dataclass

from pkg.logger.logger import Logger
from service.cart.handler.cart_command import CartCommandHandler
from service.cart.handler.cart_query import CartQueryHandler
from service.cart.service.service import Service


@dataclass(frozen=True)
class Handler:
    cart_query: CartQueryHandler
    cart_command: CartCommandHandler


def new_handler(service: Service, logger: Logger) -> Handler:
    return Handler(
        cart_query=CartQueryHandler(service.cart_query, logger),
        cart_command=CartCommandHandler(service.cart_command, logger),
    )


__all__ = ["Handler", "new_handler"]

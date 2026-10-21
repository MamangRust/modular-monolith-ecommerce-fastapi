"""Shipping address handler composition."""

from __future__ import annotations

from dataclasses import dataclass

from pkg.logger.logger import Logger
from service.shipping_address.handler.command import ShippingCommandHandler
from service.shipping_address.handler.query import ShippingQueryHandler
from service.shipping_address.service.service import Service


@dataclass(frozen=True)
class Handler:
    shipping_address_query: ShippingQueryHandler
    shipping_address_command: ShippingCommandHandler


def new_handler(service: Service, logger: Logger) -> Handler:
    return Handler(
        shipping_address_query=ShippingQueryHandler(
            service.shipping_address_query, logger
        ),
        shipping_address_command=ShippingCommandHandler(
            service.shipping_address_command, logger
        ),
    )


__all__ = ["Handler", "new_handler"]

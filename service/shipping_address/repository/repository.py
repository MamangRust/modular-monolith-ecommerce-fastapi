"""Shipping address repository composition."""

from __future__ import annotations

from dataclasses import dataclass

from pkg.database.database import Database
from service.shipping_address.repository.interfaces import (
    ShippingAddressCommandRepository,
    ShippingAddressQueryRepository,
)
from service.shipping_address.repository.shipping_address_command_repository import (
    ShippingAddressCommandRepositoryImpl,
)
from service.shipping_address.repository.shipping_address_query_repository import (
    ShippingAddressQueryRepositoryImpl,
)


@dataclass(frozen=True)
class Repositories:
    query: ShippingAddressQueryRepository
    command: ShippingAddressCommandRepository


def new_repositories(db: Database) -> Repositories:
    return Repositories(
        query=ShippingAddressQueryRepositoryImpl(db),
        command=ShippingAddressCommandRepositoryImpl(db),
    )


__all__ = ["Repositories", "new_repositories"]

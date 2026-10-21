"""Shipping address repository package."""

from service.shipping_address.repository.interfaces import (
    ShippingAddressCommandRepository,
    ShippingAddressQueryRepository,
)
from service.shipping_address.repository.repository import Repositories, new_repositories

__all__ = [
    "Repositories",
    "ShippingAddressCommandRepository",
    "ShippingAddressQueryRepository",
    "new_repositories",
]

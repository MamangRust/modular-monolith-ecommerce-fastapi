"""Shipping address service package."""

from service.shipping_address.service.interfaces import (
    ShippingAddressCommandService,
    ShippingAddressQueryService,
)
from service.shipping_address.service.service import SERVICE_NAME, Service, new_service

__all__ = [
    "SERVICE_NAME",
    "Service",
    "ShippingAddressCommandService",
    "ShippingAddressQueryService",
    "new_service",
]

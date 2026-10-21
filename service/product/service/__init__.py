"""product service layer."""

from __future__ import annotations

from service.product.service.interfaces import (
    ProductCommandService,
    ProductQueryService,
)
from service.product.service.product_command_service import (
    ProductCommandServiceImpl,
)
from service.product.service.product_query_service import (
    ProductQueryServiceImpl,
)
from service.product.service.service import SERVICE_NAME, Service, new_service

__all__ = [
    "SERVICE_NAME",
    "ProductCommandService",
    "ProductCommandServiceImpl",
    "ProductQueryService",
    "ProductQueryServiceImpl",
    "Service",
    "new_service",
]

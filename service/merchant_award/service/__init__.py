"""merchant_award service layer."""

from __future__ import annotations

from service.merchant_award.service.interfaces import (
    MerchantAwardCommandService,
    MerchantAwardQueryService,
)
from service.merchant_award.service.service import (
    SERVICE_NAME,
    Service,
    new_service,
)

__all__ = [
    "SERVICE_NAME",
    "MerchantAwardCommandService",
    "MerchantAwardQueryService",
    "Service",
    "new_service",
]

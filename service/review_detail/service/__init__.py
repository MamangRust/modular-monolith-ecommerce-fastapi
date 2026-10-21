"""Review detail service package."""

from service.review_detail.service.interfaces import (
    ReviewDetailCommandService,
    ReviewDetailQueryService,
)
from service.review_detail.service.service import SERVICE_NAME, Service, new_service

__all__ = [
    "SERVICE_NAME",
    "ReviewDetailCommandService",
    "ReviewDetailQueryService",
    "Service",
    "new_service",
]

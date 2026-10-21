"""User service package."""

from service.user.service.interfaces import UserCommandService, UserQueryService
from service.user.service.service import SERVICE_NAME, Service, new_service

__all__ = [
    "SERVICE_NAME",
    "Service",
    "UserCommandService",
    "UserQueryService",
    "new_service",
]

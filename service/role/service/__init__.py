"""Role services."""

from service.role.service.interfaces import RoleCommandService, RoleQueryService
from service.role.service.role_command_service import RoleCommandServiceImpl
from service.role.service.role_query_service import (
    RoleQueryServiceImpl,
    normalize_pagination,
)
from service.role.service.service import SERVICE_NAME, Service, new_service

__all__ = [
    "SERVICE_NAME",
    "RoleCommandService",
    "RoleCommandServiceImpl",
    "RoleQueryService",
    "RoleQueryServiceImpl",
    "Service",
    "new_service",
    "normalize_pagination",
]

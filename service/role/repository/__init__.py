"""Role repositories."""

from service.role.repository.interfaces import (
    RoleCommandRepository,
    RoleQueryRepository,
)
from service.role.repository.repository import Repositories, new_repositories
from service.role.repository.role_command_repository import RoleCommandRepositoryImpl
from service.role.repository.role_query_repository import RoleQueryRepositoryImpl

__all__ = [
    "Repositories",
    "RoleCommandRepository",
    "RoleCommandRepositoryImpl",
    "RoleQueryRepository",
    "RoleQueryRepositoryImpl",
    "new_repositories",
]

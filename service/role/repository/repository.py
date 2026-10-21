"""Role repository composition."""

from __future__ import annotations

from dataclasses import dataclass

from pkg.database.database import Database
from service.role.repository.interfaces import RoleCommandRepository, RoleQueryRepository
from service.role.repository.role_command_repository import RoleCommandRepositoryImpl
from service.role.repository.role_query_repository import RoleQueryRepositoryImpl


@dataclass(frozen=True)
class Repositories:
    query: RoleQueryRepository
    command: RoleCommandRepository


def new_repositories(db: Database) -> Repositories:
    return Repositories(
        query=RoleQueryRepositoryImpl(db),
        command=RoleCommandRepositoryImpl(db),
    )


__all__ = ["Repositories", "new_repositories"]

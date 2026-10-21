"""User repository composition."""

from __future__ import annotations

from dataclasses import dataclass

from pkg.database.database import Database
from service.user.repository.interfaces import (
    UserCommandRepository,
    UserQueryRepository,
)
from service.user.repository.user_command_repository import UserCommandRepositoryImpl
from service.user.repository.user_query_repository import UserQueryRepositoryImpl


@dataclass(frozen=True)
class Repositories:
    query: UserQueryRepository
    command: UserCommandRepository


def new_repositories(db: Database) -> Repositories:
    return Repositories(
        query=UserQueryRepositoryImpl(db),
        command=UserCommandRepositoryImpl(db),
    )


__all__ = ["Repositories", "new_repositories"]

"""Banner repository composition."""

from __future__ import annotations

from dataclasses import dataclass

from pkg.database.database import Database
from service.banner.repository.banner_command_repository import (
    BannerCommandRepositoryImpl,
)
from service.banner.repository.banner_query_repository import (
    BannerQueryRepositoryImpl,
)
from service.banner.repository.interfaces import (
    BannerCommandRepository,
    BannerQueryRepository,
)


@dataclass(frozen=True)
class Repositories:
    query: BannerQueryRepository
    command: BannerCommandRepository


def new_repositories(db: Database) -> Repositories:
    return Repositories(
        query=BannerQueryRepositoryImpl(db),
        command=BannerCommandRepositoryImpl(db),
    )


__all__ = ["Repositories", "new_repositories"]

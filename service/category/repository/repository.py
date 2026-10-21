"""Category repository composition."""

from __future__ import annotations

from dataclasses import dataclass

from pkg.database.database import Database
from service.category.repository.category_command_repository import (
    CategoryCommandRepositoryImpl,
)
from service.category.repository.category_query_repository import (
    CategoryQueryRepositoryImpl,
)
from service.category.repository.category_stats_by_id_repository import (
    CategoryStatsByIdRepositoryImpl,
)
from service.category.repository.category_stats_by_merchant_repository import (
    CategoryStatsByMerchantRepositoryImpl,
)
from service.category.repository.category_stats_repository import (
    CategoryStatsRepositoryImpl,
)
from service.category.repository.interfaces import (
    CategoryCommandRepository,
    CategoryQueryRepository,
    CategoryStatsByIdRepository,
    CategoryStatsByMerchantRepository,
    CategoryStatsRepository,
)


@dataclass(frozen=True)
class Repositories:
    query: CategoryQueryRepository
    command: CategoryCommandRepository
    stats: CategoryStatsRepository
    stats_by_id: CategoryStatsByIdRepository
    stats_by_merchant: CategoryStatsByMerchantRepository


def new_repositories(db: Database) -> Repositories:
    return Repositories(
        query=CategoryQueryRepositoryImpl(db),
        command=CategoryCommandRepositoryImpl(db),
        stats=CategoryStatsRepositoryImpl(db),
        stats_by_id=CategoryStatsByIdRepositoryImpl(db),
        stats_by_merchant=CategoryStatsByMerchantRepositoryImpl(db),
    )


__all__ = ["Repositories", "new_repositories"]

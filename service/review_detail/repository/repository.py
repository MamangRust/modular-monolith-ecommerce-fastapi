"""Review detail repository bundle."""

from __future__ import annotations

from dataclasses import dataclass

from pkg.database.database import Database
from service.review_detail.repository.interfaces import (
    ReviewDetailCommandRepository,
    ReviewDetailQueryRepository,
)
from service.review_detail.repository.review_detail_command_repository import (
    ReviewDetailCommandRepositoryImpl,
)
from service.review_detail.repository.review_detail_query_repository import (
    ReviewDetailQueryRepositoryImpl,
)


@dataclass(frozen=True)
class Repositories:
    query: ReviewDetailQueryRepository
    command: ReviewDetailCommandRepository


def new_repositories(db: Database) -> Repositories:
    return Repositories(
        query=ReviewDetailQueryRepositoryImpl(db),
        command=ReviewDetailCommandRepositoryImpl(db),
    )


__all__ = ["Repositories", "new_repositories"]

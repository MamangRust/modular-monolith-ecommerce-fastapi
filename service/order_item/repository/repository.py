"""Order item repository composition."""

from __future__ import annotations

from dataclasses import dataclass

from pkg.database.database import Database
from service.order_item.repository.interfaces import (
    OrderItemCommandRepository,
    OrderItemQueryRepository,
)
from service.order_item.repository.order_item_command_repository import (
    OrderItemCommandRepositoryImpl,
)
from service.order_item.repository.order_item_query_repository import (
    OrderItemQueryRepositoryImpl,
)


@dataclass(frozen=True)
class Repositories:
    query: OrderItemQueryRepository
    command: OrderItemCommandRepository


def new_repositories(db: Database) -> Repositories:
    return Repositories(
        query=OrderItemQueryRepositoryImpl(db),
        command=OrderItemCommandRepositoryImpl(db),
    )


__all__ = ["Repositories", "new_repositories"]

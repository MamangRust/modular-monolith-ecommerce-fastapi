"""review repository composition.

Review reaches two other domains: user and product (both via gRPC adapters). Both
adapters are consumed — the command service's `Create` validates the user and the
product before writing."""

from __future__ import annotations

from dataclasses import dataclass

import grpc.aio as grpc_aio

from pkg.adapter.product import ProductQueryAdapter
from pkg.adapter.user import UserQueryAdapter
from pkg.database.database import Database
from pkg.resilience.dependency_guard import DependencyGuard
from service.review.repository.interfaces import (
    ProductQueryRepository,
    ReviewCommandRepository,
    ReviewQueryRepository,
    UserQueryRepository,
)
from service.review.repository.review_command_repository import (
    ReviewCommandRepositoryImpl,
)
from service.review.repository.review_query_repository import ReviewQueryRepositoryImpl


@dataclass(frozen=True)
class GuardOptions:
    """Dependency guards for the review service. Review reaches the user and product services, so
 one guard each."""

    user: DependencyGuard | None = None
    product: DependencyGuard | None = None


@dataclass(frozen=True)
class Repositories:
    product_query: ProductQueryRepository
    review_query: ReviewQueryRepository
    user_query: UserQueryRepository
    review_command: ReviewCommandRepository


def new_repositories(
    db: Database,
    *,
    user_channel: grpc_aio.Channel,
    product_channel: grpc_aio.Channel,
    guards: GuardOptions,
) -> Repositories:
    return Repositories(
        product_query=ProductQueryAdapter(product_channel, guard=guards.product),
        review_query=ReviewQueryRepositoryImpl(db),
        user_query=UserQueryAdapter(user_channel, guard=guards.user),
        review_command=ReviewCommandRepositoryImpl(db),
    )


__all__ = ["GuardOptions", "Repositories", "new_repositories"]

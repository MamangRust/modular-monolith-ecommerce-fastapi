"""cart repository composition.

Cart reaches two other domains: user and product (both via gRPC adapters). Both
adapters are consumed — the command service's `Create` resolves the product
details and validates the user before writing."""

from __future__ import annotations

from dataclasses import dataclass

import grpc.aio as grpc_aio

from pkg.adapter.product import ProductQueryAdapter
from pkg.adapter.user import UserQueryAdapter
from pkg.database.database import Database
from pkg.resilience.dependency_guard import DependencyGuard
from service.cart.repository.cart_command_repository import (
    CartCommandRepositoryImpl,
)
from service.cart.repository.cart_query_repository import CartQueryRepositoryImpl
from service.cart.repository.interfaces import (
    CartCommandRepository,
    CartQueryRepository,
    ProductQueryRepository,
    UserQueryRepository,
)


@dataclass(frozen=True)
class GuardOptions:
    """Dependency guards for the cart service. Cart reaches the user and product services, so
 one guard each."""

    user: DependencyGuard | None = None
    product: DependencyGuard | None = None


@dataclass(frozen=True)
class Repositories:
    user_query: UserQueryRepository
    product_query: ProductQueryRepository
    cart_query: CartQueryRepository
    cart_command: CartCommandRepository


def new_repositories(
    db: Database,
    *,
    user_channel: grpc_aio.Channel,
    product_channel: grpc_aio.Channel,
    guards: GuardOptions,
) -> Repositories:
    return Repositories(
        user_query=UserQueryAdapter(user_channel, guard=guards.user),
        product_query=ProductQueryAdapter(product_channel, guard=guards.product),
        cart_query=CartQueryRepositoryImpl(db),
        cart_command=CartCommandRepositoryImpl(db),
    )


__all__ = ["GuardOptions", "Repositories", "new_repositories"]

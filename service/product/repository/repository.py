"""product repository composition.

Product reaches two other domains: category and merchant (both via gRPC
adapters). Unlike the merchant_* leaf domains, both adapters are consumed — the
command service's `Create`/`Update` validate the parent category and merchant
before writing."""

from __future__ import annotations

from dataclasses import dataclass

import grpc.aio as grpc_aio

from pkg.adapter.category import CategoryQueryAdapter
from pkg.adapter.merchant import MerchantQueryAdapter
from pkg.database.database import Database
from pkg.resilience.dependency_guard import DependencyGuard
from service.product.repository.interfaces import (
    CategoryQueryRepository,
    MerchantQueryRepository,
    ProductCommandRepository,
    ProductQueryRepository,
)
from service.product.repository.product_command_repository import (
    ProductCommandRepositoryImpl,
)
from service.product.repository.product_query_repository import (
    ProductQueryRepositoryImpl,
)


@dataclass(frozen=True)
class GuardOptions:
    """Dependency guards for the product service. Product reaches the category and merchant
 services, so one guard each."""

    category: DependencyGuard | None = None
    merchant: DependencyGuard | None = None


@dataclass(frozen=True)
class Repositories:
    category_query: CategoryQueryRepository
    merchant_query: MerchantQueryRepository
    product_query: ProductQueryRepository
    product_command: ProductCommandRepository


def new_repositories(
    db: Database,
    *,
    category_channel: grpc_aio.Channel,
    merchant_channel: grpc_aio.Channel,
    guards: GuardOptions,
) -> Repositories:
    return Repositories(
        category_query=CategoryQueryAdapter(category_channel, guard=guards.category),
        merchant_query=MerchantQueryAdapter(merchant_channel, guard=guards.merchant),
        product_query=ProductQueryRepositoryImpl(db),
        product_command=ProductCommandRepositoryImpl(db),
    )


__all__ = ["GuardOptions", "Repositories", "new_repositories"]

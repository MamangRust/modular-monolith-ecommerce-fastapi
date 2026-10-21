"""transaction repository composition. The five adapters reach user, merchant, order, order_item and shipping_address; the outbox is not a repository here — the command service enqueues events via `pkg.outbox.enqueue` inside its own database transaction (the shared outbox implementation, which the service re-implements per-domain)."""

from __future__ import annotations

from dataclasses import dataclass

import grpc.aio as grpc_aio

from pkg.adapter.merchant import MerchantQueryAdapter
from pkg.adapter.order import OrderQueryAdapter
from pkg.adapter.order_item import OrderItemQueryAdapter
from pkg.adapter.shipping_address import ShippingQueryAdapter
from pkg.adapter.user import UserQueryAdapter
from pkg.database.database import Database
from pkg.resilience.dependency_guard import DependencyGuard
from service.transaction.repository.interfaces import (
    MerchantQueryRepository,
    OrderItemRepository,
    OrderQueryRepository,
    ShippingAddressQueryRepository,
    TransactionCommandRepository,
    TransactionQueryRepository,
    TransactionStatsByMerchantRepository,
    TransactionStatsRepository,
    UserQueryRepository,
)
from service.transaction.repository.transaction_command_repository import (
    TransactionCommandRepositoryImpl,
)
from service.transaction.repository.transaction_query_repository import (
    TransactionQueryRepositoryImpl,
)
from service.transaction.repository.transaction_stats_by_merchant_repository import (
    TransactionStatsByMerchantRepositoryImpl,
)
from service.transaction.repository.transaction_stats_repository import (
    TransactionStatsRepositoryImpl,
)


@dataclass(frozen=True)
class GuardOptions:
    """Dependency guards for the transaction service. Transaction reaches five services."""

    user: DependencyGuard | None = None
    merchant: DependencyGuard | None = None
    order: DependencyGuard | None = None
    order_item: DependencyGuard | None = None
    shipping: DependencyGuard | None = None


@dataclass(frozen=True)
class Repositories:
    transaction_query: TransactionQueryRepository
    transaction_command: TransactionCommandRepository
    transaction_stats: TransactionStatsRepository
    transaction_stats_by_merchant: TransactionStatsByMerchantRepository
    user_query: UserQueryRepository
    merchant_query: MerchantQueryRepository
    order_query: OrderQueryRepository
    order_item: OrderItemRepository
    shipping_address: ShippingAddressQueryRepository


def new_repositories(
    db: Database,
    *,
    user_channel: grpc_aio.Channel,
    merchant_channel: grpc_aio.Channel,
    order_channel: grpc_aio.Channel,
    order_item_channel: grpc_aio.Channel,
    shipping_channel: grpc_aio.Channel,
    guards: GuardOptions,
) -> Repositories:
    return Repositories(
        transaction_query=TransactionQueryRepositoryImpl(db),
        transaction_command=TransactionCommandRepositoryImpl(db),
        transaction_stats=TransactionStatsRepositoryImpl(db),
        transaction_stats_by_merchant=TransactionStatsByMerchantRepositoryImpl(db),
        user_query=UserQueryAdapter(user_channel, guard=guards.user),
        merchant_query=MerchantQueryAdapter(merchant_channel, guard=guards.merchant),
        order_query=OrderQueryAdapter(order_channel, guard=guards.order),
        order_item=OrderItemQueryAdapter(
            order_item_channel, order_item_channel, guard=guards.order_item
        ),
        shipping_address=ShippingQueryAdapter(shipping_channel, guard=guards.shipping),
    )


__all__ = ["GuardOptions", "Repositories", "new_repositories"]

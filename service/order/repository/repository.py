"""order repository composition. The user, merchant and transaction adapters are constructed but never invoked by the service (dead wiring); the transaction adapter in particular has no live caller."""

from __future__ import annotations

from dataclasses import dataclass

import grpc.aio as grpc_aio

from pkg.adapter.merchant import MerchantQueryAdapter
from pkg.adapter.order_item import OrderItemCommandAdapter, OrderItemQueryAdapter
from pkg.adapter.product import ProductCommandAdapter, ProductQueryAdapter
from pkg.adapter.shipping_address import (
    ShippingCommandAdapter,
    ShippingQueryAdapter,
)
from pkg.adapter.transaction_command import TransactionCommandAdapter
from pkg.adapter.user import UserQueryAdapter
from pkg.database.database import Database
from pkg.resilience.dependency_guard import DependencyGuard
from service.order.repository.interfaces import (
    MerchantQueryRepository,
    OrderCommandRepository,
    OrderItemCommandRepository,
    OrderItemQueryRepository,
    OrderQueryRepository,
    OrderStatsByMerchantRepository,
    OrderStatsRepository,
    ProductCommandRepository,
    ProductQueryRepository,
    ShippingAddressCommandRepository,
    ShippingQueryRepository,
    StockReservationRepository,
    TransactionCommandRepository,
    UserQueryRepository,
)
from service.order.repository.order_command_repository import (
    OrderCommandRepositoryImpl,
)
from service.order.repository.order_query_repository import OrderQueryRepositoryImpl
from service.order.repository.order_stats_by_merchant_repository import (
    OrderStatsByMerchantRepositoryImpl,
)
from service.order.repository.order_stats_repository import OrderStatsRepositoryImpl
from service.order.repository.stock_reservation_repository import (
    StockReservationRepositoryImpl,
)


@dataclass(frozen=True)
class GuardOptions:
    """Dependency guards for the order service. Order reaches six services: user, merchant, product, order_item, shipping_address and transaction."""

    user: DependencyGuard | None = None
    merchant: DependencyGuard | None = None
    product: DependencyGuard | None = None
    order_item: DependencyGuard | None = None
    shipping: DependencyGuard | None = None
    transaction: DependencyGuard | None = None


@dataclass(frozen=True)
class Repositories:
    merchant_query: MerchantQueryRepository
    product_query: ProductQueryRepository
    product_command: ProductCommandRepository
    order_item_query: OrderItemQueryRepository
    order_item_command: OrderItemCommandRepository
    order_query: OrderQueryRepository
    order_command: OrderCommandRepository
    order_stats: OrderStatsRepository
    order_stats_by_merchant: OrderStatsByMerchantRepository
    user_query: UserQueryRepository
    shipping_address: ShippingAddressCommandRepository
    transaction_command: TransactionCommandRepository
    shipping_query: ShippingQueryRepository
    stock_reservation: StockReservationRepository


def new_repositories(
    db: Database,
    *,
    user_channel: grpc_aio.Channel,
    merchant_channel: grpc_aio.Channel,
    product_channel: grpc_aio.Channel,
    order_item_channel: grpc_aio.Channel,
    shipping_channel: grpc_aio.Channel,
    transaction_channel: grpc_aio.Channel,
    guards: GuardOptions,
) -> Repositories:
    return Repositories(
        merchant_query=MerchantQueryAdapter(
            merchant_channel, guard=guards.merchant
        ),
        product_query=ProductQueryAdapter(product_channel, guard=guards.product),
        product_command=ProductCommandAdapter(
            product_channel, guard=guards.product
        ),
        order_item_query=OrderItemQueryAdapter(
            order_item_channel,
            order_item_channel,
            guard=guards.order_item,
        ),
        order_item_command=OrderItemCommandAdapter(
            order_item_channel, guard=guards.order_item
        ),
        order_query=OrderQueryRepositoryImpl(db),
        order_command=OrderCommandRepositoryImpl(db),
        order_stats=OrderStatsRepositoryImpl(db),
        order_stats_by_merchant=OrderStatsByMerchantRepositoryImpl(db),
        user_query=UserQueryAdapter(user_channel, guard=guards.user),
        shipping_address=ShippingCommandAdapter(
            shipping_channel, guard=guards.shipping
        ),
        transaction_command=TransactionCommandAdapter(
            transaction_channel, guard=guards.transaction
        ),
        shipping_query=ShippingQueryAdapter(
            shipping_channel, guard=guards.shipping
        ),
        stock_reservation=StockReservationRepositoryImpl(db),
    )


__all__ = ["GuardOptions", "Repositories", "new_repositories"]

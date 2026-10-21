"""order repository layer."""

from __future__ import annotations

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
from service.order.repository.repository import (
    GuardOptions,
    Repositories,
    new_repositories,
)
from service.order.repository.stock_reservation_repository import (
    StockReservationRepositoryImpl,
)

__all__ = [
    "GuardOptions",
    "MerchantQueryRepository",
    "OrderCommandRepository",
    "OrderCommandRepositoryImpl",
    "OrderItemCommandRepository",
    "OrderItemQueryRepository",
    "OrderQueryRepository",
    "OrderQueryRepositoryImpl",
    "OrderStatsByMerchantRepository",
    "OrderStatsByMerchantRepositoryImpl",
    "OrderStatsRepository",
    "OrderStatsRepositoryImpl",
    "ProductCommandRepository",
    "ProductQueryRepository",
    "Repositories",
    "ShippingAddressCommandRepository",
    "ShippingQueryRepository",
    "StockReservationRepository",
    "StockReservationRepositoryImpl",
    "TransactionCommandRepository",
    "UserQueryRepository",
    "new_repositories",
]

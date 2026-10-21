"""order service"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Protocol

from pkg.database.schema.order import (
    GetMonthlyOrderRow,
    GetMonthlyTotalRevenueRow,
    GetOrderByIDRow,
    GetOrdersActiveRow,
    GetOrdersByMerchantRow,
    GetOrdersRow,
    GetOrdersTrashedRow,
    GetYearlyOrderRow,
    GetYearlyTotalRevenueRow,
    Order,
    OrderRow,
)
from shared.domain.requests.order import (
    CreateOrderRequest,
    FindAllOrder,
    FindAllOrderByMerchant,
    MonthOrderMerchant,
    MonthTotalRevenue,
    MonthTotalRevenueMerchant,
    UpdateOrderRequest,
    YearOrderMerchant,
    YearTotalRevenueMerchant,
)


@dataclass(frozen=True)
class ReconcileResult:
    """ReconcileResult — reservations repaired."""

    re_reserved: int = 0
    released: int = 0


@dataclass(frozen=True)
class CleanupResult:
    """CleanupResult — rows removed by retention."""

    released_reservations_removed: int = 0
    adjustments_removed: int = 0


class OrderQueryService(Protocol):
    async def find_all(self, request: FindAllOrder) -> tuple[list[GetOrdersRow], int]: ...

    async def find_active(
        self, request: FindAllOrder
    ) -> tuple[list[GetOrdersActiveRow], int]: ...

    async def find_trashed(
        self, request: FindAllOrder
    ) -> tuple[list[GetOrdersTrashedRow], int]: ...

    async def find_by_merchant(
        self, request: FindAllOrderByMerchant
    ) -> tuple[list[GetOrdersByMerchantRow], int]: ...

    async def find_by_id(self, order_id: int) -> GetOrderByIDRow: ...


class OrderCommandService(Protocol):
    async def create(self, request: CreateOrderRequest) -> OrderRow: ...

    async def update(self, request: UpdateOrderRequest) -> OrderRow: ...

    async def trash(self, order_id: int) -> Order: ...

    async def restore(self, order_id: int) -> Order: ...

    async def delete_permanent(self, order_id: int) -> bool: ...

    async def restore_all(self) -> bool: ...

    async def delete_all(self) -> bool: ...

    async def reconcile_stock_reservations(self) -> ReconcileResult: ...

    async def cleanup_idempotency_records(self, retention_days: int) -> CleanupResult: ...


class OrderStatsService(Protocol):
    async def find_monthly_total_revenue(
        self, request: MonthTotalRevenue
    ) -> list[GetMonthlyTotalRevenueRow]: ...

    async def find_yearly_total_revenue(
        self, year: int
    ) -> list[GetYearlyTotalRevenueRow]: ...

    async def find_monthly_order(self, year: int) -> list[GetMonthlyOrderRow]: ...

    async def find_yearly_order(self, year: int) -> list[GetYearlyOrderRow]: ...


class OrderStatsByMerchantService(Protocol):
    async def find_monthly_total_revenue_by_merchant(
        self, request: MonthTotalRevenueMerchant
    ) -> list[GetMonthlyTotalRevenueRow]: ...

    async def find_yearly_total_revenue_by_merchant(
        self, request: YearTotalRevenueMerchant
    ) -> list[GetYearlyTotalRevenueRow]: ...

    async def find_monthly_order_by_merchant(
        self, request: MonthOrderMerchant
    ) -> list[GetMonthlyOrderRow]: ...

    async def find_yearly_order_by_merchant(
        self, request: YearOrderMerchant
    ) -> list[GetYearlyOrderRow]: ...


__all__ = [
    "CleanupResult",
    "OrderCommandService",
    "OrderQueryService",
    "OrderStatsByMerchantService",
    "OrderStatsService",
    "ReconcileResult",
]

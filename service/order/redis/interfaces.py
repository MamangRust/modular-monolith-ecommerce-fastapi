"""order cache"""

from __future__ import annotations

from typing import Protocol

from pkg.database.schema.order import (
    GetMonthlyOrderRow,
    GetMonthlyTotalRevenueRow,
    GetOrdersActiveRow,
    GetOrdersByMerchantRow,
    GetOrdersRow,
    GetOrdersTrashedRow,
    GetYearlyOrderRow,
    GetYearlyTotalRevenueRow,
    OrderRow,
)
from shared.domain.requests.order import (
    FindAllOrder,
    FindAllOrderByMerchant,
    MonthOrderMerchant,
    MonthTotalRevenue,
    MonthTotalRevenueMerchant,
    YearOrderMerchant,
    YearTotalRevenueMerchant,
)


class OrderQueryCache(Protocol):
    async def get_all(
        self, request: FindAllOrder
    ) -> tuple[list[GetOrdersRow], int] | None: ...

    async def set_all(
        self, request: FindAllOrder, rows: list[GetOrdersRow], total: int
    ) -> None: ...

    async def get_active(
        self, request: FindAllOrder
    ) -> tuple[list[GetOrdersActiveRow], int] | None: ...

    async def set_active(
        self, request: FindAllOrder, rows: list[GetOrdersActiveRow], total: int
    ) -> None: ...

    async def get_trashed(
        self, request: FindAllOrder
    ) -> tuple[list[GetOrdersTrashedRow], int] | None: ...

    async def set_trashed(
        self, request: FindAllOrder, rows: list[GetOrdersTrashedRow], total: int
    ) -> None: ...

    async def get_by_merchant(
        self, request: FindAllOrderByMerchant
    ) -> tuple[list[GetOrdersByMerchantRow], int] | None: ...

    async def set_by_merchant(
        self,
        request: FindAllOrderByMerchant,
        rows: list[GetOrdersByMerchantRow],
        total: int,
    ) -> None: ...

    async def get_by_id(self, order_id: int) -> OrderRow | None: ...

    async def set_by_id(self, row: OrderRow) -> None: ...


class OrderCommandCache(Protocol):
    async def delete_order_cache(self, order_id: int) -> int: ...

    async def invalidate_order_cache(self) -> int: ...


class OrderStatsCache(Protocol):
    async def get_monthly_total_revenue(
        self, request: MonthTotalRevenue
    ) -> list[GetMonthlyTotalRevenueRow] | None: ...

    async def set_monthly_total_revenue(
        self, request: MonthTotalRevenue, rows: list[GetMonthlyTotalRevenueRow]
    ) -> None: ...

    async def get_yearly_total_revenue(
        self, year: int
    ) -> list[GetYearlyTotalRevenueRow] | None: ...

    async def set_yearly_total_revenue(
        self, year: int, rows: list[GetYearlyTotalRevenueRow]
    ) -> None: ...

    async def get_monthly_order(self, year: int) -> list[GetMonthlyOrderRow] | None: ...

    async def set_monthly_order(
        self, year: int, rows: list[GetMonthlyOrderRow]
    ) -> None: ...

    async def get_yearly_order(self, year: int) -> list[GetYearlyOrderRow] | None: ...

    async def set_yearly_order(
        self, year: int, rows: list[GetYearlyOrderRow]
    ) -> None: ...


class OrderStatsByMerchantCache(Protocol):
    async def get_monthly_total_revenue_by_merchant(
        self, request: MonthTotalRevenueMerchant
    ) -> list[GetMonthlyTotalRevenueRow] | None: ...

    async def set_monthly_total_revenue_by_merchant(
        self,
        request: MonthTotalRevenueMerchant,
        rows: list[GetMonthlyTotalRevenueRow],
    ) -> None: ...

    async def get_yearly_total_revenue_by_merchant(
        self, request: YearTotalRevenueMerchant
    ) -> list[GetYearlyTotalRevenueRow] | None: ...

    async def set_yearly_total_revenue_by_merchant(
        self,
        request: YearTotalRevenueMerchant,
        rows: list[GetYearlyTotalRevenueRow],
    ) -> None: ...

    async def get_monthly_order_by_merchant(
        self, request: MonthOrderMerchant
    ) -> list[GetMonthlyOrderRow] | None: ...

    async def set_monthly_order_by_merchant(
        self, request: MonthOrderMerchant, rows: list[GetMonthlyOrderRow]
    ) -> None: ...

    async def get_yearly_order_by_merchant(
        self, request: YearOrderMerchant
    ) -> list[GetYearlyOrderRow] | None: ...

    async def set_yearly_order_by_merchant(
        self, request: YearOrderMerchant, rows: list[GetYearlyOrderRow]
    ) -> None: ...


__all__ = [
    "OrderCommandCache",
    "OrderQueryCache",
    "OrderStatsByMerchantCache",
    "OrderStatsCache",
]

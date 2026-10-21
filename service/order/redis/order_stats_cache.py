"""order stats cache. Each stats result is a plain JSON array (marshals `&[]*db.Row`), unlike the query cache's `{data, total_records}` envelope. setters return early on a nil slice; the Python repositories always hand back a list (possibly empty), so the guard is documented but not reproduced."""

from __future__ import annotations

from collections.abc import Callable
from typing import Any

from pkg.database.schema.order import (
    GetMonthlyOrderRow,
    GetMonthlyTotalRevenueRow,
    GetYearlyOrderRow,
    GetYearlyTotalRevenueRow,
)
from pkg.logger.logger import Logger
from service.order.redis.cache import (
    monthly_order_row_from_dict,
    monthly_order_row_to_dict,
    monthly_total_revenue_row_from_dict,
    monthly_total_revenue_row_to_dict,
    yearly_order_row_from_dict,
    yearly_order_row_to_dict,
    yearly_total_revenue_row_from_dict,
    yearly_total_revenue_row_to_dict,
)
from service.order.redis.common import (
    TTL_DEFAULT,
    order_monthly_order_key,
    order_monthly_total_revenue_key,
    order_yearly_order_key,
    order_yearly_total_revenue_key,
)
from shared.cache import CacheStore
from shared.domain.requests.order import MonthTotalRevenue


def _decode[T](
    payload: Any, from_dict: Callable[[dict[str, Any]], T]
) -> list[T] | None:
    if not isinstance(payload, list):
        return None
    return [from_dict(item) for item in payload]


class OrderStatsCacheImpl:
    def __init__(self, store: CacheStore, logger: Logger) -> None:
        self._store = store
        self._logger = logger

    # ---- MonthlyTotalRevenue ----

    async def get_monthly_total_revenue(
        self, request: MonthTotalRevenue
    ) -> list[GetMonthlyTotalRevenueRow] | None:
        payload = await self._store.get_json(
            order_monthly_total_revenue_key(request.month, request.year)
        )
        return _decode(payload, monthly_total_revenue_row_from_dict)

    async def set_monthly_total_revenue(
        self, request: MonthTotalRevenue, rows: list[GetMonthlyTotalRevenueRow]
    ) -> None:
        await self._store.set_json(
            order_monthly_total_revenue_key(request.month, request.year),
            [monthly_total_revenue_row_to_dict(row) for row in rows],
            TTL_DEFAULT,
        )

    # ---- YearlyTotalRevenue ----

    async def get_yearly_total_revenue(
        self, year: int
    ) -> list[GetYearlyTotalRevenueRow] | None:
        payload = await self._store.get_json(order_yearly_total_revenue_key(year))
        return _decode(payload, yearly_total_revenue_row_from_dict)

    async def set_yearly_total_revenue(
        self, year: int, rows: list[GetYearlyTotalRevenueRow]
    ) -> None:
        await self._store.set_json(
            order_yearly_total_revenue_key(year),
            [yearly_total_revenue_row_to_dict(row) for row in rows],
            TTL_DEFAULT,
        )

    # ---- MonthlyOrder ----

    async def get_monthly_order(self, year: int) -> list[GetMonthlyOrderRow] | None:
        payload = await self._store.get_json(order_monthly_order_key(year))
        return _decode(payload, monthly_order_row_from_dict)

    async def set_monthly_order(
        self, year: int, rows: list[GetMonthlyOrderRow]
    ) -> None:
        await self._store.set_json(
            order_monthly_order_key(year),
            [monthly_order_row_to_dict(row) for row in rows],
            TTL_DEFAULT,
        )

    # ---- YearlyOrder ----

    async def get_yearly_order(self, year: int) -> list[GetYearlyOrderRow] | None:
        payload = await self._store.get_json(order_yearly_order_key(year))
        return _decode(payload, yearly_order_row_from_dict)

    async def set_yearly_order(
        self, year: int, rows: list[GetYearlyOrderRow]
    ) -> None:
        await self._store.set_json(
            order_yearly_order_key(year),
            [yearly_order_row_to_dict(row) for row in rows],
            TTL_DEFAULT,
        )


__all__ = ["OrderStatsCacheImpl"]

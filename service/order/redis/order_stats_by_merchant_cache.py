"""order stats-by-merchant cache.

Same JSON-array shapes as the global stats cache; only the keys (merchant-scoped)
and the request dataclasses differ. The row aliases
(`GetMonthlyTotalRevenueByMerchantRow`,...) are structurally identical to the
global row classes, so the shared encoders are reused."""

from __future__ import annotations

from collections.abc import Callable
from typing import Any

from pkg.database.schema.order import (
    GetMonthlyOrderByMerchantRow,
    GetMonthlyTotalRevenueByMerchantRow,
    GetYearlyOrderByMerchantRow,
    GetYearlyTotalRevenueByMerchantRow,
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
    order_monthly_order_by_merchant_key,
    order_monthly_total_revenue_by_merchant_key,
    order_yearly_order_by_merchant_key,
    order_yearly_total_revenue_by_merchant_key,
)
from shared.cache import CacheStore
from shared.domain.requests.order import (
    MonthOrderMerchant,
    MonthTotalRevenueMerchant,
    YearOrderMerchant,
    YearTotalRevenueMerchant,
)


def _decode[T](
    payload: Any, from_dict: Callable[[dict[str, Any]], T]
) -> list[T] | None:
    if not isinstance(payload, list):
        return None
    return [from_dict(item) for item in payload]


class OrderStatsByMerchantCacheImpl:
    def __init__(self, store: CacheStore, logger: Logger) -> None:
        self._store = store
        self._logger = logger

    # ---- MonthlyTotalRevenue ----

    async def get_monthly_total_revenue_by_merchant(
        self, request: MonthTotalRevenueMerchant
    ) -> list[GetMonthlyTotalRevenueByMerchantRow] | None:
        payload = await self._store.get_json(
            order_monthly_total_revenue_by_merchant_key(
                request.merchant_id, request.month, request.year
            )
        )
        return _decode(payload, monthly_total_revenue_row_from_dict)

    async def set_monthly_total_revenue_by_merchant(
        self,
        request: MonthTotalRevenueMerchant,
        rows: list[GetMonthlyTotalRevenueByMerchantRow],
    ) -> None:
        await self._store.set_json(
            order_monthly_total_revenue_by_merchant_key(
                request.merchant_id, request.month, request.year
            ),
            [monthly_total_revenue_row_to_dict(row) for row in rows],
            TTL_DEFAULT,
        )

    # ---- YearlyTotalRevenue ----

    async def get_yearly_total_revenue_by_merchant(
        self, request: YearTotalRevenueMerchant
    ) -> list[GetYearlyTotalRevenueByMerchantRow] | None:
        payload = await self._store.get_json(
            order_yearly_total_revenue_by_merchant_key(
                request.merchant_id, request.year
            )
        )
        return _decode(payload, yearly_total_revenue_row_from_dict)

    async def set_yearly_total_revenue_by_merchant(
        self,
        request: YearTotalRevenueMerchant,
        rows: list[GetYearlyTotalRevenueByMerchantRow],
    ) -> None:
        await self._store.set_json(
            order_yearly_total_revenue_by_merchant_key(
                request.merchant_id, request.year
            ),
            [yearly_total_revenue_row_to_dict(row) for row in rows],
            TTL_DEFAULT,
        )

    # ---- MonthlyOrder ----

    async def get_monthly_order_by_merchant(
        self, request: MonthOrderMerchant
    ) -> list[GetMonthlyOrderByMerchantRow] | None:
        payload = await self._store.get_json(
            order_monthly_order_by_merchant_key(request.merchant_id, request.year)
        )
        return _decode(payload, monthly_order_row_from_dict)

    async def set_monthly_order_by_merchant(
        self, request: MonthOrderMerchant, rows: list[GetMonthlyOrderByMerchantRow]
    ) -> None:
        await self._store.set_json(
            order_monthly_order_by_merchant_key(request.merchant_id, request.year),
            [monthly_order_row_to_dict(row) for row in rows],
            TTL_DEFAULT,
        )

    # ---- YearlyOrder ----

    async def get_yearly_order_by_merchant(
        self, request: YearOrderMerchant
    ) -> list[GetYearlyOrderByMerchantRow] | None:
        payload = await self._store.get_json(
            order_yearly_order_by_merchant_key(request.merchant_id, request.year)
        )
        return _decode(payload, yearly_order_row_from_dict)

    async def set_yearly_order_by_merchant(
        self, request: YearOrderMerchant, rows: list[GetYearlyOrderByMerchantRow]
    ) -> None:
        await self._store.set_json(
            order_yearly_order_by_merchant_key(request.merchant_id, request.year),
            [yearly_order_row_to_dict(row) for row in rows],
            TTL_DEFAULT,
        )


__all__ = ["OrderStatsByMerchantCacheImpl"]

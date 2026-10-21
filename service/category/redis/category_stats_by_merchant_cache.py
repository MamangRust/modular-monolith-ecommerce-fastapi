"""Category stats-by-merchant cache."""

from __future__ import annotations

from pkg.database.schema.category import (
    GetMonthlyCategoryByMerchantRow,
    GetMonthlyTotalPriceByMerchantRow,
    GetYearlyCategoryByMerchantRow,
    GetYearlyTotalPriceByMerchantRow,
)
from pkg.logger.logger import Logger
from service.category.redis.cache import (
    stats_rows_from_payload,
    stats_rows_to_payload,
)
from service.category.redis.common import (
    TTL_DEFAULT,
    stats_bymerchant_month_price_key,
    stats_bymerchant_month_total_price_key,
    stats_bymerchant_year_price_key,
    stats_bymerchant_year_total_price_key,
)
from shared.cache import CacheStore


class CategoryStatsByMerchantCacheImpl:
    def __init__(self, store: CacheStore, logger: Logger) -> None:
        self._store = store
        self._logger = logger

    async def get_month_total_price_by_merchant(
        self, merchant_id: int, year: int, month: int
    ) -> list[GetMonthlyTotalPriceByMerchantRow] | None:
        payload = await self._store.get_json(
            stats_bymerchant_month_total_price_key(merchant_id, month, year)
        )
        return stats_rows_from_payload(GetMonthlyTotalPriceByMerchantRow, payload)

    async def set_month_total_price_by_merchant(
        self,
        merchant_id: int,
        year: int,
        month: int,
        rows: list[GetMonthlyTotalPriceByMerchantRow],
    ) -> None:
        await self._store.set_json(
            stats_bymerchant_month_total_price_key(merchant_id, month, year),
            stats_rows_to_payload(rows),
            TTL_DEFAULT,
        )

    async def get_year_total_price_by_merchant(
        self, merchant_id: int, year: int
    ) -> list[GetYearlyTotalPriceByMerchantRow] | None:
        payload = await self._store.get_json(
            stats_bymerchant_year_total_price_key(merchant_id, year)
        )
        return stats_rows_from_payload(GetYearlyTotalPriceByMerchantRow, payload)

    async def set_year_total_price_by_merchant(
        self,
        merchant_id: int,
        year: int,
        rows: list[GetYearlyTotalPriceByMerchantRow],
    ) -> None:
        await self._store.set_json(
            stats_bymerchant_year_total_price_key(merchant_id, year),
            stats_rows_to_payload(rows),
            TTL_DEFAULT,
        )

    async def get_month_price_by_merchant(
        self, merchant_id: int, year: int
    ) -> list[GetMonthlyCategoryByMerchantRow] | None:
        payload = await self._store.get_json(
            stats_bymerchant_month_price_key(merchant_id, year)
        )
        return stats_rows_from_payload(GetMonthlyCategoryByMerchantRow, payload)

    async def set_month_price_by_merchant(
        self,
        merchant_id: int,
        year: int,
        rows: list[GetMonthlyCategoryByMerchantRow],
    ) -> None:
        await self._store.set_json(
            stats_bymerchant_month_price_key(merchant_id, year),
            stats_rows_to_payload(rows),
            TTL_DEFAULT,
        )

    async def get_year_price_by_merchant(
        self, merchant_id: int, year: int
    ) -> list[GetYearlyCategoryByMerchantRow] | None:
        payload = await self._store.get_json(
            stats_bymerchant_year_price_key(merchant_id, year)
        )
        return stats_rows_from_payload(GetYearlyCategoryByMerchantRow, payload)

    async def set_year_price_by_merchant(
        self,
        merchant_id: int,
        year: int,
        rows: list[GetYearlyCategoryByMerchantRow],
    ) -> None:
        await self._store.set_json(
            stats_bymerchant_year_price_key(merchant_id, year),
            stats_rows_to_payload(rows),
            TTL_DEFAULT,
        )


__all__ = ["CategoryStatsByMerchantCacheImpl"]

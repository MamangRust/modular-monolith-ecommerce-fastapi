"""Category stats-by-id cache."""

from __future__ import annotations

from pkg.database.schema.category import (
    GetMonthlyCategoryByIdRow,
    GetMonthlyTotalPriceByIdRow,
    GetYearlyCategoryByIdRow,
    GetYearlyTotalPriceByIdRow,
)
from pkg.logger.logger import Logger
from service.category.redis.cache import (
    stats_rows_from_payload,
    stats_rows_to_payload,
)
from service.category.redis.common import (
    TTL_DEFAULT,
    stats_byid_month_price_key,
    stats_byid_month_total_price_key,
    stats_byid_year_price_key,
    stats_byid_year_total_price_key,
)
from shared.cache import CacheStore


class CategoryStatsByIdCacheImpl:
    def __init__(self, store: CacheStore, logger: Logger) -> None:
        self._store = store
        self._logger = logger

    async def get_month_total_price_by_id(
        self, category_id: int, year: int, month: int
    ) -> list[GetMonthlyTotalPriceByIdRow] | None:
        payload = await self._store.get_json(
            stats_byid_month_total_price_key(category_id, month, year)
        )
        return stats_rows_from_payload(GetMonthlyTotalPriceByIdRow, payload)

    async def set_month_total_price_by_id(
        self,
        category_id: int,
        year: int,
        month: int,
        rows: list[GetMonthlyTotalPriceByIdRow],
    ) -> None:
        await self._store.set_json(
            stats_byid_month_total_price_key(category_id, month, year),
            stats_rows_to_payload(rows),
            TTL_DEFAULT,
        )

    async def get_year_total_price_by_id(
        self, category_id: int, year: int
    ) -> list[GetYearlyTotalPriceByIdRow] | None:
        payload = await self._store.get_json(
            stats_byid_year_total_price_key(category_id, year)
        )
        return stats_rows_from_payload(GetYearlyTotalPriceByIdRow, payload)

    async def set_year_total_price_by_id(
        self,
        category_id: int,
        year: int,
        rows: list[GetYearlyTotalPriceByIdRow],
    ) -> None:
        await self._store.set_json(
            stats_byid_year_total_price_key(category_id, year),
            stats_rows_to_payload(rows),
            TTL_DEFAULT,
        )

    async def get_month_price_by_id(
        self, category_id: int, year: int
    ) -> list[GetMonthlyCategoryByIdRow] | None:
        payload = await self._store.get_json(
            stats_byid_month_price_key(category_id, year)
        )
        return stats_rows_from_payload(GetMonthlyCategoryByIdRow, payload)

    async def set_month_price_by_id(
        self,
        category_id: int,
        year: int,
        rows: list[GetMonthlyCategoryByIdRow],
    ) -> None:
        await self._store.set_json(
            stats_byid_month_price_key(category_id, year),
            stats_rows_to_payload(rows),
            TTL_DEFAULT,
        )

    async def get_year_price_by_id(
        self, category_id: int, year: int
    ) -> list[GetYearlyCategoryByIdRow] | None:
        payload = await self._store.get_json(
            stats_byid_year_price_key(category_id, year)
        )
        return stats_rows_from_payload(GetYearlyCategoryByIdRow, payload)

    async def set_year_price_by_id(
        self,
        category_id: int,
        year: int,
        rows: list[GetYearlyCategoryByIdRow],
    ) -> None:
        await self._store.set_json(
            stats_byid_year_price_key(category_id, year),
            stats_rows_to_payload(rows),
            TTL_DEFAULT,
        )


__all__ = ["CategoryStatsByIdCacheImpl"]

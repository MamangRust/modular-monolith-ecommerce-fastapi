"""Category stats cache. the key `<scope>:year:%d` is reused for both the year-total-price and the year-price payloads, so they overwrite each other; splits them (see `redis/common.py` and the)."""

from __future__ import annotations

from pkg.database.schema.category import (
    GetMonthlyCategoryRow,
    GetMonthlyTotalPriceRow,
    GetYearlyCategoryRow,
    GetYearlyTotalPriceRow,
)
from pkg.logger.logger import Logger
from service.category.redis.cache import (
    stats_rows_from_payload,
    stats_rows_to_payload,
)
from service.category.redis.common import (
    TTL_DEFAULT,
    stats_month_price_key,
    stats_month_total_price_key,
    stats_year_price_key,
    stats_year_total_price_key,
)
from shared.cache import CacheStore


class CategoryStatsCacheImpl:
    def __init__(self, store: CacheStore, logger: Logger) -> None:
        self._store = store
        self._logger = logger

    async def get_month_total_price(
        self, year: int, month: int
    ) -> list[GetMonthlyTotalPriceRow] | None:
        payload = await self._store.get_json(stats_month_total_price_key(month, year))
        return stats_rows_from_payload(GetMonthlyTotalPriceRow, payload)

    async def set_month_total_price(
        self, year: int, month: int, rows: list[GetMonthlyTotalPriceRow]
    ) -> None:
        await self._store.set_json(
            stats_month_total_price_key(month, year),
            stats_rows_to_payload(rows),
            TTL_DEFAULT,
        )

    async def get_year_total_price(
        self, year: int
    ) -> list[GetYearlyTotalPriceRow] | None:
        payload = await self._store.get_json(stats_year_total_price_key(year))
        return stats_rows_from_payload(GetYearlyTotalPriceRow, payload)

    async def set_year_total_price(
        self, year: int, rows: list[GetYearlyTotalPriceRow]
    ) -> None:
        await self._store.set_json(
            stats_year_total_price_key(year),
            stats_rows_to_payload(rows),
            TTL_DEFAULT,
        )

    async def get_month_price(self, year: int) -> list[GetMonthlyCategoryRow] | None:
        payload = await self._store.get_json(stats_month_price_key(year))
        return stats_rows_from_payload(GetMonthlyCategoryRow, payload)

    async def set_month_price(
        self, year: int, rows: list[GetMonthlyCategoryRow]
    ) -> None:
        await self._store.set_json(
            stats_month_price_key(year),
            stats_rows_to_payload(rows),
            TTL_DEFAULT,
        )

    async def get_year_price(self, year: int) -> list[GetYearlyCategoryRow] | None:
        payload = await self._store.get_json(stats_year_price_key(year))
        return stats_rows_from_payload(GetYearlyCategoryRow, payload)

    async def set_year_price(self, year: int, rows: list[GetYearlyCategoryRow]) -> None:
        await self._store.set_json(
            stats_year_price_key(year),
            stats_rows_to_payload(rows),
            TTL_DEFAULT,
        )


__all__ = ["CategoryStatsCacheImpl"]

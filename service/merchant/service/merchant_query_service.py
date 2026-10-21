"""Merchant query service. Reads are cache-first; a miss loads from the DB and populates the cache. The `total_count` comes from the first row's window column. Repository failures propagate unchanged (forwards them through `errorhandler.HandleError`, which returns the error), so the wire code matches the repository error."""

from __future__ import annotations

from pkg.database.schema.merchant import (
    GetMerchantByIDRow,
    GetMerchantsActiveRow,
    GetMerchantsRow,
    GetMerchantsTrashedRow,
)
from pkg.logger.logger import Logger
from service.merchant.redis.interfaces import MerchantQueryCache
from service.merchant.repository.interfaces import MerchantQueryRepository
from shared.observability import Observability


class MerchantQueryServiceImpl:
    def __init__(
        self,
        repo: MerchantQueryRepository,
        cache: MerchantQueryCache,
        logger: Logger,
        obs: Observability,
    ) -> None:
        self._repo = repo
        self._cache = cache
        self._logger = logger
        self._obs = obs

    async def find_all(
        self, search: str, page: int, page_size: int
    ) -> tuple[list[GetMerchantsRow], int]:
        with self._obs.span("merchant.query.find_all", page=page, page_size=page_size):
            cached = await self._cache.get_merchants(page, page_size, search)
            if cached is not None:
                return cached
            rows = await self._repo.find_all(search, page, page_size)
            total = rows[0].total_count if rows else 0
            await self._cache.set_merchants(page, page_size, search, rows, total)
            return rows, total

    async def find_active(
        self, search: str, page: int, page_size: int
    ) -> tuple[list[GetMerchantsActiveRow], int]:
        with self._obs.span(
            "merchant.query.find_active", page=page, page_size=page_size
        ):
            cached = await self._cache.get_merchant_active(page, page_size, search)
            if cached is not None:
                return cached
            rows = await self._repo.find_active(search, page, page_size)
            total = rows[0].total_count if rows else 0
            await self._cache.set_merchant_active(page, page_size, search, rows, total)
            return rows, total

    async def find_trashed(
        self, search: str, page: int, page_size: int
    ) -> tuple[list[GetMerchantsTrashedRow], int]:
        with self._obs.span(
            "merchant.query.find_trashed", page=page, page_size=page_size
        ):
            cached = await self._cache.get_merchant_trashed(page, page_size, search)
            if cached is not None:
                return cached
            rows = await self._repo.find_trashed(search, page, page_size)
            total = rows[0].total_count if rows else 0
            await self._cache.set_merchant_trashed(page, page_size, search, rows, total)
            return rows, total

    async def find_by_id(self, merchant_id: int) -> GetMerchantByIDRow:
        with self._obs.span("merchant.query.find_by_id", merchant_id=merchant_id):
            cached = await self._cache.get_merchant(merchant_id)
            if cached is not None:
                return cached
            merchant = await self._repo.find_by_id(merchant_id)
            await self._cache.set_merchant(merchant)
            return merchant


__all__ = ["MerchantQueryServiceImpl"]

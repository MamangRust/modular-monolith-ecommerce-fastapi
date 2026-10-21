"""merchant_detail query service. Reads are cache-first; a miss loads from the DB and populates the cache. The `total_count` comes from the first row's window column. Unlike merchant, the merchant_detail query service does NOT forward the repository error: it passes its own sentinel to `errorhandler.HandleError`, which returns that sentinel unchanged. So a read failure is remapped — list reads to `err_find_*_merchant_details` (500) and `FindByID` to `err_merchant_detail_not_found` (404). replicates this."""

from __future__ import annotations

from pkg.database.schema.merchant_detail import (
    GetMerchantDetailRow,
    GetMerchantDetailsActiveRow,
    GetMerchantDetailsRow,
    GetMerchantDetailsTrashedRow,
)
from pkg.logger.logger import Logger
from service.merchant_detail.redis.interfaces import MerchantDetailQueryCache
from service.merchant_detail.repository.interfaces import (
    MerchantDetailQueryRepository,
)
from shared.errors import (
    err_find_active_merchant_details,
    err_find_all_merchant_details,
    err_find_trashed_merchant_details,
    err_merchant_detail_not_found,
)
from shared.observability import Observability


class MerchantDetailQueryServiceImpl:
    def __init__(
        self,
        repo: MerchantDetailQueryRepository,
        cache: MerchantDetailQueryCache,
        logger: Logger,
        obs: Observability,
    ) -> None:
        self._repo = repo
        self._cache = cache
        self._logger = logger
        self._obs = obs

    async def find_all(
        self, search: str, page: int, page_size: int
    ) -> tuple[list[GetMerchantDetailsRow], int]:
        with self._obs.span(
            "merchant_detail.query.find_all", page=page, page_size=page_size
        ):
            cached = await self._cache.get_merchant_details(page, page_size, search)
            if cached is not None:
                return cached
            try:
                rows = await self._repo.find_all(search, page, page_size)
            except Exception as exc:
                raise err_find_all_merchant_details.with_internal(exc) from exc
            total = rows[0].total_count if rows else 0
            await self._cache.set_merchant_details(
                page, page_size, search, rows, total
            )
            return rows, total

    async def find_active(
        self, search: str, page: int, page_size: int
    ) -> tuple[list[GetMerchantDetailsActiveRow], int]:
        with self._obs.span(
            "merchant_detail.query.find_active", page=page, page_size=page_size
        ):
            cached = await self._cache.get_merchant_details_active(
                page, page_size, search
            )
            if cached is not None:
                return cached
            try:
                rows = await self._repo.find_active(search, page, page_size)
            except Exception as exc:
                raise err_find_active_merchant_details.with_internal(exc) from exc
            total = rows[0].total_count if rows else 0
            await self._cache.set_merchant_details_active(
                page, page_size, search, rows, total
            )
            return rows, total

    async def find_trashed(
        self, search: str, page: int, page_size: int
    ) -> tuple[list[GetMerchantDetailsTrashedRow], int]:
        with self._obs.span(
            "merchant_detail.query.find_trashed", page=page, page_size=page_size
        ):
            cached = await self._cache.get_merchant_details_trashed(
                page, page_size, search
            )
            if cached is not None:
                return cached
            try:
                rows = await self._repo.find_trashed(search, page, page_size)
            except Exception as exc:
                raise err_find_trashed_merchant_details.with_internal(exc) from exc
            total = rows[0].total_count if rows else 0
            await self._cache.set_merchant_details_trashed(
                page, page_size, search, rows, total
            )
            return rows, total

    async def find_by_id(self, merchant_detail_id: int) -> GetMerchantDetailRow:
        with self._obs.span(
            "merchant_detail.query.find_by_id",
            merchant_detail_id=merchant_detail_id,
        ):
            cached = await self._cache.get_merchant_detail(merchant_detail_id)
            if cached is not None:
                return cached
            try:
                row = await self._repo.find_by_id(merchant_detail_id)
            except Exception as exc:
                raise err_merchant_detail_not_found.with_internal(exc) from exc
            await self._cache.set_merchant_detail(row)
            return row


__all__ = ["MerchantDetailQueryServiceImpl"]

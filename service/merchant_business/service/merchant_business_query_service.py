"""merchant_business query service.

Reads are cache-first; a miss loads from the DB and populates the cache. The
`total_count` comes from the first row's window column."""

from __future__ import annotations

from pkg.database.schema.merchant_business import (
    GetMerchantBusinessInformationRow,
    GetMerchantsBusinessInformationActiveRow,
    GetMerchantsBusinessInformationRow,
    GetMerchantsBusinessInformationTrashedRow,
)
from pkg.logger.logger import Logger
from service.merchant_business.redis.interfaces import MerchantBusinessQueryCache
from service.merchant_business.repository.interfaces import (
    MerchantBusinessQueryRepository,
)
from shared.errors import (
    AppError,
    err_failed_find_active_merchant_business,
    err_failed_find_all_merchant_business,
    err_failed_find_merchant_business_by_id,
    err_failed_find_trashed_merchant_business,
    err_merchant_business_not_found,
)
from shared.observability import Observability


class MerchantBusinessQueryServiceImpl:
    def __init__(
        self,
        repo: MerchantBusinessQueryRepository,
        cache: MerchantBusinessQueryCache,
        logger: Logger,
        obs: Observability,
    ) -> None:
        self._repo = repo
        self._cache = cache
        self._logger = logger
        self._obs = obs

    async def find_all(
        self, search: str, page: int, page_size: int
    ) -> tuple[list[GetMerchantsBusinessInformationRow], int]:
        with self._obs.span(
            "merchant_business.query.find_all", page=page, page_size=page_size
        ):
            cached = await self._cache.get_merchant_businesses(
                page, page_size, search
            )
            if cached is not None:
                return cached
            try:
                rows = await self._repo.find_all(search, page, page_size)
            except Exception as exc:
                raise err_failed_find_all_merchant_business.with_internal(
                    exc
                ) from exc
            total = rows[0].total_count if rows else 0
            await self._cache.set_merchant_businesses(
                page, page_size, search, rows, total
            )
            return rows, total

    async def find_active(
        self, search: str, page: int, page_size: int
    ) -> tuple[list[GetMerchantsBusinessInformationActiveRow], int]:
        with self._obs.span(
            "merchant_business.query.find_active", page=page, page_size=page_size
        ):
            cached = await self._cache.get_merchant_businesses_active(
                page, page_size, search
            )
            if cached is not None:
                return cached
            try:
                rows = await self._repo.find_active(search, page, page_size)
            except Exception as exc:
                raise err_failed_find_active_merchant_business.with_internal(
                    exc
                ) from exc
            total = rows[0].total_count if rows else 0
            await self._cache.set_merchant_businesses_active(
                page, page_size, search, rows, total
            )
            return rows, total

    async def find_trashed(
        self, search: str, page: int, page_size: int
    ) -> tuple[list[GetMerchantsBusinessInformationTrashedRow], int]:
        with self._obs.span(
            "merchant_business.query.find_trashed", page=page, page_size=page_size
        ):
            cached = await self._cache.get_merchant_businesses_trashed(
                page, page_size, search
            )
            if cached is not None:
                return cached
            try:
                rows = await self._repo.find_trashed(search, page, page_size)
            except Exception as exc:
                raise err_failed_find_trashed_merchant_business.with_internal(
                    exc
                ) from exc
            total = rows[0].total_count if rows else 0
            await self._cache.set_merchant_businesses_trashed(
                page, page_size, search, rows, total
            )
            return rows, total

    async def find_by_id(
        self, merchant_business_info_id: int
    ) -> GetMerchantBusinessInformationRow:
        with self._obs.span(
            "merchant_business.query.find_by_id",
            merchant_business_info_id=merchant_business_info_id,
        ):
            cached = await self._cache.get_merchant_business(
                merchant_business_info_id
            )
            if cached is not None:
                return cached
            try:
                row = await self._repo.find_by_id(merchant_business_info_id)
            except AppError as exc:
                if exc is err_merchant_business_not_found:
                    raise err_merchant_business_not_found from exc
                raise err_failed_find_merchant_business_by_id.with_internal(
                    exc
                ) from exc
            except Exception as exc:
                raise err_failed_find_merchant_business_by_id.with_internal(
                    exc
                ) from exc
            await self._cache.set_merchant_business(row)
            return row


__all__ = ["MerchantBusinessQueryServiceImpl"]

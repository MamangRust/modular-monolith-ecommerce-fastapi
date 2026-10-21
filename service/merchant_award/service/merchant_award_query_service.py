"""merchant_award query service. Reads are cache-first; a miss loads from the DB and populates the cache. The `total_count` comes from the first row's window column. Unlike merchant_detail (which remaps reads to its own sentinels), the merchant_award query service forwards the repository error unchanged through `errorhandler.HandleError` — the same behaviour as merchant. So a read failure keeps the repository's code (e.g. 404 for a missing row)."""

from __future__ import annotations

from pkg.database.schema.merchant_award import (
    GetMerchantCertificationOrAwardRow,
    GetMerchantCertificationsAndAwardsActiveRow,
    GetMerchantCertificationsAndAwardsRow,
    GetMerchantCertificationsAndAwardsTrashedRow,
)
from pkg.logger.logger import Logger
from service.merchant_award.redis.interfaces import MerchantAwardQueryCache
from service.merchant_award.repository.interfaces import (
    MerchantAwardQueryRepository,
)
from shared.observability import Observability


class MerchantAwardQueryServiceImpl:
    def __init__(
        self,
        repo: MerchantAwardQueryRepository,
        cache: MerchantAwardQueryCache,
        logger: Logger,
        obs: Observability,
    ) -> None:
        self._repo = repo
        self._cache = cache
        self._logger = logger
        self._obs = obs

    async def find_all(
        self, search: str, page: int, page_size: int
    ) -> tuple[list[GetMerchantCertificationsAndAwardsRow], int]:
        with self._obs.span(
            "merchant_award.query.find_all", page=page, page_size=page_size
        ):
            cached = await self._cache.get_merchant_awards(page, page_size, search)
            if cached is not None:
                return cached
            rows = await self._repo.find_all(search, page, page_size)
            total = rows[0].total_count if rows else 0
            await self._cache.set_merchant_awards(page, page_size, search, rows, total)
            return rows, total

    async def find_active(
        self, search: str, page: int, page_size: int
    ) -> tuple[list[GetMerchantCertificationsAndAwardsActiveRow], int]:
        with self._obs.span(
            "merchant_award.query.find_active", page=page, page_size=page_size
        ):
            cached = await self._cache.get_merchant_awards_active(
                page, page_size, search
            )
            if cached is not None:
                return cached
            rows = await self._repo.find_active(search, page, page_size)
            total = rows[0].total_count if rows else 0
            await self._cache.set_merchant_awards_active(
                page, page_size, search, rows, total
            )
            return rows, total

    async def find_trashed(
        self, search: str, page: int, page_size: int
    ) -> tuple[list[GetMerchantCertificationsAndAwardsTrashedRow], int]:
        with self._obs.span(
            "merchant_award.query.find_trashed", page=page, page_size=page_size
        ):
            cached = await self._cache.get_merchant_awards_trashed(
                page, page_size, search
            )
            if cached is not None:
                return cached
            rows = await self._repo.find_trashed(search, page, page_size)
            total = rows[0].total_count if rows else 0
            await self._cache.set_merchant_awards_trashed(
                page, page_size, search, rows, total
            )
            return rows, total

    async def find_by_id(
        self, merchant_certification_id: int
    ) -> GetMerchantCertificationOrAwardRow:
        with self._obs.span(
            "merchant_award.query.find_by_id",
            merchant_certification_id=merchant_certification_id,
        ):
            cached = await self._cache.get_merchant_award(merchant_certification_id)
            if cached is not None:
                return cached
            row = await self._repo.find_by_id(merchant_certification_id)
            await self._cache.set_merchant_award(row)
            return row


__all__ = ["MerchantAwardQueryServiceImpl"]

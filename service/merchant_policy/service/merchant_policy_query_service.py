"""merchant_policy query service. Reads are cache-first; a miss loads from the DB and populates the cache. Like merchant_business (and unlike merchant_award), the merchant_policy query service remaps reads to its own sentinels: list failures become `err_failed_find_*_merchant_policies` (500), and `FindByID` maps the repository not-found to `err_merchant_policy_not_found` (404) and every other failure to `err_failed_find_merchant_policy_by_id` (500). NORMALISATION: sets `totalRecords:= len(page)` for every list and leaves the window `COUNT(*)` unused. follows the rest of the codebase and uses the window count from the first row, so `total_records` is the full result size rather than the page length."""

from __future__ import annotations

from pkg.database.schema.merchant_policy import (
    GetMerchantPoliciesActiveRow,
    GetMerchantPoliciesRow,
    GetMerchantPoliciesTrashedRow,
    GetMerchantPolicyRow,
)
from pkg.logger.logger import Logger
from service.merchant_policy.redis.interfaces import MerchantPolicyQueryCache
from service.merchant_policy.repository.interfaces import (
    MerchantPolicyQueryRepository,
)
from shared.errors import (
    AppError,
    err_failed_find_active_merchant_policies,
    err_failed_find_all_merchant_policies,
    err_failed_find_merchant_policy_by_id,
    err_failed_find_trashed_merchant_policies,
    err_merchant_policy_not_found,
)
from shared.observability import Observability


class MerchantPolicyQueryServiceImpl:
    def __init__(
        self,
        repo: MerchantPolicyQueryRepository,
        cache: MerchantPolicyQueryCache,
        logger: Logger,
        obs: Observability,
    ) -> None:
        self._repo = repo
        self._cache = cache
        self._logger = logger
        self._obs = obs

    async def find_all(
        self, search: str, page: int, page_size: int
    ) -> tuple[list[GetMerchantPoliciesRow], int]:
        with self._obs.span(
            "merchant_policy.query.find_all", page=page, page_size=page_size
        ):
            cached = await self._cache.get_merchant_policies(
                page, page_size, search
            )
            if cached is not None:
                return cached
            try:
                rows = await self._repo.find_all(search, page, page_size)
            except Exception as exc:
                raise err_failed_find_all_merchant_policies.with_internal(
                    exc
                ) from exc
            total = rows[0].total_count if rows else 0
            await self._cache.set_merchant_policies(
                page, page_size, search, rows, total
            )
            return rows, total

    async def find_active(
        self, search: str, page: int, page_size: int
    ) -> tuple[list[GetMerchantPoliciesActiveRow], int]:
        with self._obs.span(
            "merchant_policy.query.find_active", page=page, page_size=page_size
        ):
            cached = await self._cache.get_merchant_policies_active(
                page, page_size, search
            )
            if cached is not None:
                return cached
            try:
                rows = await self._repo.find_active(search, page, page_size)
            except Exception as exc:
                raise err_failed_find_active_merchant_policies.with_internal(
                    exc
                ) from exc
            total = rows[0].total_count if rows else 0
            await self._cache.set_merchant_policies_active(
                page, page_size, search, rows, total
            )
            return rows, total

    async def find_trashed(
        self, search: str, page: int, page_size: int
    ) -> tuple[list[GetMerchantPoliciesTrashedRow], int]:
        with self._obs.span(
            "merchant_policy.query.find_trashed", page=page, page_size=page_size
        ):
            cached = await self._cache.get_merchant_policies_trashed(
                page, page_size, search
            )
            if cached is not None:
                return cached
            try:
                rows = await self._repo.find_trashed(search, page, page_size)
            except Exception as exc:
                raise err_failed_find_trashed_merchant_policies.with_internal(
                    exc
                ) from exc
            total = rows[0].total_count if rows else 0
            await self._cache.set_merchant_policies_trashed(
                page, page_size, search, rows, total
            )
            return rows, total

    async def find_by_id(self, merchant_policy_id: int) -> GetMerchantPolicyRow:
        with self._obs.span(
            "merchant_policy.query.find_by_id",
            merchant_policy_id=merchant_policy_id,
        ):
            cached = await self._cache.get_merchant_policy(merchant_policy_id)
            if cached is not None:
                return cached
            try:
                row = await self._repo.find_by_id(merchant_policy_id)
            except AppError as exc:
                if exc is err_merchant_policy_not_found:
                    raise err_merchant_policy_not_found from exc
                raise err_failed_find_merchant_policy_by_id.with_internal(
                    exc
                ) from exc
            except Exception as exc:
                raise err_failed_find_merchant_policy_by_id.with_internal(
                    exc
                ) from exc
            await self._cache.set_merchant_policy(row)
            return row


__all__ = ["MerchantPolicyQueryServiceImpl"]

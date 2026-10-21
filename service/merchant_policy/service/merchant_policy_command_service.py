"""merchant_policy command service. `Trash`, `Restore`, `DeletePermanent` and `DeleteAll` propagate the repository error unchanged (so a missing row stays 404). (Note this differs from merchant_business, whose `Create` also evicts the new row's key — a harmless absent here.)"""

from __future__ import annotations

from pkg.database.schema.merchant_policy import (
    CreateMerchantPolicyRow,
    MerchantPolicy,
    UpdateMerchantPolicyRow,
)
from pkg.logger.logger import Logger
from service.merchant_policy.redis.interfaces import MerchantPolicyCommandCache
from service.merchant_policy.repository.interfaces import (
    MerchantPolicyCommandRepository,
)
from shared.domain.requests.merchant_policy import (
    CreateMerchantPolicyRequest,
    UpdateMerchantPolicyRequest,
)
from shared.errors import (
    err_failed_create_merchant_policy,
    err_failed_restore_all_merchant_policies,
    err_failed_update_merchant_policy,
)
from shared.observability import Observability


class MerchantPolicyCommandServiceImpl:
    def __init__(
        self,
        repo: MerchantPolicyCommandRepository,
        cache: MerchantPolicyCommandCache,
        logger: Logger,
        obs: Observability,
    ) -> None:
        self._repo = repo
        self._cache = cache
        self._logger = logger
        self._obs = obs

    async def create(
        self, request: CreateMerchantPolicyRequest
    ) -> CreateMerchantPolicyRow:
        with self._obs.span(
            "merchant_policy.command.create", merchant_id=request.merchant_id
        ):
            try:
                return await self._repo.create(request)
            except Exception as exc:
                raise err_failed_create_merchant_policy.with_internal(exc) from exc

    async def update(
        self, request: UpdateMerchantPolicyRequest
    ) -> UpdateMerchantPolicyRow:
        with self._obs.span(
            "merchant_policy.command.update",
            merchant_policy_id=request.merchant_policy_id,
        ):
            try:
                row = await self._repo.update(request)
            except Exception as exc:
                raise err_failed_update_merchant_policy.with_internal(exc) from exc
            await self._cache.delete_cached_merchant_policy(row.merchant_policy_id)
            return row

    async def trash(self, merchant_policy_id: int) -> MerchantPolicy:
        with self._obs.span(
            "merchant_policy.command.trash", merchant_policy_id=merchant_policy_id
        ):
            row = await self._repo.trash(merchant_policy_id)
            await self._cache.delete_cached_merchant_policy(merchant_policy_id)
            return row

    async def restore(self, merchant_policy_id: int) -> MerchantPolicy:
        with self._obs.span(
            "merchant_policy.command.restore",
            merchant_policy_id=merchant_policy_id,
        ):
            row = await self._repo.restore(merchant_policy_id)
            await self._cache.delete_cached_merchant_policy(merchant_policy_id)
            return row

    async def delete_permanent(self, merchant_policy_id: int) -> bool:
        with self._obs.span(
            "merchant_policy.command.delete_permanent",
            merchant_policy_id=merchant_policy_id,
        ):
            success = await self._repo.delete_permanent(merchant_policy_id)
            await self._cache.delete_cached_merchant_policy(merchant_policy_id)
            return success

    async def restore_all(self) -> bool:
        with self._obs.span("merchant_policy.command.restore_all"):
            try:
                return await self._repo.restore_all()
            except Exception as exc:
                raise err_failed_restore_all_merchant_policies.with_internal(
                    exc
                ) from exc

    async def delete_all(self) -> bool:
        with self._obs.span("merchant_policy.command.delete_all"):
            return await self._repo.delete_all()


__all__ = ["MerchantPolicyCommandServiceImpl"]

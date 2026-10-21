"""merchant_business command service. `Trash`, `Restore`, `DeletePermanent` and `DeleteAll` propagate the repository error unchanged (so a missing row stays 404)."""

from __future__ import annotations

from pkg.database.schema.merchant_business import (
    CreateMerchantBusinessInformationRow,
    MerchantBusinessInformation,
    UpdateMerchantBusinessInformationRow,
)
from pkg.logger.logger import Logger
from service.merchant_business.redis.interfaces import (
    MerchantBusinessCommandCache,
)
from service.merchant_business.repository.interfaces import (
    MerchantBusinessCommandRepository,
)
from shared.domain.requests.merchant_business import (
    CreateMerchantBusinessInformationRequest,
    UpdateMerchantBusinessInformationRequest,
)
from shared.errors import (
    err_failed_create_merchant_business,
    err_failed_restore_all_merchant_business,
    err_failed_update_merchant_business,
)
from shared.observability import Observability


class MerchantBusinessCommandServiceImpl:
    def __init__(
        self,
        repo: MerchantBusinessCommandRepository,
        cache: MerchantBusinessCommandCache,
        logger: Logger,
        obs: Observability,
    ) -> None:
        self._repo = repo
        self._cache = cache
        self._logger = logger
        self._obs = obs

    async def create(
        self, request: CreateMerchantBusinessInformationRequest
    ) -> CreateMerchantBusinessInformationRow:
        with self._obs.span(
            "merchant_business.command.create", merchant_id=request.merchant_id
        ):
            try:
                row = await self._repo.create(request)
            except Exception as exc:
                raise err_failed_create_merchant_business.with_internal(exc) from exc
            await self._cache.delete_cached_merchant_business(
                row.merchant_business_info_id
            )
            return row

    async def update(
        self, request: UpdateMerchantBusinessInformationRequest
    ) -> UpdateMerchantBusinessInformationRow:
        with self._obs.span(
            "merchant_business.command.update",
            merchant_business_info_id=request.merchant_business_info_id,
        ):
            try:
                row = await self._repo.update(request)
            except Exception as exc:
                raise err_failed_update_merchant_business.with_internal(exc) from exc
            await self._cache.delete_cached_merchant_business(
                row.merchant_business_info_id
            )
            return row

    async def trash(
        self, merchant_business_info_id: int
    ) -> MerchantBusinessInformation:
        with self._obs.span(
            "merchant_business.command.trash",
            merchant_business_info_id=merchant_business_info_id,
        ):
            row = await self._repo.trash(merchant_business_info_id)
            await self._cache.delete_cached_merchant_business(
                merchant_business_info_id
            )
            return row

    async def restore(
        self, merchant_business_info_id: int
    ) -> MerchantBusinessInformation:
        with self._obs.span(
            "merchant_business.command.restore",
            merchant_business_info_id=merchant_business_info_id,
        ):
            row = await self._repo.restore(merchant_business_info_id)
            await self._cache.delete_cached_merchant_business(
                merchant_business_info_id
            )
            return row

    async def delete_permanent(self, merchant_business_info_id: int) -> bool:
        with self._obs.span(
            "merchant_business.command.delete_permanent",
            merchant_business_info_id=merchant_business_info_id,
        ):
            success = await self._repo.delete_permanent(merchant_business_info_id)
            await self._cache.delete_cached_merchant_business(
                merchant_business_info_id
            )
            return success

    async def restore_all(self) -> bool:
        with self._obs.span("merchant_business.command.restore_all"):
            try:
                return await self._repo.restore_all()
            except Exception as exc:
                raise err_failed_restore_all_merchant_business.with_internal(
                    exc
                ) from exc

    async def delete_all(self) -> bool:
        with self._obs.span("merchant_business.command.delete_all"):
            return await self._repo.delete_all()


__all__ = ["MerchantBusinessCommandServiceImpl"]

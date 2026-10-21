"""merchant_award command service. `Trash`, `Restore`, `DeletePermanent` and `DeleteAll` propagate the repository error unchanged (so a missing row stays 404)."""

from __future__ import annotations

from pkg.database.schema.merchant_award import (
    CreateMerchantCertificationOrAwardRow,
    MerchantCertificationsAndAward,
    UpdateMerchantCertificationOrAwardRow,
)
from pkg.logger.logger import Logger
from service.merchant_award.redis.interfaces import MerchantAwardCommandCache
from service.merchant_award.repository.interfaces import (
    MerchantAwardCommandRepository,
)
from shared.domain.requests.merchant_award import (
    CreateMerchantCertificationOrAwardRequest,
    UpdateMerchantCertificationOrAwardRequest,
)
from shared.errors import (
    err_failed_create_merchant_award,
    err_failed_restore_all_merchant_awards,
    err_failed_update_merchant_award,
)
from shared.observability import Observability


class MerchantAwardCommandServiceImpl:
    def __init__(
        self,
        repo: MerchantAwardCommandRepository,
        cache: MerchantAwardCommandCache,
        logger: Logger,
        obs: Observability,
    ) -> None:
        self._repo = repo
        self._cache = cache
        self._logger = logger
        self._obs = obs

    async def create(
        self, request: CreateMerchantCertificationOrAwardRequest
    ) -> CreateMerchantCertificationOrAwardRow:
        with self._obs.span(
            "merchant_award.command.create", merchant_id=request.merchant_id
        ):
            try:
                return await self._repo.create(request)
            except Exception as exc:
                raise err_failed_create_merchant_award.with_internal(exc) from exc

    async def update(
        self, request: UpdateMerchantCertificationOrAwardRequest
    ) -> UpdateMerchantCertificationOrAwardRow:
        with self._obs.span(
            "merchant_award.command.update",
            merchant_certification_id=request.merchant_certification_id,
        ):
            try:
                row = await self._repo.update(request)
            except Exception as exc:
                raise err_failed_update_merchant_award.with_internal(exc) from exc
            if request.merchant_certification_id is not None:
                await self._cache.delete_cached_merchant_award(
                    request.merchant_certification_id
                )
            return row

    async def trash(
        self, merchant_certification_id: int
    ) -> MerchantCertificationsAndAward:
        with self._obs.span(
            "merchant_award.command.trash",
            merchant_certification_id=merchant_certification_id,
        ):
            row = await self._repo.trash(merchant_certification_id)
            await self._cache.delete_cached_merchant_award(
                merchant_certification_id
            )
            return row

    async def restore(
        self, merchant_certification_id: int
    ) -> MerchantCertificationsAndAward:
        with self._obs.span(
            "merchant_award.command.restore",
            merchant_certification_id=merchant_certification_id,
        ):
            # does not evict the cache on restore.
            return await self._repo.restore(merchant_certification_id)

    async def delete_permanent(self, merchant_certification_id: int) -> bool:
        with self._obs.span(
            "merchant_award.command.delete_permanent",
            merchant_certification_id=merchant_certification_id,
        ):
            success = await self._repo.delete_permanent(merchant_certification_id)
            await self._cache.delete_cached_merchant_award(
                merchant_certification_id
            )
            return success

    async def restore_all(self) -> bool:
        with self._obs.span("merchant_award.command.restore_all"):
            try:
                return await self._repo.restore_all()
            except Exception as exc:
                raise err_failed_restore_all_merchant_awards.with_internal(
                    exc
                ) from exc

    async def delete_all(self) -> bool:
        with self._obs.span("merchant_award.command.delete_all"):
            return await self._repo.delete_all()


__all__ = ["MerchantAwardCommandServiceImpl"]

"""merchant_social_link command service. Every method passes its own sentinel to `errorhandler.HandleError`, which returns that sentinel — so a failure surfaces as the 500 sentinel regardless of the underlying repository error (unlike merchant, which forwards it). No cache is involved."""

from __future__ import annotations

from pkg.database.schema.merchant_detail import (
    CreateMerchantSocialMediaLinkRow,
    UpdateMerchantSocialMediaLinkRow,
)
from pkg.logger.logger import Logger
from service.merchant_detail.repository.interfaces import (
    MerchantSocialLinkCommandRepository,
)
from shared.domain.requests.merchant_detail import (
    CreateMerchantSocialRequest,
    UpdateMerchantSocialRequest,
)
from shared.errors import (
    err_create_merchant_social_link,
    err_delete_all_permanent_merchant_social_links,
    err_delete_permanent_merchant_social_link,
    err_restore_all_merchant_social_links,
    err_restore_merchant_social_link,
    err_trash_merchant_social_link,
    err_update_merchant_social_link,
)
from shared.observability import Observability


class MerchantSocialLinkCommandServiceImpl:
    def __init__(
        self,
        repo: MerchantSocialLinkCommandRepository,
        logger: Logger,
        obs: Observability,
    ) -> None:
        self._repo = repo
        self._logger = logger
        self._obs = obs

    async def create(
        self, request: CreateMerchantSocialRequest
    ) -> CreateMerchantSocialMediaLinkRow:
        with self._obs.span(
            "merchant_social_link.command.create",
            merchant_detail_id=request.merchant_detail_id,
        ):
            try:
                return await self._repo.create(request)
            except Exception as exc:
                raise err_create_merchant_social_link.with_internal(exc) from exc

    async def update(
        self, request: UpdateMerchantSocialRequest
    ) -> UpdateMerchantSocialMediaLinkRow:
        with self._obs.span(
            "merchant_social_link.command.update", social_link_id=request.id
        ):
            try:
                return await self._repo.update(request)
            except Exception as exc:
                raise err_update_merchant_social_link.with_internal(exc) from exc

    async def trash(self, social_id: int) -> bool:
        with self._obs.span(
            "merchant_social_link.command.trash", social_link_id=social_id
        ):
            try:
                return await self._repo.trash(social_id)
            except Exception as exc:
                raise err_trash_merchant_social_link.with_internal(exc) from exc

    async def restore(self, social_id: int) -> bool:
        with self._obs.span(
            "merchant_social_link.command.restore", social_link_id=social_id
        ):
            try:
                return await self._repo.restore(social_id)
            except Exception as exc:
                raise err_restore_merchant_social_link.with_internal(exc) from exc

    async def delete_permanent(self, social_id: int) -> bool:
        with self._obs.span(
            "merchant_social_link.command.delete_permanent",
            social_link_id=social_id,
        ):
            try:
                return await self._repo.delete_permanent(social_id)
            except Exception as exc:
                raise err_delete_permanent_merchant_social_link.with_internal(
                    exc
                ) from exc

    async def restore_all(self) -> bool:
        with self._obs.span("merchant_social_link.command.restore_all"):
            try:
                return await self._repo.restore_all()
            except Exception as exc:
                raise err_restore_all_merchant_social_links.with_internal(
                    exc
                ) from exc

    async def delete_all(self) -> bool:
        with self._obs.span("merchant_social_link.command.delete_all"):
            try:
                return await self._repo.delete_all()
            except Exception as exc:
                raise err_delete_all_permanent_merchant_social_links.with_internal(
                    exc
                ) from exc


__all__ = ["MerchantSocialLinkCommandServiceImpl"]

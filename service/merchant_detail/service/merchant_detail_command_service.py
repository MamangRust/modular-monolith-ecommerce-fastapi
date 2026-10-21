"""merchant_detail command service. `DeletePermanent` reproduces the source verbatim: it first calls `Trash` (to obtain the row whose cover/logo files are removed) — ignoring any error from that call — then calls `DeletePermanent`, then best-effort removes the files (`os.Remove` errors are ignored,). The side effect is that deleting an *active* detail works (it is trashed first) and deleting a missing detail reports success."""

from __future__ import annotations

import os

from pkg.database.schema.merchant_detail import (
    CreateMerchantDetailRow,
    MerchantDetail,
    UpdateMerchantDetailRow,
)
from pkg.logger.logger import Logger
from service.merchant_detail.redis.interfaces import MerchantDetailCommandCache
from service.merchant_detail.repository.interfaces import (
    MerchantDetailCommandRepository,
    MerchantQueryRepository,
)
from shared.domain.requests.merchant_detail import (
    CreateMerchantDetailRequest,
    UpdateMerchantDetailRequest,
)
from shared.errors import (
    err_create_merchant_detail,
    err_restore_all_merchant_details,
    err_update_merchant_detail,
)
from shared.observability import Observability


def _remove_file(path: str | None) -> None:
    """Best-effort file removal (`os.Remove` ignores its error)."""
    if not path:
        return
    try:
        os.remove(path)
    except OSError:
        pass


class MerchantDetailCommandServiceImpl:
    def __init__(
        self,
        repo: MerchantDetailCommandRepository,
        merchant_query: MerchantQueryRepository,
        cache: MerchantDetailCommandCache,
        logger: Logger,
        obs: Observability,
    ) -> None:
        self._repo = repo
        self._merchant_query = merchant_query
        self._cache = cache
        self._logger = logger
        self._obs = obs

    async def create(
        self, request: CreateMerchantDetailRequest
    ) -> CreateMerchantDetailRow:
        with self._obs.span(
            "merchant_detail.command.create", merchant_id=request.merchant_id
        ):
            # Validate merchant existence; the adapter error propagates unchanged.
            await self._merchant_query.find_by_id(request.merchant_id)
            try:
                return await self._repo.create(request)
            except Exception as exc:
                raise err_create_merchant_detail.with_internal(exc) from exc

    async def update(
        self, request: UpdateMerchantDetailRequest
    ) -> UpdateMerchantDetailRow:
        with self._obs.span(
            "merchant_detail.command.update",
            merchant_detail_id=request.merchant_detail_id,
        ):
            try:
                row = await self._repo.update(request)
            except Exception as exc:
                raise err_update_merchant_detail.with_internal(exc) from exc
            if request.merchant_detail_id is not None:
                await self._cache.delete_cached_merchant_detail(
                    request.merchant_detail_id
                )
            return row

    async def trash(self, merchant_detail_id: int) -> MerchantDetail:
        with self._obs.span(
            "merchant_detail.command.trash", merchant_detail_id=merchant_detail_id
        ):
            row = await self._repo.trash(merchant_detail_id)
            await self._cache.delete_cached_merchant_detail(merchant_detail_id)
            return row

    async def restore(self, merchant_detail_id: int) -> MerchantDetail:
        with self._obs.span(
            "merchant_detail.command.restore",
            merchant_detail_id=merchant_detail_id,
        ):
            row = await self._repo.restore(merchant_detail_id)
            await self._cache.delete_cached_merchant_detail(merchant_detail_id)
            return row

    async def delete_permanent(self, merchant_detail_id: int) -> bool:
        with self._obs.span(
            "merchant_detail.command.delete_permanent",
            merchant_detail_id=merchant_detail_id,
        ):
            # calls Trash first (and ignores its error) to obtain the row for
            # file removal; the is reproduced verbatim (see module docstring).
            detail: MerchantDetail | None
            try:
                detail = await self._repo.trash(merchant_detail_id)
            except Exception:
                detail = None

            success = await self._repo.delete_permanent(merchant_detail_id)

            if detail is not None:
                _remove_file(detail.cover_image_url)
                _remove_file(detail.logo_url)

            await self._cache.delete_cached_merchant_detail(merchant_detail_id)
            return success

    async def restore_all(self) -> bool:
        with self._obs.span("merchant_detail.command.restore_all"):
            try:
                return await self._repo.restore_all()
            except Exception as exc:
                raise err_restore_all_merchant_details.with_internal(exc) from exc

    async def delete_all(self) -> bool:
        with self._obs.span("merchant_detail.command.delete_all"):
            return await self._repo.delete_all()


__all__ = ["MerchantDetailCommandServiceImpl"]

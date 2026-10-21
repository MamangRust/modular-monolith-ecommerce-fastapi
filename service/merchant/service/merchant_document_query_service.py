"""Merchant document query service. injects a `MerchantDocumentQueryCache` into this service but never reads from it — every method hits the repository directly. keeps the cache dependency (unused) for wiring."""

from __future__ import annotations

from pkg.database.schema.merchant_document import (
    GetActiveMerchantDocumentsRow,
    GetMerchantDocumentRow,
    GetMerchantDocumentsRow,
    GetTrashedMerchantDocumentsRow,
)
from pkg.logger.logger import Logger
from service.merchant.redis.interfaces import MerchantDocumentQueryCache
from service.merchant.repository.interfaces import MerchantDocumentQueryRepository
from shared.observability import Observability


class MerchantDocumentQueryServiceImpl:
    def __init__(
        self,
        repo: MerchantDocumentQueryRepository,
        cache: MerchantDocumentQueryCache,
        logger: Logger,
        obs: Observability,
    ) -> None:
        self._repo = repo
        self._cache = cache
        self._logger = logger
        self._obs = obs

    async def find_all(
        self, search: str, page: int, page_size: int
    ) -> tuple[list[GetMerchantDocumentsRow], int]:
        with self._obs.span(
            "merchant_document.query.find_all", page=page, page_size=page_size
        ):
            return await self._repo.find_all(search, page, page_size)

    async def find_by_id(self, document_id: int) -> GetMerchantDocumentRow:
        with self._obs.span(
            "merchant_document.query.find_by_id", document_id=document_id
        ):
            return await self._repo.find_by_id(document_id)

    async def find_active(
        self, search: str, page: int, page_size: int
    ) -> tuple[list[GetActiveMerchantDocumentsRow], int]:
        with self._obs.span(
            "merchant_document.query.find_active", page=page, page_size=page_size
        ):
            return await self._repo.find_active(search, page, page_size)

    async def find_trashed(
        self, search: str, page: int, page_size: int
    ) -> tuple[list[GetTrashedMerchantDocumentsRow], int]:
        with self._obs.span(
            "merchant_document.query.find_trashed", page=page, page_size=page_size
        ):
            return await self._repo.find_trashed(search, page, page_size)


__all__ = ["MerchantDocumentQueryServiceImpl"]

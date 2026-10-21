"""Merchant document query cache. Kept faithful rather than dropped."""

from __future__ import annotations

from pkg.database.schema.merchant_document import (
    GetActiveMerchantDocumentsRow,
    GetMerchantDocumentRow,
    GetMerchantDocumentsRow,
)
from pkg.logger.logger import Logger
from service.merchant.redis.cache import (
    decode_page,
    document_active_row_from_dict,
    document_active_row_to_dict,
    document_by_id_from_dict,
    document_by_id_to_dict,
    document_row_from_dict,
    document_row_to_dict,
    encode_page,
)
from service.merchant.redis.common import (
    TTL_DEFAULT,
    merchant_document_active_key,
    merchant_document_all_key,
    merchant_document_by_id_key,
    merchant_document_trashed_key,
)
from shared.cache import CacheStore


class MerchantDocumentQueryCacheImpl:
    def __init__(self, store: CacheStore, logger: Logger) -> None:
        self._store = store
        self._logger = logger

    async def get_merchant_documents(
        self, page: int, page_size: int, search: str
    ) -> tuple[list[GetMerchantDocumentsRow], int] | None:
        payload = await self._store.get_json(
            merchant_document_all_key(page, page_size, search)
        )
        return decode_page(payload, document_row_from_dict)

    async def set_merchant_documents(
        self,
        page: int,
        page_size: int,
        search: str,
        rows: list[GetMerchantDocumentsRow],
        total: int,
    ) -> None:
        await self._store.set_json(
            merchant_document_all_key(page, page_size, search),
            encode_page(rows, total, document_row_to_dict),
            TTL_DEFAULT,
        )

    async def get_merchant_documents_active(
        self, page: int, page_size: int, search: str
    ) -> tuple[list[GetActiveMerchantDocumentsRow], int] | None:
        payload = await self._store.get_json(
            merchant_document_active_key(page, page_size, search)
        )
        return decode_page(payload, document_active_row_from_dict)

    async def set_merchant_documents_active(
        self,
        page: int,
        page_size: int,
        search: str,
        rows: list[GetActiveMerchantDocumentsRow],
        total: int,
    ) -> None:
        await self._store.set_json(
            merchant_document_active_key(page, page_size, search),
            encode_page(rows, total, document_active_row_to_dict),
            TTL_DEFAULT,
        )

    async def get_merchant_documents_trashed(
        self, page: int, page_size: int, search: str
    ) -> tuple[list[GetActiveMerchantDocumentsRow], int] | None:
        payload = await self._store.get_json(
            merchant_document_trashed_key(page, page_size, search)
        )
        return decode_page(payload, document_active_row_from_dict)

    async def set_merchant_documents_trashed(
        self,
        page: int,
        page_size: int,
        search: str,
        rows: list[GetActiveMerchantDocumentsRow],
        total: int,
    ) -> None:
        await self._store.set_json(
            merchant_document_trashed_key(page, page_size, search),
            encode_page(rows, total, document_active_row_to_dict),
            TTL_DEFAULT,
        )

    async def get_merchant_document(
        self, document_id: int
    ) -> GetMerchantDocumentRow | None:
        payload = await self._store.get_json(
            merchant_document_by_id_key(document_id)
        )
        if not isinstance(payload, dict):
            return None
        return document_by_id_from_dict(payload)

    async def set_merchant_document(self, row: GetMerchantDocumentRow) -> None:
        await self._store.set_json(
            merchant_document_by_id_key(row.document_id),
            document_by_id_to_dict(row),
            TTL_DEFAULT,
        )


__all__ = ["MerchantDocumentQueryCacheImpl"]

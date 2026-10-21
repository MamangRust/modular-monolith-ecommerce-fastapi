"""Merchant cache"""

from __future__ import annotations

from typing import Protocol

from pkg.database.schema.merchant import (
    GetMerchantByIDRow,
    GetMerchantsActiveRow,
    GetMerchantsRow,
    GetMerchantsTrashedRow,
)
from pkg.database.schema.merchant_document import (
    GetActiveMerchantDocumentsRow,
    GetMerchantDocumentRow,
    GetMerchantDocumentsRow,
    GetTrashedMerchantDocumentsRow,
)


class MerchantQueryCache(Protocol):
    async def get_merchants(
        self, page: int, page_size: int, search: str
    ) -> tuple[list[GetMerchantsRow], int] | None: ...

    async def set_merchants(
        self,
        page: int,
        page_size: int,
        search: str,
        rows: list[GetMerchantsRow],
        total: int,
    ) -> None: ...

    async def get_merchant_active(
        self, page: int, page_size: int, search: str
    ) -> tuple[list[GetMerchantsActiveRow], int] | None: ...

    async def set_merchant_active(
        self,
        page: int,
        page_size: int,
        search: str,
        rows: list[GetMerchantsActiveRow],
        total: int,
    ) -> None: ...

    async def get_merchant_trashed(
        self, page: int, page_size: int, search: str
    ) -> tuple[list[GetMerchantsTrashedRow], int] | None: ...

    async def set_merchant_trashed(
        self,
        page: int,
        page_size: int,
        search: str,
        rows: list[GetMerchantsTrashedRow],
        total: int,
    ) -> None: ...

    async def get_merchant(self, merchant_id: int) -> GetMerchantByIDRow | None: ...

    async def set_merchant(self, row: GetMerchantByIDRow) -> None: ...


class MerchantCommandCache(Protocol):
    async def delete_cached_merchant(self, merchant_id: int) -> int: ...

    async def invalidate_merchant_cache(self) -> int: ...


class MerchantDocumentQueryCache(Protocol):
    async def get_merchant_documents(
        self, page: int, page_size: int, search: str
    ) -> tuple[list[GetMerchantDocumentsRow], int] | None: ...

    async def set_merchant_documents(
        self,
        page: int,
        page_size: int,
        search: str,
        rows: list[GetMerchantDocumentsRow],
        total: int,
    ) -> None: ...

    async def get_merchant_documents_active(
        self, page: int, page_size: int, search: str
    ) -> tuple[list[GetActiveMerchantDocumentsRow], int] | None: ...

    async def set_merchant_documents_active(
        self,
        page: int,
        page_size: int,
        search: str,
        rows: list[GetActiveMerchantDocumentsRow],
        total: int,
    ) -> None: ...

    async def get_merchant_documents_trashed(
        self, page: int, page_size: int, search: str
    ) -> tuple[list[GetTrashedMerchantDocumentsRow], int] | None: ...

    async def set_merchant_documents_trashed(
        self,
        page: int,
        page_size: int,
        search: str,
        rows: list[GetTrashedMerchantDocumentsRow],
        total: int,
    ) -> None: ...

    async def get_merchant_document(
        self, document_id: int
    ) -> GetMerchantDocumentRow | None: ...

    async def set_merchant_document(self, row: GetMerchantDocumentRow) -> None: ...


class MerchantDocumentCommandCache(Protocol):
    async def delete_cached_merchant_documents(self, document_id: int) -> int: ...


__all__ = [
    "MerchantCommandCache",
    "MerchantDocumentCommandCache",
    "MerchantDocumentQueryCache",
    "MerchantQueryCache",
]

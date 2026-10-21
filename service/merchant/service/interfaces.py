"""Merchant service"""

from __future__ import annotations

from typing import Protocol

from pkg.database.schema.merchant import (
    CreateMerchantRow,
    GetMerchantByIDRow,
    GetMerchantsActiveRow,
    GetMerchantsRow,
    GetMerchantsTrashedRow,
    Merchant,
    UpdateMerchantRow,
    UpdateMerchantStatusRow,
)
from pkg.database.schema.merchant_document import (
    CreateMerchantDocumentRow,
    GetActiveMerchantDocumentsRow,
    GetMerchantDocumentRow,
    GetMerchantDocumentsRow,
    GetTrashedMerchantDocumentsRow,
    MerchantDocument,
    UpdateMerchantDocumentRow,
    UpdateMerchantDocumentStatusRow,
)
from shared.domain.requests.merchant import (
    CreateMerchantDocumentRequest,
    CreateMerchantRequest,
    UpdateMerchantDocumentRequest,
    UpdateMerchantDocumentStatusRequest,
    UpdateMerchantRequest,
    UpdateMerchantStatusRequest,
)


class MerchantQueryService(Protocol):
    async def find_all(
        self, search: str, page: int, page_size: int
    ) -> tuple[list[GetMerchantsRow], int]: ...

    async def find_active(
        self, search: str, page: int, page_size: int
    ) -> tuple[list[GetMerchantsActiveRow], int]: ...

    async def find_trashed(
        self, search: str, page: int, page_size: int
    ) -> tuple[list[GetMerchantsTrashedRow], int]: ...

    async def find_by_id(self, merchant_id: int) -> GetMerchantByIDRow: ...


class MerchantCommandService(Protocol):
    async def create(self, request: CreateMerchantRequest) -> CreateMerchantRow: ...

    async def update(self, request: UpdateMerchantRequest) -> UpdateMerchantRow: ...

    async def update_status(
        self, request: UpdateMerchantStatusRequest
    ) -> UpdateMerchantStatusRow: ...

    async def trash(self, merchant_id: int) -> Merchant: ...

    async def restore(self, merchant_id: int) -> Merchant: ...

    async def delete_permanent(self, merchant_id: int) -> bool: ...

    async def restore_all(self) -> bool: ...

    async def delete_all(self) -> bool: ...


class MerchantDocumentQueryService(Protocol):
    async def find_all(
        self, search: str, page: int, page_size: int
    ) -> tuple[list[GetMerchantDocumentsRow], int]: ...

    async def find_by_id(self, document_id: int) -> GetMerchantDocumentRow: ...

    async def find_active(
        self, search: str, page: int, page_size: int
    ) -> tuple[list[GetActiveMerchantDocumentsRow], int]: ...

    async def find_trashed(
        self, search: str, page: int, page_size: int
    ) -> tuple[list[GetTrashedMerchantDocumentsRow], int]: ...


class MerchantDocumentCommandService(Protocol):
    async def create(
        self, request: CreateMerchantDocumentRequest
    ) -> CreateMerchantDocumentRow: ...

    async def update(
        self, request: UpdateMerchantDocumentRequest
    ) -> UpdateMerchantDocumentRow: ...

    async def update_status(
        self, request: UpdateMerchantDocumentStatusRequest
    ) -> UpdateMerchantDocumentStatusRow: ...

    async def trash(self, document_id: int) -> MerchantDocument: ...

    async def restore(self, document_id: int) -> MerchantDocument: ...

    async def delete_permanent(self, document_id: int) -> bool: ...

    async def restore_all(self) -> bool: ...

    async def delete_all(self) -> bool: ...


__all__ = [
    "MerchantCommandService",
    "MerchantDocumentCommandService",
    "MerchantDocumentQueryService",
    "MerchantQueryService",
]

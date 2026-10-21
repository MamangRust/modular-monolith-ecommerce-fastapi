"""Merchant repository Two command repositories expose explicit `*_in_tx` variants so the service can commit the business write and its outbox event atomically (Phase 6 — transactional outbox). The transaction handle is an `sqlalchemy.ext.asyncio.AsyncConnection` yielded by `Database.transaction`, the equivalent of the `*`."""

from __future__ import annotations

from typing import Protocol

from sqlalchemy.ext.asyncio import AsyncConnection

from pkg.database.schema.merchant import (
    CreateMerchantRow,
    GetMerchantByIDRow,
    GetMerchantsActiveRow,
    GetMerchantsRow,
    GetMerchantsTrashedRow,
    GetUserByIDRow,
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


class MerchantQueryRepository(Protocol):
    async def find_all(
        self, search: str, page: int, page_size: int
    ) -> list[GetMerchantsRow]: ...

    async def find_active(
        self, search: str, page: int, page_size: int
    ) -> list[GetMerchantsActiveRow]: ...

    async def find_trashed(
        self, search: str, page: int, page_size: int
    ) -> list[GetMerchantsTrashedRow]: ...

    async def find_by_id(self, merchant_id: int) -> GetMerchantByIDRow: ...


class MerchantCommandRepository(Protocol):
    async def create(self, request: CreateMerchantRequest) -> CreateMerchantRow: ...

    async def create_in_tx(
        self, conn: AsyncConnection, request: CreateMerchantRequest
    ) -> CreateMerchantRow: ...

    async def update(self, request: UpdateMerchantRequest) -> UpdateMerchantRow: ...

    async def update_status(
        self, request: UpdateMerchantStatusRequest
    ) -> UpdateMerchantStatusRow: ...

    async def update_status_in_tx(
        self, conn: AsyncConnection, request: UpdateMerchantStatusRequest
    ) -> UpdateMerchantStatusRow: ...

    async def trash(self, merchant_id: int) -> Merchant: ...

    async def restore(self, merchant_id: int) -> Merchant: ...

    async def delete_permanent(self, merchant_id: int) -> bool: ...

    async def restore_all(self) -> bool: ...

    async def delete_all(self) -> bool: ...


class MerchantDocumentQueryRepository(Protocol):
    async def find_all(
        self, search: str, page: int, page_size: int
    ) -> tuple[list[GetMerchantDocumentsRow], int]: ...

    async def find_active(
        self, search: str, page: int, page_size: int
    ) -> tuple[list[GetActiveMerchantDocumentsRow], int]: ...

    async def find_trashed(
        self, search: str, page: int, page_size: int
    ) -> tuple[list[GetTrashedMerchantDocumentsRow], int]: ...

    async def find_by_id(self, document_id: int) -> GetMerchantDocumentRow: ...


class MerchantDocumentCommandRepository(Protocol):
    async def create(
        self, request: CreateMerchantDocumentRequest
    ) -> CreateMerchantDocumentRow: ...

    async def create_in_tx(
        self, conn: AsyncConnection, request: CreateMerchantDocumentRequest
    ) -> CreateMerchantDocumentRow: ...

    async def update(
        self, request: UpdateMerchantDocumentRequest
    ) -> UpdateMerchantDocumentRow: ...

    async def update_status(
        self, request: UpdateMerchantDocumentStatusRequest
    ) -> UpdateMerchantDocumentStatusRow: ...

    async def update_status_in_tx(
        self, conn: AsyncConnection, request: UpdateMerchantDocumentStatusRequest
    ) -> UpdateMerchantDocumentStatusRow: ...

    async def trash(self, document_id: int) -> MerchantDocument: ...

    async def restore(self, document_id: int) -> MerchantDocument: ...

    async def delete_permanent(self, document_id: int) -> bool: ...

    async def restore_all(self) -> bool: ...

    async def delete_all(self) -> bool: ...


class UserQueryRepository(Protocol):
    async def find_by_id(self, user_id: int) -> GetUserByIDRow: ...


__all__ = [
    "MerchantCommandRepository",
    "MerchantDocumentCommandRepository",
    "MerchantDocumentQueryRepository",
    "MerchantQueryRepository",
    "UserQueryRepository",
]

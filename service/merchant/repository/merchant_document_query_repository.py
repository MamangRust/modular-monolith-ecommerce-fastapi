"""Merchant document read repository. The list queries return `(rows, total_count)`; the total comes from the `COUNT(*) OVER` window on the first row (0 when the page is empty), exactly like the `totalCount` derivation. `FindById` maps a missing row to the shared `err_merchant_not_found` (the document repository reuses `ErrMerchantNotFound`). the `$1::TEXT IS NULL OR...` guard is dropped (binds a non-nil string), so only the three `ILIKE` terms matter; a NULL `note` never matches."""

from __future__ import annotations

from pkg.database.database import Database
from pkg.database.schema.merchant_document import (
    GetActiveMerchantDocumentsRow,
    GetMerchantDocumentRow,
    GetMerchantDocumentsRow,
    GetTrashedMerchantDocumentsRow,
)
from shared.errors import err_merchant_internal, err_merchant_not_found

_GET_MERCHANT_DOCUMENTS = """
SELECT
    document_id,
    merchant_id,
    document_type,
    document_url,
    status,
    note,
    uploaded_at,
    created_at,
    updated_at,
    COUNT(*) OVER () AS total_count
FROM merchant_documents
WHERE
    deleted_at IS NULL
    AND (
        document_type ILIKE '%' || :search || '%'
        OR status ILIKE '%' || :search || '%'
        OR note ILIKE '%' || :search || '%'
    )
ORDER BY document_id
LIMIT :limit
OFFSET :offset
"""

_GET_ACTIVE_MERCHANT_DOCUMENTS = """
SELECT
    document_id,
    merchant_id,
    document_type,
    document_url,
    status,
    note,
    uploaded_at,
    created_at,
    updated_at,
    deleted_at,
    COUNT(*) OVER () AS total_count
FROM merchant_documents
WHERE
    deleted_at IS NULL
    AND status != 'deleted'
    AND (
        document_type ILIKE '%' || :search || '%'
        OR status ILIKE '%' || :search || '%'
        OR note ILIKE '%' || :search || '%'
    )
ORDER BY document_id
LIMIT :limit
OFFSET :offset
"""

_GET_TRASHED_MERCHANT_DOCUMENTS = """
SELECT
    document_id,
    merchant_id,
    document_type,
    document_url,
    status,
    note,
    uploaded_at,
    created_at,
    updated_at,
    deleted_at,
    COUNT(*) OVER () AS total_count
FROM merchant_documents
WHERE
    deleted_at IS NOT NULL
    AND (
        document_type ILIKE '%' || :search || '%'
        OR status ILIKE '%' || :search || '%'
        OR note ILIKE '%' || :search || '%'
    )
ORDER BY document_id
LIMIT :limit
OFFSET :offset
"""

_GET_MERCHANT_DOCUMENT = """
SELECT
    document_id,
    merchant_id,
    document_type,
    document_url,
    status,
    note,
    uploaded_at,
    created_at,
    updated_at
FROM merchant_documents
WHERE
    document_id = :document_id
    AND deleted_at IS NULL
"""


def _total(rows: list) -> int:
    return rows[0].total_count if rows else 0


class MerchantDocumentQueryRepositoryImpl:
    def __init__(self, db: Database) -> None:
        self._db = db

    async def find_all(
        self, search: str, page: int, page_size: int
    ) -> tuple[list[GetMerchantDocumentsRow], int]:
        offset = (page - 1) * page_size
        try:
            raw = await self._db.select(
                _GET_MERCHANT_DOCUMENTS,
                {"search": search, "limit": page_size, "offset": offset},
            )
        except Exception as exc:
            raise err_merchant_internal.with_internal(exc) from exc
        rows = [GetMerchantDocumentsRow.from_row(row) for row in raw]
        return rows, _total(rows)

    async def find_active(
        self, search: str, page: int, page_size: int
    ) -> tuple[list[GetActiveMerchantDocumentsRow], int]:
        offset = (page - 1) * page_size
        try:
            raw = await self._db.select(
                _GET_ACTIVE_MERCHANT_DOCUMENTS,
                {"search": search, "limit": page_size, "offset": offset},
            )
        except Exception as exc:
            raise err_merchant_internal.with_internal(exc) from exc
        rows = [GetActiveMerchantDocumentsRow.from_row(row) for row in raw]
        return rows, _total(rows)

    async def find_trashed(
        self, search: str, page: int, page_size: int
    ) -> tuple[list[GetTrashedMerchantDocumentsRow], int]:
        offset = (page - 1) * page_size
        try:
            raw = await self._db.select(
                _GET_TRASHED_MERCHANT_DOCUMENTS,
                {"search": search, "limit": page_size, "offset": offset},
            )
        except Exception as exc:
            raise err_merchant_internal.with_internal(exc) from exc
        rows = [GetTrashedMerchantDocumentsRow.from_row(row) for row in raw]
        return rows, _total(rows)

    async def find_by_id(self, document_id: int) -> GetMerchantDocumentRow:
        try:
            row = await self._db.scalar(
                _GET_MERCHANT_DOCUMENT, {"document_id": document_id}
            )
        except Exception as exc:
            raise err_merchant_internal.with_internal(exc) from exc
        if row is None:
            raise err_merchant_not_found
        return GetMerchantDocumentRow.from_row(row)


__all__ = ["MerchantDocumentQueryRepositoryImpl"]

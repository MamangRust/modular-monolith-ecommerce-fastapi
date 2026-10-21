"""Merchant document write repository. Create hardcodes `status = 'pending'` and a NULL note, the SQL."""

from __future__ import annotations

from typing import Any

from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncConnection

from pkg.database.database import Database
from pkg.database.schema.merchant_document import (
    CreateMerchantDocumentRow,
    MerchantDocument,
    UpdateMerchantDocumentRow,
    UpdateMerchantDocumentStatusRow,
)
from shared.domain.requests.merchant import (
    CreateMerchantDocumentRequest,
    UpdateMerchantDocumentRequest,
    UpdateMerchantDocumentStatusRequest,
)
from shared.errors import (
    AppError,
    err_merchant_internal,
    err_merchant_not_found,
)

_CREATE_MERCHANT_DOCUMENT = """
INSERT INTO merchant_documents (
    merchant_id, document_type, document_url, status, note, uploaded_at, updated_at
)
VALUES (
    :merchant_id, :document_type, :document_url, :status, :note,
    CURRENT_TIMESTAMP, CURRENT_TIMESTAMP
)
RETURNING
    document_id, merchant_id, document_type, document_url, status, note,
    uploaded_at, created_at, updated_at
"""

_UPDATE_MERCHANT_DOCUMENT = """
UPDATE merchant_documents
SET
    document_type = :document_type,
    document_url = :document_url,
    status = :status,
    note = :note,
    updated_at = CURRENT_TIMESTAMP
WHERE
    document_id = :document_id
    AND deleted_at IS NULL
RETURNING
    document_id, merchant_id, document_type, document_url, status, note,
    uploaded_at, created_at, updated_at
"""

_UPDATE_MERCHANT_DOCUMENT_STATUS = """
UPDATE merchant_documents
SET
    status = :status,
    note = :note,
    updated_at = CURRENT_TIMESTAMP
WHERE
    document_id = :document_id
    AND deleted_at IS NULL
RETURNING
    document_id, merchant_id, document_type, document_url, status, note,
    uploaded_at, created_at, updated_at
"""

_TRASH_MERCHANT_DOCUMENT = """
UPDATE merchant_documents
SET
    deleted_at = CURRENT_TIMESTAMP
WHERE
    document_id = :document_id
    AND deleted_at IS NULL
RETURNING
    document_id, merchant_id, document_type, document_url, status, note,
    uploaded_at, created_at, updated_at, deleted_at
"""

_RESTORE_MERCHANT_DOCUMENT = """
UPDATE merchant_documents
SET
    deleted_at = NULL
WHERE
    document_id = :document_id
    AND deleted_at IS NOT NULL
RETURNING
    document_id, merchant_id, document_type, document_url, status, note,
    uploaded_at, created_at, updated_at, deleted_at
"""

_DELETE_MERCHANT_DOCUMENT_PERMANENTLY = """
DELETE FROM merchant_documents
WHERE document_id = :document_id AND deleted_at IS NOT NULL
"""

_RESTORE_ALL_MERCHANT_DOCUMENTS = (
    "UPDATE merchant_documents SET deleted_at = NULL WHERE deleted_at IS NOT NULL"
)

_DELETE_ALL_PERMANENT_MERCHANT_DOCUMENTS = (
    "DELETE FROM merchant_documents WHERE deleted_at IS NOT NULL"
)


def _nullable(value: str | None) -> str | None:
    return value or None


class MerchantDocumentCommandRepositoryImpl:
    def __init__(self, db: Database) -> None:
        self._db = db

    async def _returning(
        self,
        sql: str,
        params: dict[str, Any],
        conn: AsyncConnection | None = None,
    ) -> dict[str, Any] | None:
        if conn is None:
            return await self._db.execute(sql, params)
        result = await conn.execute(text(sql), params)
        if not result.returns_rows:
            return None
        row = result.mappings().first()
        return dict(row) if row is not None else None

    async def create(
        self, request: CreateMerchantDocumentRequest
    ) -> CreateMerchantDocumentRow:
        return await self._create(request, conn=None)

    async def create_in_tx(
        self, conn: AsyncConnection, request: CreateMerchantDocumentRequest
    ) -> CreateMerchantDocumentRow:
        return await self._create(request, conn=conn)

    async def _create(
        self, request: CreateMerchantDocumentRequest, conn: AsyncConnection | None
    ) -> CreateMerchantDocumentRow:
        params = {
            "merchant_id": request.merchant_id,
            "document_type": request.document_type,
            "document_url": request.document_url,
            "status": "pending",
            "note": None,
        }
        try:
            row = await self._returning(_CREATE_MERCHANT_DOCUMENT, params, conn)
        except AppError:
            raise
        except Exception as exc:
            raise err_merchant_internal.with_internal(exc) from exc
        if row is None:
            raise err_merchant_not_found
        return CreateMerchantDocumentRow.from_row(row)

    async def update(
        self, request: UpdateMerchantDocumentRequest
    ) -> UpdateMerchantDocumentRow:
        params = {
            "document_id": request.document_id,
            "document_type": request.document_type,
            "document_url": request.document_url,
            "status": request.status,
            "note": _nullable(request.note),
        }
        try:
            row = await self._returning(_UPDATE_MERCHANT_DOCUMENT, params)
        except AppError:
            raise
        except Exception as exc:
            raise err_merchant_internal.with_internal(exc) from exc
        if row is None:
            raise err_merchant_not_found
        return UpdateMerchantDocumentRow.from_row(row)

    async def update_status(
        self, request: UpdateMerchantDocumentStatusRequest
    ) -> UpdateMerchantDocumentStatusRow:
        return await self._update_status(request, conn=None)

    async def update_status_in_tx(
        self, conn: AsyncConnection, request: UpdateMerchantDocumentStatusRequest
    ) -> UpdateMerchantDocumentStatusRow:
        return await self._update_status(request, conn=conn)

    async def _update_status(
        self,
        request: UpdateMerchantDocumentStatusRequest,
        conn: AsyncConnection | None,
    ) -> UpdateMerchantDocumentStatusRow:
        params = {
            "document_id": request.document_id,
            "status": request.status,
            "note": _nullable(request.note),
        }
        try:
            row = await self._returning(_UPDATE_MERCHANT_DOCUMENT_STATUS, params, conn)
        except AppError:
            raise
        except Exception as exc:
            raise err_merchant_internal.with_internal(exc) from exc
        if row is None:
            raise err_merchant_not_found
        return UpdateMerchantDocumentStatusRow.from_row(row)

    async def trash(self, document_id: int) -> MerchantDocument:
        try:
            row = await self._returning(
                _TRASH_MERCHANT_DOCUMENT, {"document_id": document_id}
            )
        except AppError:
            raise
        except Exception as exc:
            raise err_merchant_internal.with_internal(exc) from exc
        if row is None:
            raise err_merchant_not_found
        return MerchantDocument.from_row(row)

    async def restore(self, document_id: int) -> MerchantDocument:
        try:
            row = await self._returning(
                _RESTORE_MERCHANT_DOCUMENT, {"document_id": document_id}
            )
        except AppError:
            raise
        except Exception as exc:
            raise err_merchant_internal.with_internal(exc) from exc
        if row is None:
            raise err_merchant_not_found
        return MerchantDocument.from_row(row)

    async def delete_permanent(self, document_id: int) -> bool:
        try:
            await self._db.execute(
                _DELETE_MERCHANT_DOCUMENT_PERMANENTLY, {"document_id": document_id}
            )
        except AppError:
            raise
        except Exception as exc:
            raise err_merchant_internal.with_internal(exc) from exc
        return True

    async def restore_all(self) -> bool:
        try:
            await self._db.execute(_RESTORE_ALL_MERCHANT_DOCUMENTS)
        except AppError:
            raise
        except Exception as exc:
            raise err_merchant_internal.with_internal(exc) from exc
        return True

    async def delete_all(self) -> bool:
        try:
            await self._db.execute(_DELETE_ALL_PERMANENT_MERCHANT_DOCUMENTS)
        except AppError:
            raise
        except Exception as exc:
            raise err_merchant_internal.with_internal(exc) from exc
        return True


__all__ = ["MerchantDocumentCommandRepositoryImpl"]

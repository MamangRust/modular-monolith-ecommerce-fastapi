"""Merchant write repository. `create`/`update`/`update_status` map a missing row (`None` from the `RETURNING` projection) to `err_merchant_not_found`; every other failure maps to the matching sentinel. `delete_permanent`/`delete_all` surface a foreign key violation (Postgres `23503`) as a 409 conflict, the `pgErr.Code == "23503"` branch; the bulk restore/delete otherwise ignore affected rows, so operating on nothing still reports success. `create_in_tx`/`update_status_in_tx` run on the caller's transaction connection so the outbox event commits atomically with the write."""

from __future__ import annotations

from typing import Any

from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncConnection

from pkg.database.database import Database
from pkg.database.errors import is_foreign_key_violation
from pkg.database.schema.merchant import (
    CreateMerchantRow,
    Merchant,
    UpdateMerchantRow,
    UpdateMerchantStatusRow,
)
from shared.domain.requests.merchant import (
    CreateMerchantRequest,
    UpdateMerchantRequest,
    UpdateMerchantStatusRequest,
)
from shared.errors import (
    AppError,
    err_create_merchant,
    err_delete_all_merchants,
    err_delete_merchant_permanent,
    err_merchant_internal,
    err_merchant_not_found,
    err_restore_all_merchants,
    err_restore_merchant,
    err_trashed_merchant,
    err_update_merchant,
    new_conflict_error,
)

_CREATE_MERCHANT = """
INSERT INTO merchants (
    user_id, name, description, address, contact_email, contact_phone, status
)
VALUES (
    :user_id, :name, :description, :address, :contact_email, :contact_phone, :status
)
RETURNING
    merchant_id, user_id, name, description, address, contact_email,
    contact_phone, status, created_at, updated_at
"""

_UPDATE_MERCHANT = """
UPDATE merchants
SET
    name = :name,
    description = :description,
    address = :address,
    contact_email = :contact_email,
    contact_phone = :contact_phone,
    status = :status,
    updated_at = CURRENT_TIMESTAMP
WHERE
    merchant_id = :merchant_id
    AND deleted_at IS NULL
RETURNING
    merchant_id, user_id, name, description, address, contact_email,
    contact_phone, status, created_at, updated_at
"""

_UPDATE_MERCHANT_STATUS = """
UPDATE merchants
SET
    status = :status,
    updated_at = CURRENT_TIMESTAMP
WHERE
    merchant_id = :merchant_id
    AND deleted_at IS NULL
RETURNING
    merchant_id, user_id, name, description, address, contact_email,
    contact_phone, status, created_at, updated_at
"""

_TRASH_MERCHANT = """
UPDATE merchants
SET
    deleted_at = CURRENT_TIMESTAMP
WHERE
    merchant_id = :merchant_id
    AND deleted_at IS NULL
RETURNING
    merchant_id, user_id, name, description, address, contact_email,
    contact_phone, status, created_at, updated_at, deleted_at
"""

_RESTORE_MERCHANT = """
UPDATE merchants
SET
    deleted_at = NULL
WHERE
    merchant_id = :merchant_id
    AND deleted_at IS NOT NULL
RETURNING
    merchant_id, user_id, name, description, address, contact_email,
    contact_phone, status, created_at, updated_at, deleted_at
"""

_DELETE_MERCHANT_PERMANENTLY = """
DELETE FROM merchants
WHERE merchant_id = :merchant_id AND deleted_at IS NOT NULL
"""

_RESTORE_ALL_MERCHANTS = (
    "UPDATE merchants SET deleted_at = NULL WHERE deleted_at IS NOT NULL"
)

_DELETE_ALL_PERMANENT_MERCHANTS = (
    "DELETE FROM merchants WHERE deleted_at IS NOT NULL"
)


def _nullable(value: str | None) -> str | None:
    """empty -> NULL."""
    return value or None


class MerchantCommandRepositoryImpl:
    def __init__(self, db: Database) -> None:
        self._db = db

    async def _returning(
        self,
        sql: str,
        params: dict[str, Any],
        conn: AsyncConnection | None = None,
    ) -> dict[str, Any] | None:
        """Run a `RETURNING` statement, returning the first row or None."""
        if conn is None:
            return await self._db.execute(sql, params)
        result = await conn.execute(text(sql), params)
        if not result.returns_rows:
            return None
        row = result.mappings().first()
        return dict(row) if row is not None else None

    async def create(self, request: CreateMerchantRequest) -> CreateMerchantRow:
        return await self._create(request, conn=None)

    async def create_in_tx(
        self, conn: AsyncConnection, request: CreateMerchantRequest
    ) -> CreateMerchantRow:
        return await self._create(request, conn=conn)

    async def _create(
        self, request: CreateMerchantRequest, conn: AsyncConnection | None
    ) -> CreateMerchantRow:
        params = {
            "user_id": request.user_id,
            "name": request.name,
            "description": _nullable(request.description),
            "address": _nullable(request.address),
            "contact_email": _nullable(request.contact_email),
            "contact_phone": _nullable(request.contact_phone),
            # hardcodes "active" on create and ignores the body status.
            "status": "active",
        }
        try:
            row = await self._returning(_CREATE_MERCHANT, params, conn)
        except AppError:
            raise
        except Exception as exc:
            raise err_create_merchant.with_internal(exc) from exc
        if row is None:
            raise err_merchant_not_found
        return CreateMerchantRow.from_row(row)

    async def update(self, request: UpdateMerchantRequest) -> UpdateMerchantRow:
        params = {
            "merchant_id": request.merchant_id,
            "name": request.name,
            "description": _nullable(request.description),
            "address": _nullable(request.address),
            "contact_email": _nullable(request.contact_email),
            "contact_phone": _nullable(request.contact_phone),
            "status": request.status,
        }
        try:
            row = await self._returning(_UPDATE_MERCHANT, params)
        except AppError:
            raise
        except Exception as exc:
            raise err_update_merchant.with_internal(exc) from exc
        if row is None:
            raise err_merchant_not_found
        return UpdateMerchantRow.from_row(row)

    async def update_status(
        self, request: UpdateMerchantStatusRequest
    ) -> UpdateMerchantStatusRow:
        return await self._update_status(request, conn=None)

    async def update_status_in_tx(
        self, conn: AsyncConnection, request: UpdateMerchantStatusRequest
    ) -> UpdateMerchantStatusRow:
        return await self._update_status(request, conn=conn)

    async def _update_status(
        self, request: UpdateMerchantStatusRequest, conn: AsyncConnection | None
    ) -> UpdateMerchantStatusRow:
        params = {"merchant_id": request.merchant_id, "status": request.status}
        try:
            row = await self._returning(_UPDATE_MERCHANT_STATUS, params, conn)
        except AppError:
            raise
        except Exception as exc:
            raise err_merchant_internal.with_internal(exc) from exc
        if row is None:
            raise err_merchant_not_found
        return UpdateMerchantStatusRow.from_row(row)

    async def trash(self, merchant_id: int) -> Merchant:
        try:
            row = await self._returning(_TRASH_MERCHANT, {"merchant_id": merchant_id})
        except AppError:
            raise
        except Exception as exc:
            raise err_trashed_merchant.with_internal(exc) from exc
        if row is None:
            raise err_merchant_not_found
        return Merchant.from_row(row)

    async def restore(self, merchant_id: int) -> Merchant:
        try:
            row = await self._returning(_RESTORE_MERCHANT, {"merchant_id": merchant_id})
        except AppError:
            raise
        except Exception as exc:
            raise err_restore_merchant.with_internal(exc) from exc
        if row is None:
            raise err_merchant_not_found
        return Merchant.from_row(row)

    async def delete_permanent(self, merchant_id: int) -> bool:
        try:
            await self._db.execute(
                _DELETE_MERCHANT_PERMANENTLY, {"merchant_id": merchant_id}
            )
        except AppError:
            raise
        except Exception as exc:
            if is_foreign_key_violation(exc):
                raise new_conflict_error(
                    "cannot permanently delete merchant while related records exist"
                ).with_internal(exc) from exc
            raise err_delete_merchant_permanent.with_internal(exc) from exc
        return True

    async def restore_all(self) -> bool:
        try:
            await self._db.execute(_RESTORE_ALL_MERCHANTS)
        except AppError:
            raise
        except Exception as exc:
            raise err_restore_all_merchants.with_internal(exc) from exc
        return True

    async def delete_all(self) -> bool:
        try:
            await self._db.execute(_DELETE_ALL_PERMANENT_MERCHANTS)
        except AppError:
            raise
        except Exception as exc:
            if is_foreign_key_violation(exc):
                raise new_conflict_error(
                    "cannot permanently delete merchants while related records exist"
                ).with_internal(exc) from exc
            raise err_delete_all_merchants.with_internal(exc) from exc
        return True


__all__ = ["MerchantCommandRepositoryImpl"]

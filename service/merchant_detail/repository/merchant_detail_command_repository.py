"""merchant_detail write repository. `create`/`update`/`trash`/`restore` map a missing row (`None` from the `RETURNING` projection) to `err_merchant_detail_not_found`; every other failure maps to the matching sentinel. always sends non-nil pointers for the nullable string columns (`&request.DisplayName`), so an empty value is stored as `''`, never NULL — passes the raw strings, not `_nullable(...)`."""

from __future__ import annotations

from typing import Any

from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncConnection

from pkg.database.database import Database
from pkg.database.schema.merchant_detail import (
    CreateMerchantDetailRow,
    MerchantDetail,
    UpdateMerchantDetailRow,
)
from shared.domain.requests.merchant_detail import (
    CreateMerchantDetailRequest,
    UpdateMerchantDetailRequest,
)
from shared.errors import (
    AppError,
    err_create_merchant_detail,
    err_delete_all_permanent_merchant_details,
    err_delete_permanent_merchant_detail,
    err_merchant_detail_not_found,
    err_restore_all_merchant_details,
    err_restore_merchant_detail,
    err_trash_merchant_detail,
    err_update_merchant_detail,
)

_RETURNING_COLUMNS = """
    merchant_detail_id,
    merchant_id,
    display_name,
    cover_image_url,
    logo_url,
    short_description,
    website_url,
    created_at,
    updated_at
"""

_CREATE_MERCHANT_DETAIL = f"""
INSERT INTO merchant_details (
    merchant_id, display_name, cover_image_url, logo_url,
    short_description, website_url
)
VALUES (
    :merchant_id, :display_name, :cover_image_url, :logo_url,
    :short_description, :website_url
)
RETURNING
{_RETURNING_COLUMNS}
"""

_UPDATE_MERCHANT_DETAIL = f"""
UPDATE merchant_details
SET
    display_name = :display_name,
    cover_image_url = :cover_image_url,
    logo_url = :logo_url,
    short_description = :short_description,
    website_url = :website_url,
    updated_at = CURRENT_TIMESTAMP
WHERE
    merchant_detail_id = :merchant_detail_id
    AND deleted_at IS NULL
RETURNING
{_RETURNING_COLUMNS}
"""

_TRASH_MERCHANT_DETAIL = f"""
UPDATE merchant_details
SET deleted_at = CURRENT_TIMESTAMP
WHERE
    merchant_detail_id = :merchant_detail_id
    AND deleted_at IS NULL
RETURNING
{_RETURNING_COLUMNS},
    deleted_at
"""

_RESTORE_MERCHANT_DETAIL = f"""
UPDATE merchant_details
SET deleted_at = NULL
WHERE
    merchant_detail_id = :merchant_detail_id
    AND deleted_at IS NOT NULL
RETURNING
{_RETURNING_COLUMNS},
    deleted_at
"""

_DELETE_MERCHANT_DETAIL_PERMANENTLY = """
DELETE FROM merchant_details
WHERE
    merchant_detail_id = :merchant_detail_id
    AND deleted_at IS NOT NULL
"""

_RESTORE_ALL_MERCHANT_DETAILS = (
    "UPDATE merchant_details SET deleted_at = NULL WHERE deleted_at IS NOT NULL"
)

_DELETE_ALL_PERMANENT_MERCHANT_DETAILS = (
    "DELETE FROM merchant_details WHERE deleted_at IS NOT NULL"
)


class MerchantDetailCommandRepositoryImpl:
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
        self, request: CreateMerchantDetailRequest
    ) -> CreateMerchantDetailRow:
        params = {
            "merchant_id": request.merchant_id,
            "display_name": request.display_name,
            "cover_image_url": request.cover_image_url,
            "logo_url": request.logo_url,
            "short_description": request.short_description,
            "website_url": request.website_url,
        }
        try:
            row = await self._returning(_CREATE_MERCHANT_DETAIL, params)
        except AppError:
            raise
        except Exception as exc:
            raise err_create_merchant_detail.with_internal(exc) from exc
        if row is None:
            raise err_merchant_detail_not_found
        return CreateMerchantDetailRow.from_row(row)

    async def update(
        self, request: UpdateMerchantDetailRequest
    ) -> UpdateMerchantDetailRow:
        params = {
            "merchant_detail_id": request.merchant_detail_id,
            "display_name": request.display_name,
            "cover_image_url": request.cover_image_url,
            "logo_url": request.logo_url,
            "short_description": request.short_description,
            "website_url": request.website_url,
        }
        try:
            row = await self._returning(_UPDATE_MERCHANT_DETAIL, params)
        except AppError:
            raise
        except Exception as exc:
            raise err_update_merchant_detail.with_internal(exc) from exc
        if row is None:
            raise err_merchant_detail_not_found
        return UpdateMerchantDetailRow.from_row(row)

    async def trash(self, merchant_detail_id: int) -> MerchantDetail:
        try:
            row = await self._returning(
                _TRASH_MERCHANT_DETAIL, {"merchant_detail_id": merchant_detail_id}
            )
        except AppError:
            raise
        except Exception as exc:
            raise err_trash_merchant_detail.with_internal(exc) from exc
        if row is None:
            raise err_merchant_detail_not_found
        return MerchantDetail.from_row(row)

    async def restore(self, merchant_detail_id: int) -> MerchantDetail:
        try:
            row = await self._returning(
                _RESTORE_MERCHANT_DETAIL, {"merchant_detail_id": merchant_detail_id}
            )
        except AppError:
            raise
        except Exception as exc:
            raise err_restore_merchant_detail.with_internal(exc) from exc
        if row is None:
            raise err_merchant_detail_not_found
        return MerchantDetail.from_row(row)

    async def delete_permanent(self, merchant_detail_id: int) -> bool:
        try:
            await self._db.execute(
                _DELETE_MERCHANT_DETAIL_PERMANENTLY,
                {"merchant_detail_id": merchant_detail_id},
            )
        except AppError:
            raise
        except Exception as exc:
            raise err_delete_permanent_merchant_detail.with_internal(exc) from exc
        return True

    async def restore_all(self) -> bool:
        try:
            await self._db.execute(_RESTORE_ALL_MERCHANT_DETAILS)
        except AppError:
            raise
        except Exception as exc:
            raise err_restore_all_merchant_details.with_internal(exc) from exc
        return True

    async def delete_all(self) -> bool:
        try:
            await self._db.execute(_DELETE_ALL_PERMANENT_MERCHANT_DETAILS)
        except AppError:
            raise
        except Exception as exc:
            raise err_delete_all_permanent_merchant_details.with_internal(exc) from exc
        return True


__all__ = ["MerchantDetailCommandRepositoryImpl"]

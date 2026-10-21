"""merchant_business write repository. `create`/`update`/`trash`/`restore` map a missing row (`None` from the `RETURNING` projection) to `err_merchant_business_not_found`; every other failure maps to the matching sentinel. Nullable columns follow `stringPtr` / `int32Ptr`: an empty string becomes NULL, and a zero int becomes NULL. Validation requires `business_type`/`tax_id` non-empty, `established_year` in 1900..2100 and `number_of_employees >= 1`, so in practice only `website_url` can be empty; the int branches are still."""

from __future__ import annotations

from typing import Any

from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncConnection

from pkg.database.database import Database
from pkg.database.schema.merchant_business import (
    CreateMerchantBusinessInformationRow,
    MerchantBusinessInformation,
    UpdateMerchantBusinessInformationRow,
)
from shared.domain.requests.merchant_business import (
    CreateMerchantBusinessInformationRequest,
    UpdateMerchantBusinessInformationRequest,
)
from shared.errors import (
    AppError,
    err_create_merchant_business,
    err_delete_all_permanent_merchant_businesses,
    err_delete_permanent_merchant_business,
    err_merchant_business_not_found,
    err_restore_all_merchant_businesses,
    err_restore_merchant_business,
    err_trash_merchant_business,
    err_update_merchant_business,
)

_RETURNING_COLUMNS = """
    merchant_business_info_id,
    merchant_id,
    business_type,
    tax_id,
    established_year,
    number_of_employees,
    website_url,
    created_at,
    updated_at
"""

_CREATE_MERCHANT_BUSINESS = f"""
INSERT INTO merchant_business_information (
    merchant_id, business_type, tax_id,
    established_year, number_of_employees, website_url
)
VALUES (
    :merchant_id, :business_type, :tax_id,
    :established_year, :number_of_employees, :website_url
)
RETURNING
{_RETURNING_COLUMNS}
"""

_UPDATE_MERCHANT_BUSINESS = f"""
UPDATE merchant_business_information
SET
    business_type = :business_type,
    tax_id = :tax_id,
    established_year = :established_year,
    number_of_employees = :number_of_employees,
    website_url = :website_url,
    updated_at = CURRENT_TIMESTAMP
WHERE
    merchant_business_info_id = :merchant_business_info_id
    AND deleted_at IS NULL
RETURNING
{_RETURNING_COLUMNS}
"""

_TRASH_MERCHANT_BUSINESS = f"""
UPDATE merchant_business_information
SET deleted_at = CURRENT_TIMESTAMP
WHERE
    merchant_business_info_id = :merchant_business_info_id
    AND deleted_at IS NULL
RETURNING
{_RETURNING_COLUMNS},
    deleted_at
"""

_RESTORE_MERCHANT_BUSINESS = f"""
UPDATE merchant_business_information
SET deleted_at = NULL
WHERE
    merchant_business_info_id = :merchant_business_info_id
    AND deleted_at IS NOT NULL
RETURNING
{_RETURNING_COLUMNS},
    deleted_at
"""

_DELETE_MERCHANT_BUSINESS_PERMANENTLY = """
DELETE FROM merchant_business_information
WHERE
    merchant_business_info_id = :merchant_business_info_id
    AND deleted_at IS NOT NULL
"""

_RESTORE_ALL_MERCHANT_BUSINESSES = (
    "UPDATE merchant_business_information SET deleted_at = NULL "
    "WHERE deleted_at IS NOT NULL"
)

_DELETE_ALL_PERMANENT_MERCHANT_BUSINESSES = (
    "DELETE FROM merchant_business_information WHERE deleted_at IS NOT NULL"
)


def _nullable_str(value: str) -> str | None:
    """empty -> NULL."""
    return value if value != "" else None


def _nullable_int(value: int) -> int | None:
    """zero -> NULL."""
    return value if value != 0 else None


class MerchantBusinessCommandRepositoryImpl:
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
        self, request: CreateMerchantBusinessInformationRequest
    ) -> CreateMerchantBusinessInformationRow:
        params = {
            "merchant_id": request.merchant_id,
            "business_type": _nullable_str(request.business_type),
            "tax_id": _nullable_str(request.tax_id),
            "established_year": _nullable_int(request.established_year),
            "number_of_employees": _nullable_int(request.number_of_employees),
            "website_url": _nullable_str(request.website_url),
        }
        try:
            row = await self._returning(_CREATE_MERCHANT_BUSINESS, params)
        except AppError:
            raise
        except Exception as exc:
            raise err_create_merchant_business.with_internal(exc) from exc
        if row is None:
            raise err_merchant_business_not_found
        return CreateMerchantBusinessInformationRow.from_row(row)

    async def update(
        self, request: UpdateMerchantBusinessInformationRequest
    ) -> UpdateMerchantBusinessInformationRow:
        params = {
            "merchant_business_info_id": request.merchant_business_info_id,
            "business_type": _nullable_str(request.business_type),
            "tax_id": _nullable_str(request.tax_id),
            "established_year": _nullable_int(request.established_year),
            "number_of_employees": _nullable_int(request.number_of_employees),
            "website_url": _nullable_str(request.website_url),
        }
        try:
            row = await self._returning(_UPDATE_MERCHANT_BUSINESS, params)
        except AppError:
            raise
        except Exception as exc:
            raise err_update_merchant_business.with_internal(exc) from exc
        if row is None:
            raise err_merchant_business_not_found
        return UpdateMerchantBusinessInformationRow.from_row(row)

    async def trash(
        self, merchant_business_info_id: int
    ) -> MerchantBusinessInformation:
        try:
            row = await self._returning(
                _TRASH_MERCHANT_BUSINESS,
                {"merchant_business_info_id": merchant_business_info_id},
            )
        except AppError:
            raise
        except Exception as exc:
            raise err_trash_merchant_business.with_internal(exc) from exc
        if row is None:
            raise err_merchant_business_not_found
        return MerchantBusinessInformation.from_row(row)

    async def restore(
        self, merchant_business_info_id: int
    ) -> MerchantBusinessInformation:
        try:
            row = await self._returning(
                _RESTORE_MERCHANT_BUSINESS,
                {"merchant_business_info_id": merchant_business_info_id},
            )
        except AppError:
            raise
        except Exception as exc:
            raise err_restore_merchant_business.with_internal(exc) from exc
        if row is None:
            raise err_merchant_business_not_found
        return MerchantBusinessInformation.from_row(row)

    async def delete_permanent(self, merchant_business_info_id: int) -> bool:
        try:
            await self._db.execute(
                _DELETE_MERCHANT_BUSINESS_PERMANENTLY,
                {"merchant_business_info_id": merchant_business_info_id},
            )
        except AppError:
            raise
        except Exception as exc:
            raise err_delete_permanent_merchant_business.with_internal(exc) from exc
        return True

    async def restore_all(self) -> bool:
        try:
            await self._db.execute(_RESTORE_ALL_MERCHANT_BUSINESSES)
        except AppError:
            raise
        except Exception as exc:
            raise err_restore_all_merchant_businesses.with_internal(exc) from exc
        return True

    async def delete_all(self) -> bool:
        try:
            await self._db.execute(_DELETE_ALL_PERMANENT_MERCHANT_BUSINESSES)
        except AppError:
            raise
        except Exception as exc:
            raise err_delete_all_permanent_merchant_businesses.with_internal(
                exc
            ) from exc
        return True


__all__ = ["MerchantBusinessCommandRepositoryImpl"]

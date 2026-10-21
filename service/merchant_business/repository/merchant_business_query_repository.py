"""merchant_business read repository. SQL is kept verbatim from the reference, including the `COUNT(*) OVER` window that supplies `total_count` in the same round trip as the page. the `LOWER(m.name) LIKE LOWER(CONCAT('%', $1::text, '%')` guard becomes an `ILIKE` (equivalent); binds a plain `string` (never nil), so no null branch is needed. An empty search matches every row. `find_by_id` maps a missing row to `err_merchant_business_not_found` (404) and any other failure to `err_merchant_business_internal` (500), matching the `pgx.ErrNoRows` branch (note: this uses the repository's *internal* sentinel, unlike merchant_award's dedicated find-by-id sentinel)."""

from __future__ import annotations

from pkg.database.database import Database
from pkg.database.schema.merchant_business import (
    GetMerchantBusinessInformationRow,
    GetMerchantsBusinessInformationActiveRow,
    GetMerchantsBusinessInformationRow,
    GetMerchantsBusinessInformationTrashedRow,
)
from shared.errors import (
    err_find_active_merchant_businesses,
    err_find_all_merchant_businesses,
    err_find_trashed_merchant_businesses,
    err_merchant_business_internal,
    err_merchant_business_not_found,
)

_BASE_COLUMNS = """
    mbi.merchant_business_info_id,
    mbi.merchant_id,
    mbi.business_type,
    mbi.tax_id,
    mbi.established_year,
    mbi.number_of_employees,
    mbi.website_url,
    mbi.created_at,
    mbi.updated_at
"""

_GET_MERCHANT_BUSINESSES = f"""
SELECT
{_BASE_COLUMNS},
    m.name AS merchant_name,
    COUNT(*) OVER () AS total_count
FROM
    merchant_business_information mbi
    JOIN merchants m ON mbi.merchant_id = m.merchant_id
WHERE
    mbi.deleted_at IS NULL
    AND m.name ILIKE '%' || :search || '%'
LIMIT :limit
OFFSET :offset
"""

_GET_MERCHANT_BUSINESSES_ACTIVE = f"""
SELECT
{_BASE_COLUMNS},
    mbi.deleted_at,
    m.name AS merchant_name,
    COUNT(*) OVER () AS total_count
FROM
    merchant_business_information mbi
    JOIN merchants m ON mbi.merchant_id = m.merchant_id
WHERE
    mbi.deleted_at IS NULL
    AND m.deleted_at IS NULL
    AND m.name ILIKE '%' || :search || '%'
LIMIT :limit
OFFSET :offset
"""

_GET_MERCHANT_BUSINESSES_TRASHED = f"""
SELECT
{_BASE_COLUMNS},
    mbi.deleted_at,
    m.name AS merchant_name,
    COUNT(*) OVER () AS total_count
FROM
    merchant_business_information mbi
    JOIN merchants m ON mbi.merchant_id = m.merchant_id
WHERE
    mbi.deleted_at IS NOT NULL
    AND m.name ILIKE '%' || :search || '%'
LIMIT :limit
OFFSET :offset
"""

_GET_MERCHANT_BUSINESS = f"""
SELECT
{_BASE_COLUMNS}
FROM merchant_business_information mbi
WHERE
    merchant_business_info_id = :merchant_business_info_id
    AND deleted_at IS NULL
"""


class MerchantBusinessQueryRepositoryImpl:
    def __init__(self, db: Database) -> None:
        self._db = db

    async def find_all(
        self, search: str, page: int, page_size: int
    ) -> list[GetMerchantsBusinessInformationRow]:
        offset = (page - 1) * page_size
        try:
            rows = await self._db.select(
                _GET_MERCHANT_BUSINESSES,
                {"search": search, "limit": page_size, "offset": offset},
            )
        except Exception as exc:
            raise err_find_all_merchant_businesses.with_internal(exc) from exc
        return [GetMerchantsBusinessInformationRow.from_row(row) for row in rows]

    async def find_active(
        self, search: str, page: int, page_size: int
    ) -> list[GetMerchantsBusinessInformationActiveRow]:
        offset = (page - 1) * page_size
        try:
            rows = await self._db.select(
                _GET_MERCHANT_BUSINESSES_ACTIVE,
                {"search": search, "limit": page_size, "offset": offset},
            )
        except Exception as exc:
            raise err_find_active_merchant_businesses.with_internal(exc) from exc
        return [
            GetMerchantsBusinessInformationActiveRow.from_row(row) for row in rows
        ]

    async def find_trashed(
        self, search: str, page: int, page_size: int
    ) -> list[GetMerchantsBusinessInformationTrashedRow]:
        offset = (page - 1) * page_size
        try:
            rows = await self._db.select(
                _GET_MERCHANT_BUSINESSES_TRASHED,
                {"search": search, "limit": page_size, "offset": offset},
            )
        except Exception as exc:
            raise err_find_trashed_merchant_businesses.with_internal(exc) from exc
        return [
            GetMerchantsBusinessInformationTrashedRow.from_row(row) for row in rows
        ]

    async def find_by_id(
        self, merchant_business_info_id: int
    ) -> GetMerchantBusinessInformationRow:
        try:
            row = await self._db.scalar(
                _GET_MERCHANT_BUSINESS,
                {"merchant_business_info_id": merchant_business_info_id},
            )
        except Exception as exc:
            raise err_merchant_business_internal.with_internal(exc) from exc
        if row is None:
            raise err_merchant_business_not_found
        return GetMerchantBusinessInformationRow.from_row(row)


__all__ = ["MerchantBusinessQueryRepositoryImpl"]

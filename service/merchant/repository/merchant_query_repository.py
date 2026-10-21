"""Merchant read repository. SQL is kept verbatim from the reference, including the `COUNT(*) OVER` window that supplies `total_count` in the same round trip as the page. the `$1::TEXT IS NULL OR...` guard is dropped: binds a plain `string` (never nil), so the branch is always false and only the two `ILIKE` terms matter. A NULL `contact_email` yields NULL from `ILIKE` and therefore does not match, matching. An empty search matches every row."""

from __future__ import annotations

from pkg.database.database import Database
from pkg.database.schema.merchant import (
    GetMerchantByIDRow,
    GetMerchantsActiveRow,
    GetMerchantsRow,
    GetMerchantsTrashedRow,
)
from shared.errors import (
    err_find_active_merchants,
    err_find_all_merchants,
    err_find_trashed_merchants,
    err_merchant_internal,
    err_merchant_not_found,
)

_GET_MERCHANTS = """
SELECT
    merchant_id,
    user_id,
    name,
    description,
    address,
    contact_email,
    contact_phone,
    status,
    created_at,
    updated_at,
    COUNT(*) OVER () AS total_count
FROM merchants
WHERE
    deleted_at IS NULL
    AND (
        name ILIKE '%' || :search || '%'
        OR contact_email ILIKE '%' || :search || '%'
    )
ORDER BY created_at DESC
LIMIT :limit
OFFSET :offset
"""

_GET_MERCHANTS_ACTIVE = """
SELECT
    merchant_id,
    user_id,
    name,
    description,
    address,
    contact_email,
    contact_phone,
    status,
    created_at,
    updated_at,
    deleted_at,
    COUNT(*) OVER () AS total_count
FROM merchants
WHERE
    deleted_at IS NULL
    AND (
        name ILIKE '%' || :search || '%'
        OR contact_email ILIKE '%' || :search || '%'
    )
ORDER BY created_at DESC
LIMIT :limit
OFFSET :offset
"""

_GET_MERCHANTS_TRASHED = """
SELECT
    merchant_id,
    user_id,
    name,
    description,
    address,
    contact_email,
    contact_phone,
    status,
    created_at,
    updated_at,
    deleted_at,
    COUNT(*) OVER () AS total_count
FROM merchants
WHERE
    deleted_at IS NOT NULL
    AND (
        name ILIKE '%' || :search || '%'
        OR contact_email ILIKE '%' || :search || '%'
    )
ORDER BY created_at DESC
LIMIT :limit
OFFSET :offset
"""

_GET_MERCHANT_BY_ID = """
SELECT
    merchant_id,
    user_id,
    name,
    description,
    address,
    contact_email,
    contact_phone,
    status,
    created_at,
    updated_at
FROM merchants
WHERE
    merchant_id = :merchant_id
    AND deleted_at IS NULL
"""


class MerchantQueryRepositoryImpl:
    def __init__(self, db: Database) -> None:
        self._db = db

    async def find_all(
        self, search: str, page: int, page_size: int
    ) -> list[GetMerchantsRow]:
        offset = (page - 1) * page_size
        try:
            rows = await self._db.select(
                _GET_MERCHANTS,
                {"search": search, "limit": page_size, "offset": offset},
            )
        except Exception as exc:
            raise err_find_all_merchants.with_internal(exc) from exc
        return [GetMerchantsRow.from_row(row) for row in rows]

    async def find_active(
        self, search: str, page: int, page_size: int
    ) -> list[GetMerchantsActiveRow]:
        offset = (page - 1) * page_size
        try:
            rows = await self._db.select(
                _GET_MERCHANTS_ACTIVE,
                {"search": search, "limit": page_size, "offset": offset},
            )
        except Exception as exc:
            raise err_find_active_merchants.with_internal(exc) from exc
        return [GetMerchantsActiveRow.from_row(row) for row in rows]

    async def find_trashed(
        self, search: str, page: int, page_size: int
    ) -> list[GetMerchantsTrashedRow]:
        offset = (page - 1) * page_size
        try:
            rows = await self._db.select(
                _GET_MERCHANTS_TRASHED,
                {"search": search, "limit": page_size, "offset": offset},
            )
        except Exception as exc:
            raise err_find_trashed_merchants.with_internal(exc) from exc
        return [GetMerchantsTrashedRow.from_row(row) for row in rows]

    async def find_by_id(self, merchant_id: int) -> GetMerchantByIDRow:
        try:
            row = await self._db.scalar(
                _GET_MERCHANT_BY_ID, {"merchant_id": merchant_id}
            )
        except Exception as exc:
            raise err_merchant_internal.with_internal(exc) from exc
        if row is None:
            raise err_merchant_not_found
        return GetMerchantByIDRow.from_row(row)


__all__ = ["MerchantQueryRepositoryImpl"]

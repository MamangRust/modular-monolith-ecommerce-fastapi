"""merchant_detail read repository. SQL is kept verbatim from the reference, including the `COUNT(*) OVER` window that supplies `total_count` in the same round trip as the page and the `json_agg(json_build_object(...)` that builds `social_media_links`. the `LOWER(m.name) LIKE LOWER(CONCAT('%', $1::text, '%')` guard becomes an `ILIKE` (equivalent); binds a plain `string` (never nil), so no null branch is needed. An empty search matches every row. `find_by_id_trashed` is for completeness but has no caller: the service exposes no trashed single read (the method is dead code, like the one)."""

from __future__ import annotations

from pkg.database.database import Database
from pkg.database.schema.merchant_detail import (
    GetMerchantDetailRow,
    GetMerchantDetailsActiveRow,
    GetMerchantDetailsRow,
    GetMerchantDetailsTrashedRow,
    GetMerchantDetailTrashedRow,
)
from shared.errors import (
    err_find_active_merchant_details,
    err_find_all_merchant_details,
    err_find_by_id_trashed_merchant_detail,
    err_find_trashed_merchant_details,
    err_merchant_detail_internal,
    err_merchant_detail_not_found,
)

_LINKS_AGG = (
    "json_agg(json_build_object("
    "'id', sml.merchant_social_id, "
    "'platform', sml.platform, "
    "'url', sml.url))"
)

_BASE_COLUMNS = """
    md.merchant_detail_id,
    md.merchant_id,
    md.display_name,
    md.cover_image_url,
    md.logo_url,
    md.short_description,
    md.website_url,
    md.created_at,
    md.updated_at
"""

_GET_MERCHANT_DETAILS = f"""
SELECT
{_BASE_COLUMNS},
    m.name AS merchant_name,
    COUNT(*) OVER () AS total_count,
    {_LINKS_AGG} AS social_media_links
FROM
    merchant_details md
    JOIN merchants m ON md.merchant_id = m.merchant_id
    LEFT JOIN merchant_social_media_links sml
        ON sml.merchant_detail_id = md.merchant_detail_id
WHERE
    md.deleted_at IS NULL
    AND m.name ILIKE '%' || :search || '%'
GROUP BY
    md.merchant_detail_id,
    m.merchant_id
LIMIT :limit
OFFSET :offset
"""

_GET_MERCHANT_DETAILS_ACTIVE = f"""
SELECT
{_BASE_COLUMNS},
    md.deleted_at,
    m.name AS merchant_name,
    COUNT(*) OVER () AS total_count,
    {_LINKS_AGG} AS social_media_links
FROM
    merchant_details md
    JOIN merchants m ON md.merchant_id = m.merchant_id
    LEFT JOIN merchant_social_media_links sml
        ON sml.merchant_detail_id = md.merchant_detail_id
WHERE
    md.deleted_at IS NULL
    AND m.deleted_at IS NULL
    AND m.name ILIKE '%' || :search || '%'
GROUP BY
    md.merchant_detail_id,
    m.merchant_id
LIMIT :limit
OFFSET :offset
"""

_GET_MERCHANT_DETAILS_TRASHED = f"""
SELECT
{_BASE_COLUMNS},
    md.deleted_at,
    m.name AS merchant_name,
    COUNT(*) OVER () AS total_count,
    {_LINKS_AGG} AS social_media_links
FROM
    merchant_details md
    JOIN merchants m ON md.merchant_id = m.merchant_id
    LEFT JOIN merchant_social_media_links sml
        ON sml.merchant_detail_id = md.merchant_detail_id
WHERE
    md.deleted_at IS NOT NULL
    AND m.name ILIKE '%' || :search || '%'
GROUP BY
    md.merchant_detail_id,
    m.merchant_id
LIMIT :limit
OFFSET :offset
"""

_GET_MERCHANT_DETAIL = f"""
SELECT
{_BASE_COLUMNS},
    m.name AS merchant_name,
    {_LINKS_AGG} AS social_media_links
FROM
    merchant_details md
    JOIN merchants m ON md.merchant_id = m.merchant_id
    LEFT JOIN merchant_social_media_links sml
        ON sml.merchant_detail_id = md.merchant_detail_id
WHERE
    md.merchant_detail_id = :merchant_detail_id
    AND md.deleted_at IS NULL
GROUP BY
    md.merchant_detail_id,
    m.merchant_id
"""

_GET_MERCHANT_DETAIL_TRASHED = f"""
SELECT
{_BASE_COLUMNS}
FROM merchant_details md
WHERE
    merchant_detail_id = :merchant_detail_id
    AND deleted_at IS NOT NULL
"""


class MerchantDetailQueryRepositoryImpl:
    def __init__(self, db: Database) -> None:
        self._db = db

    async def find_all(
        self, search: str, page: int, page_size: int
    ) -> list[GetMerchantDetailsRow]:
        offset = (page - 1) * page_size
        try:
            rows = await self._db.select(
                _GET_MERCHANT_DETAILS,
                {"search": search, "limit": page_size, "offset": offset},
            )
        except Exception as exc:
            raise err_find_all_merchant_details.with_internal(exc) from exc
        return [GetMerchantDetailsRow.from_row(row) for row in rows]

    async def find_active(
        self, search: str, page: int, page_size: int
    ) -> list[GetMerchantDetailsActiveRow]:
        offset = (page - 1) * page_size
        try:
            rows = await self._db.select(
                _GET_MERCHANT_DETAILS_ACTIVE,
                {"search": search, "limit": page_size, "offset": offset},
            )
        except Exception as exc:
            raise err_find_active_merchant_details.with_internal(exc) from exc
        return [GetMerchantDetailsActiveRow.from_row(row) for row in rows]

    async def find_trashed(
        self, search: str, page: int, page_size: int
    ) -> list[GetMerchantDetailsTrashedRow]:
        offset = (page - 1) * page_size
        try:
            rows = await self._db.select(
                _GET_MERCHANT_DETAILS_TRASHED,
                {"search": search, "limit": page_size, "offset": offset},
            )
        except Exception as exc:
            raise err_find_trashed_merchant_details.with_internal(exc) from exc
        return [GetMerchantDetailsTrashedRow.from_row(row) for row in rows]

    async def find_by_id(self, merchant_detail_id: int) -> GetMerchantDetailRow:
        try:
            row = await self._db.scalar(
                _GET_MERCHANT_DETAIL,
                {"merchant_detail_id": merchant_detail_id},
            )
        except Exception as exc:
            raise err_merchant_detail_internal.with_internal(exc) from exc
        if row is None:
            raise err_merchant_detail_not_found
        return GetMerchantDetailRow.from_row(row)

    async def find_by_id_trashed(
        self, merchant_detail_id: int
    ) -> GetMerchantDetailTrashedRow:
        try:
            row = await self._db.scalar(
                _GET_MERCHANT_DETAIL_TRASHED,
                {"merchant_detail_id": merchant_detail_id},
            )
        except Exception as exc:
            raise err_find_by_id_trashed_merchant_detail.with_internal(exc) from exc
        if row is None:
            raise err_merchant_detail_not_found
        return GetMerchantDetailTrashedRow.from_row(row)


__all__ = ["MerchantDetailQueryRepositoryImpl"]

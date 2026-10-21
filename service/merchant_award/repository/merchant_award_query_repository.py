"""merchant_award read repository. SQL is kept verbatim from the reference, including the `COUNT(*) OVER` window that supplies `total_count` in the same round trip as the page. the `LOWER(m.name) LIKE LOWER(CONCAT('%', $1::text, '%')` guard becomes an `ILIKE` (equivalent); binds a plain `string` (never nil), so no null branch is needed. An empty search matches every row. `find_by_id` maps a missing row to `err_merchant_award_not_found` (404) and any other failure to `err_find_by_id_merchant_award` (500), matching the `pgx.ErrNoRows` branch."""

from __future__ import annotations

from pkg.database.database import Database
from pkg.database.schema.merchant_award import (
    GetMerchantCertificationOrAwardRow,
    GetMerchantCertificationsAndAwardsActiveRow,
    GetMerchantCertificationsAndAwardsRow,
    GetMerchantCertificationsAndAwardsTrashedRow,
)
from shared.errors import (
    err_find_active_merchant_awards,
    err_find_all_merchant_awards,
    err_find_by_id_merchant_award,
    err_find_trashed_merchant_awards,
    err_merchant_award_not_found,
)

_BASE_COLUMNS = """
    mca.merchant_certification_id,
    mca.merchant_id,
    mca.title,
    mca.description,
    mca.issued_by,
    mca.issue_date,
    mca.expiry_date,
    mca.certificate_url,
    mca.created_at,
    mca.updated_at
"""

_GET_MERCHANT_AWARDS = f"""
SELECT
{_BASE_COLUMNS},
    m.name AS merchant_name,
    COUNT(*) OVER () AS total_count
FROM
    merchant_certifications_and_awards mca
    JOIN merchants m ON mca.merchant_id = m.merchant_id
WHERE
    mca.deleted_at IS NULL
    AND m.name ILIKE '%' || :search || '%'
LIMIT :limit
OFFSET :offset
"""

_GET_MERCHANT_AWARDS_ACTIVE = f"""
SELECT
{_BASE_COLUMNS},
    mca.deleted_at,
    m.name AS merchant_name,
    COUNT(*) OVER () AS total_count
FROM
    merchant_certifications_and_awards mca
    JOIN merchants m ON mca.merchant_id = m.merchant_id
WHERE
    mca.deleted_at IS NULL
    AND m.deleted_at IS NULL
    AND m.name ILIKE '%' || :search || '%'
LIMIT :limit
OFFSET :offset
"""

_GET_MERCHANT_AWARDS_TRASHED = f"""
SELECT
{_BASE_COLUMNS},
    mca.deleted_at,
    m.name AS merchant_name,
    COUNT(*) OVER () AS total_count
FROM
    merchant_certifications_and_awards mca
    JOIN merchants m ON mca.merchant_id = m.merchant_id
WHERE
    mca.deleted_at IS NOT NULL
    AND m.name ILIKE '%' || :search || '%'
LIMIT :limit
OFFSET :offset
"""

_GET_MERCHANT_AWARD = f"""
SELECT
{_BASE_COLUMNS}
FROM merchant_certifications_and_awards mca
WHERE
    merchant_certification_id = :merchant_certification_id
    AND deleted_at IS NULL
"""


class MerchantAwardQueryRepositoryImpl:
    def __init__(self, db: Database) -> None:
        self._db = db

    async def find_all(
        self, search: str, page: int, page_size: int
    ) -> list[GetMerchantCertificationsAndAwardsRow]:
        offset = (page - 1) * page_size
        try:
            rows = await self._db.select(
                _GET_MERCHANT_AWARDS,
                {"search": search, "limit": page_size, "offset": offset},
            )
        except Exception as exc:
            raise err_find_all_merchant_awards.with_internal(exc) from exc
        return [GetMerchantCertificationsAndAwardsRow.from_row(row) for row in rows]

    async def find_active(
        self, search: str, page: int, page_size: int
    ) -> list[GetMerchantCertificationsAndAwardsActiveRow]:
        offset = (page - 1) * page_size
        try:
            rows = await self._db.select(
                _GET_MERCHANT_AWARDS_ACTIVE,
                {"search": search, "limit": page_size, "offset": offset},
            )
        except Exception as exc:
            raise err_find_active_merchant_awards.with_internal(exc) from exc
        return [
            GetMerchantCertificationsAndAwardsActiveRow.from_row(row) for row in rows
        ]

    async def find_trashed(
        self, search: str, page: int, page_size: int
    ) -> list[GetMerchantCertificationsAndAwardsTrashedRow]:
        offset = (page - 1) * page_size
        try:
            rows = await self._db.select(
                _GET_MERCHANT_AWARDS_TRASHED,
                {"search": search, "limit": page_size, "offset": offset},
            )
        except Exception as exc:
            raise err_find_trashed_merchant_awards.with_internal(exc) from exc
        return [
            GetMerchantCertificationsAndAwardsTrashedRow.from_row(row) for row in rows
        ]

    async def find_by_id(
        self, merchant_certification_id: int
    ) -> GetMerchantCertificationOrAwardRow:
        try:
            row = await self._db.scalar(
                _GET_MERCHANT_AWARD,
                {"merchant_certification_id": merchant_certification_id},
            )
        except Exception as exc:
            raise err_find_by_id_merchant_award.with_internal(exc) from exc
        if row is None:
            raise err_merchant_award_not_found
        return GetMerchantCertificationOrAwardRow.from_row(row)


__all__ = ["MerchantAwardQueryRepositoryImpl"]

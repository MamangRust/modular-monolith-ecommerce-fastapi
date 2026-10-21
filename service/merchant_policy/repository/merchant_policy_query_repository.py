"""merchant_policy read repository. SQL is kept verbatim from the reference, including the `COUNT(*) OVER` window that supplies `total_count` in the same round trip as the page. the `LOWER(m.name) LIKE LOWER(CONCAT('%', $1::text, '%')` guard becomes an `ILIKE` (equivalent); binds a plain `string` (never nil), so no null branch is needed. An empty search matches every row. `find_by_id` maps a missing row to `err_merchant_policy_not_found` (404) and any other failure to `err_find_merchant_policy_by_id` (500) — note this uses the repository's *dedicated* find-by-id sentinel, unlike merchant_business."""

from __future__ import annotations

from pkg.database.database import Database
from pkg.database.schema.merchant_policy import (
    GetMerchantPoliciesActiveRow,
    GetMerchantPoliciesRow,
    GetMerchantPoliciesTrashedRow,
    GetMerchantPolicyRow,
)
from shared.errors import (
    err_find_active_merchant_policies,
    err_find_all_merchant_policies,
    err_find_merchant_policy_by_id,
    err_find_trashed_merchant_policies,
    err_merchant_policy_not_found,
)

_BASE_COLUMNS = """
    mp.merchant_policy_id,
    mp.merchant_id,
    mp.policy_type,
    mp.title,
    mp.description,
    mp.created_at,
    mp.updated_at
"""

_GET_MERCHANT_POLICIES = f"""
SELECT
{_BASE_COLUMNS},
    m.name AS merchant_name,
    COUNT(*) OVER () AS total_count
FROM
    merchant_policies mp
    JOIN merchants m ON mp.merchant_id = m.merchant_id
WHERE
    mp.deleted_at IS NULL
    AND m.name ILIKE '%' || :search || '%'
LIMIT :limit
OFFSET :offset
"""

_GET_MERCHANT_POLICIES_ACTIVE = f"""
SELECT
{_BASE_COLUMNS},
    mp.deleted_at,
    m.name AS merchant_name,
    COUNT(*) OVER () AS total_count
FROM
    merchant_policies mp
    JOIN merchants m ON mp.merchant_id = m.merchant_id
WHERE
    mp.deleted_at IS NULL
    AND m.deleted_at IS NULL
    AND m.name ILIKE '%' || :search || '%'
LIMIT :limit
OFFSET :offset
"""

_GET_MERCHANT_POLICIES_TRASHED = f"""
SELECT
{_BASE_COLUMNS},
    mp.deleted_at,
    m.name AS merchant_name,
    COUNT(*) OVER () AS total_count
FROM
    merchant_policies mp
    JOIN merchants m ON mp.merchant_id = m.merchant_id
WHERE
    mp.deleted_at IS NOT NULL
    AND m.name ILIKE '%' || :search || '%'
LIMIT :limit
OFFSET :offset
"""

_GET_MERCHANT_POLICY = f"""
SELECT
{_BASE_COLUMNS}
FROM merchant_policies mp
WHERE
    merchant_policy_id = :merchant_policy_id
    AND deleted_at IS NULL
"""


class MerchantPolicyQueryRepositoryImpl:
    def __init__(self, db: Database) -> None:
        self._db = db

    async def find_all(
        self, search: str, page: int, page_size: int
    ) -> list[GetMerchantPoliciesRow]:
        offset = (page - 1) * page_size
        try:
            rows = await self._db.select(
                _GET_MERCHANT_POLICIES,
                {"search": search, "limit": page_size, "offset": offset},
            )
        except Exception as exc:
            raise err_find_all_merchant_policies.with_internal(exc) from exc
        return [GetMerchantPoliciesRow.from_row(row) for row in rows]

    async def find_active(
        self, search: str, page: int, page_size: int
    ) -> list[GetMerchantPoliciesActiveRow]:
        offset = (page - 1) * page_size
        try:
            rows = await self._db.select(
                _GET_MERCHANT_POLICIES_ACTIVE,
                {"search": search, "limit": page_size, "offset": offset},
            )
        except Exception as exc:
            raise err_find_active_merchant_policies.with_internal(exc) from exc
        return [GetMerchantPoliciesActiveRow.from_row(row) for row in rows]

    async def find_trashed(
        self, search: str, page: int, page_size: int
    ) -> list[GetMerchantPoliciesTrashedRow]:
        offset = (page - 1) * page_size
        try:
            rows = await self._db.select(
                _GET_MERCHANT_POLICIES_TRASHED,
                {"search": search, "limit": page_size, "offset": offset},
            )
        except Exception as exc:
            raise err_find_trashed_merchant_policies.with_internal(exc) from exc
        return [GetMerchantPoliciesTrashedRow.from_row(row) for row in rows]

    async def find_by_id(self, merchant_policy_id: int) -> GetMerchantPolicyRow:
        try:
            row = await self._db.scalar(
                _GET_MERCHANT_POLICY,
                {"merchant_policy_id": merchant_policy_id},
            )
        except Exception as exc:
            raise err_find_merchant_policy_by_id.with_internal(exc) from exc
        if row is None:
            raise err_merchant_policy_not_found
        return GetMerchantPolicyRow.from_row(row)


__all__ = ["MerchantPolicyQueryRepositoryImpl"]

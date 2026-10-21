"""merchant_policy write repository. `create`/`update`/`trash`/`restore` map a missing row (`None` from the `RETURNING` projection) to `err_merchant_policy_not_found`; every other failure maps to the matching sentinel. Every business column is `NOT NULL` in the DDL (`policy_type`, `title`, `description`), so unlike merchant_business there are no nullable `stringPtr` / `int32Ptr` branches to port — the request values bind directly."""

from __future__ import annotations

from typing import Any

from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncConnection

from pkg.database.database import Database
from pkg.database.schema.merchant_policy import (
    CreateMerchantPolicyRow,
    MerchantPolicy,
    UpdateMerchantPolicyRow,
)
from shared.domain.requests.merchant_policy import (
    CreateMerchantPolicyRequest,
    UpdateMerchantPolicyRequest,
)
from shared.errors import (
    AppError,
    err_create_merchant_policy,
    err_delete_all_merchant_policies_permanent,
    err_delete_merchant_policy_permanent,
    err_merchant_policy_not_found,
    err_restore_all_merchant_policies,
    err_restore_merchant_policy,
    err_trashed_merchant_policy,
    err_update_merchant_policy,
)

_RETURNING_COLUMNS = """
    merchant_policy_id,
    merchant_id,
    policy_type,
    title,
    description,
    created_at,
    updated_at
"""

_CREATE_MERCHANT_POLICY = f"""
INSERT INTO merchant_policies (
    merchant_id, policy_type, title, description
)
VALUES (
    :merchant_id, :policy_type, :title, :description
)
RETURNING
{_RETURNING_COLUMNS}
"""

_UPDATE_MERCHANT_POLICY = f"""
UPDATE merchant_policies
SET
    policy_type = :policy_type,
    title = :title,
    description = :description,
    updated_at = CURRENT_TIMESTAMP
WHERE
    merchant_policy_id = :merchant_policy_id
    AND deleted_at IS NULL
RETURNING
{_RETURNING_COLUMNS}
"""

_TRASH_MERCHANT_POLICY = f"""
UPDATE merchant_policies
SET deleted_at = CURRENT_TIMESTAMP
WHERE
    merchant_policy_id = :merchant_policy_id
    AND deleted_at IS NULL
RETURNING
{_RETURNING_COLUMNS},
    deleted_at
"""

_RESTORE_MERCHANT_POLICY = f"""
UPDATE merchant_policies
SET deleted_at = NULL
WHERE
    merchant_policy_id = :merchant_policy_id
    AND deleted_at IS NOT NULL
RETURNING
{_RETURNING_COLUMNS},
    deleted_at
"""

_DELETE_MERCHANT_POLICY_PERMANENTLY = """
DELETE FROM merchant_policies
WHERE
    merchant_policy_id = :merchant_policy_id
    AND deleted_at IS NOT NULL
"""

_RESTORE_ALL_MERCHANT_POLICIES = (
    "UPDATE merchant_policies SET deleted_at = NULL WHERE deleted_at IS NOT NULL"
)

_DELETE_ALL_PERMANENT_MERCHANT_POLICIES = (
    "DELETE FROM merchant_policies WHERE deleted_at IS NOT NULL"
)


class MerchantPolicyCommandRepositoryImpl:
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
        self, request: CreateMerchantPolicyRequest
    ) -> CreateMerchantPolicyRow:
        params = {
            "merchant_id": request.merchant_id,
            "policy_type": request.policy_type,
            "title": request.title,
            "description": request.description,
        }
        try:
            row = await self._returning(_CREATE_MERCHANT_POLICY, params)
        except AppError:
            raise
        except Exception as exc:
            raise err_create_merchant_policy.with_internal(exc) from exc
        if row is None:
            raise err_merchant_policy_not_found
        return CreateMerchantPolicyRow.from_row(row)

    async def update(
        self, request: UpdateMerchantPolicyRequest
    ) -> UpdateMerchantPolicyRow:
        params = {
            "merchant_policy_id": request.merchant_policy_id,
            "policy_type": request.policy_type,
            "title": request.title,
            "description": request.description,
        }
        try:
            row = await self._returning(_UPDATE_MERCHANT_POLICY, params)
        except AppError:
            raise
        except Exception as exc:
            raise err_update_merchant_policy.with_internal(exc) from exc
        if row is None:
            raise err_merchant_policy_not_found
        return UpdateMerchantPolicyRow.from_row(row)

    async def trash(self, merchant_policy_id: int) -> MerchantPolicy:
        try:
            row = await self._returning(
                _TRASH_MERCHANT_POLICY,
                {"merchant_policy_id": merchant_policy_id},
            )
        except AppError:
            raise
        except Exception as exc:
            raise err_trashed_merchant_policy.with_internal(exc) from exc
        if row is None:
            raise err_merchant_policy_not_found
        return MerchantPolicy.from_row(row)

    async def restore(self, merchant_policy_id: int) -> MerchantPolicy:
        try:
            row = await self._returning(
                _RESTORE_MERCHANT_POLICY,
                {"merchant_policy_id": merchant_policy_id},
            )
        except AppError:
            raise
        except Exception as exc:
            raise err_restore_merchant_policy.with_internal(exc) from exc
        if row is None:
            raise err_merchant_policy_not_found
        return MerchantPolicy.from_row(row)

    async def delete_permanent(self, merchant_policy_id: int) -> bool:
        try:
            await self._db.execute(
                _DELETE_MERCHANT_POLICY_PERMANENTLY,
                {"merchant_policy_id": merchant_policy_id},
            )
        except AppError:
            raise
        except Exception as exc:
            raise err_delete_merchant_policy_permanent.with_internal(exc) from exc
        return True

    async def restore_all(self) -> bool:
        try:
            await self._db.execute(_RESTORE_ALL_MERCHANT_POLICIES)
        except AppError:
            raise
        except Exception as exc:
            raise err_restore_all_merchant_policies.with_internal(exc) from exc
        return True

    async def delete_all(self) -> bool:
        try:
            await self._db.execute(_DELETE_ALL_PERMANENT_MERCHANT_POLICIES)
        except AppError:
            raise
        except Exception as exc:
            raise err_delete_all_merchant_policies_permanent.with_internal(
                exc
            ) from exc
        return True


__all__ = ["MerchantPolicyCommandRepositoryImpl"]

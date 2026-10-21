"""merchant_award write repository. `create`/`update`/`trash`/`restore` map a missing row (`None` from the `RETURNING` projection) to `err_merchant_award_not_found`; every other failure maps to the matching sentinel. Nullable columns follow `stringPtr` / `parseDateToPgDate`: an empty string becomes NULL (not `''`), and an empty/unparseable date becomes NULL. `stringPtr` returns nil for `""`, so `description`/`issued_by`/`certificate_url` are stored as NULL when empty (validation requires the first two non-empty, so only `certificate_url` can be empty in practice)."""

from __future__ import annotations

from datetime import date
from typing import Any

from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncConnection

from pkg.database.database import Database
from pkg.database.schema.merchant_award import (
    CreateMerchantCertificationOrAwardRow,
    MerchantCertificationsAndAward,
    UpdateMerchantCertificationOrAwardRow,
)
from shared.domain.requests.merchant_award import (
    CreateMerchantCertificationOrAwardRequest,
    UpdateMerchantCertificationOrAwardRequest,
)
from shared.errors import (
    AppError,
    err_create_merchant_award,
    err_delete_all_merchant_awards_permanent,
    err_delete_merchant_award_permanent,
    err_merchant_award_not_found,
    err_restore_all_merchant_awards,
    err_restore_merchant_award,
    err_trashed_merchant_award,
    err_update_merchant_award,
)

_RETURNING_COLUMNS = """
    merchant_certification_id,
    merchant_id,
    title,
    description,
    issued_by,
    issue_date,
    expiry_date,
    certificate_url,
    created_at,
    updated_at
"""

_CREATE_MERCHANT_AWARD = f"""
INSERT INTO merchant_certifications_and_awards (
    merchant_id, title, description, issued_by,
    issue_date, expiry_date, certificate_url
)
VALUES (
    :merchant_id, :title, :description, :issued_by,
    :issue_date, :expiry_date, :certificate_url
)
RETURNING
{_RETURNING_COLUMNS}
"""

_UPDATE_MERCHANT_AWARD = f"""
UPDATE merchant_certifications_and_awards
SET
    title = :title,
    description = :description,
    issued_by = :issued_by,
    issue_date = :issue_date,
    expiry_date = :expiry_date,
    certificate_url = :certificate_url,
    updated_at = CURRENT_TIMESTAMP
WHERE
    merchant_certification_id = :merchant_certification_id
    AND deleted_at IS NULL
RETURNING
{_RETURNING_COLUMNS}
"""

_TRASH_MERCHANT_AWARD = f"""
UPDATE merchant_certifications_and_awards
SET deleted_at = CURRENT_TIMESTAMP
WHERE
    merchant_certification_id = :merchant_certification_id
    AND deleted_at IS NULL
RETURNING
{_RETURNING_COLUMNS},
    deleted_at
"""

_RESTORE_MERCHANT_AWARD = f"""
UPDATE merchant_certifications_and_awards
SET deleted_at = NULL
WHERE
    merchant_certification_id = :merchant_certification_id
    AND deleted_at IS NOT NULL
RETURNING
{_RETURNING_COLUMNS},
    deleted_at
"""

_DELETE_MERCHANT_AWARD_PERMANENTLY = """
DELETE FROM merchant_certifications_and_awards
WHERE
    merchant_certification_id = :merchant_certification_id
    AND deleted_at IS NOT NULL
"""

_RESTORE_ALL_MERCHANT_AWARDS = (
    "UPDATE merchant_certifications_and_awards SET deleted_at = NULL "
    "WHERE deleted_at IS NOT NULL"
)

_DELETE_ALL_PERMANENT_MERCHANT_AWARDS = (
    "DELETE FROM merchant_certifications_and_awards WHERE deleted_at IS NOT NULL"
)


def _nullable(value: str) -> str | None:
    """empty -> NULL."""
    return value if value != "" else None


def _parse_date(value: str) -> date | None:
    """empty/unparseable -> NULL."""
    if value == "":
        return None
    try:
        return date.fromisoformat(value)
    except ValueError:
        return None


class MerchantAwardCommandRepositoryImpl:
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
        self, request: CreateMerchantCertificationOrAwardRequest
    ) -> CreateMerchantCertificationOrAwardRow:
        params = {
            "merchant_id": request.merchant_id,
            "title": request.title,
            "description": _nullable(request.description),
            "issued_by": _nullable(request.issued_by),
            "issue_date": _parse_date(request.issue_date),
            "expiry_date": _parse_date(request.expiry_date),
            "certificate_url": _nullable(request.certificate_url),
        }
        try:
            row = await self._returning(_CREATE_MERCHANT_AWARD, params)
        except AppError:
            raise
        except Exception as exc:
            raise err_create_merchant_award.with_internal(exc) from exc
        if row is None:
            raise err_merchant_award_not_found
        return CreateMerchantCertificationOrAwardRow.from_row(row)

    async def update(
        self, request: UpdateMerchantCertificationOrAwardRequest
    ) -> UpdateMerchantCertificationOrAwardRow:
        params = {
            "merchant_certification_id": request.merchant_certification_id,
            "title": request.title,
            "description": _nullable(request.description),
            "issued_by": _nullable(request.issued_by),
            "issue_date": _parse_date(request.issue_date),
            "expiry_date": _parse_date(request.expiry_date),
            "certificate_url": _nullable(request.certificate_url),
        }
        try:
            row = await self._returning(_UPDATE_MERCHANT_AWARD, params)
        except AppError:
            raise
        except Exception as exc:
            raise err_update_merchant_award.with_internal(exc) from exc
        if row is None:
            raise err_merchant_award_not_found
        return UpdateMerchantCertificationOrAwardRow.from_row(row)

    async def trash(
        self, merchant_certification_id: int
    ) -> MerchantCertificationsAndAward:
        try:
            row = await self._returning(
                _TRASH_MERCHANT_AWARD,
                {"merchant_certification_id": merchant_certification_id},
            )
        except AppError:
            raise
        except Exception as exc:
            raise err_trashed_merchant_award.with_internal(exc) from exc
        if row is None:
            raise err_merchant_award_not_found
        return MerchantCertificationsAndAward.from_row(row)

    async def restore(
        self, merchant_certification_id: int
    ) -> MerchantCertificationsAndAward:
        try:
            row = await self._returning(
                _RESTORE_MERCHANT_AWARD,
                {"merchant_certification_id": merchant_certification_id},
            )
        except AppError:
            raise
        except Exception as exc:
            raise err_restore_merchant_award.with_internal(exc) from exc
        if row is None:
            raise err_merchant_award_not_found
        return MerchantCertificationsAndAward.from_row(row)

    async def delete_permanent(self, merchant_certification_id: int) -> bool:
        try:
            await self._db.execute(
                _DELETE_MERCHANT_AWARD_PERMANENTLY,
                {"merchant_certification_id": merchant_certification_id},
            )
        except AppError:
            raise
        except Exception as exc:
            raise err_delete_merchant_award_permanent.with_internal(exc) from exc
        return True

    async def restore_all(self) -> bool:
        try:
            await self._db.execute(_RESTORE_ALL_MERCHANT_AWARDS)
        except AppError:
            raise
        except Exception as exc:
            raise err_restore_all_merchant_awards.with_internal(exc) from exc
        return True

    async def delete_all(self) -> bool:
        try:
            await self._db.execute(_DELETE_ALL_PERMANENT_MERCHANT_AWARDS)
        except AppError:
            raise
        except Exception as exc:
            raise err_delete_all_merchant_awards_permanent.with_internal(exc) from exc
        return True


__all__ = ["MerchantAwardCommandRepositoryImpl"]

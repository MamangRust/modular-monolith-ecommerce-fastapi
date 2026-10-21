"""Banner write repository. `create`/`update` parse the request's date/time strings into `date`/`time` values, mapping a parse failure to the matching error. Soft delete uses `deleted_at`; `delete_permanent` and the bulk operations are hard deletes., `delete_permanent` and the bulk restore/delete ignore affected rows, so operating on a missing banner still reports success (see the)."""

from __future__ import annotations

from datetime import date, time

from pkg.database.database import Database
from pkg.database.errors import NoRowsError
from pkg.database.schema.banner import (
    Banner,
    CreateBannerRow,
    UpdateBannerRow,
)
from shared.domain.requests.banner import CreateBannerRequest, UpdateBannerRequest
from shared.errors import (
    AppError,
    err_banner_end_date,
    err_banner_end_time,
    err_banner_start_date,
    err_banner_start_time,
    err_constraint_or_failed,
    err_no_rows_or_failed,
)

_CREATE_BANNER = """
INSERT INTO banners (name, start_date, end_date, start_time, end_time, is_active)
VALUES (:name, :start_date, :end_date, :start_time, :end_time, :is_active)
RETURNING
    banner_id, name, start_date, end_date, start_time, end_time, is_active,
    created_at, updated_at
"""

_UPDATE_BANNER = """
UPDATE banners
SET
    name = :name,
    start_date = :start_date,
    end_date = :end_date,
    start_time = :start_time,
    end_time = :end_time,
    is_active = :is_active,
    updated_at = CURRENT_TIMESTAMP
WHERE
    banner_id = :banner_id
    AND deleted_at IS NULL
RETURNING
    banner_id, name, start_date, end_date, start_time, end_time, is_active,
    created_at, updated_at
"""

_TRASH_BANNER = """
UPDATE banners
SET deleted_at = CURRENT_TIMESTAMP
WHERE
    banner_id = :banner_id
    AND deleted_at IS NULL
RETURNING
    banner_id, name, start_date, end_date, start_time, end_time, is_active,
    created_at, updated_at, deleted_at
"""

_RESTORE_BANNER = """
UPDATE banners
SET deleted_at = NULL
WHERE
    banner_id = :banner_id
    AND deleted_at IS NOT NULL
RETURNING
    banner_id, name, start_date, end_date, start_time, end_time, is_active,
    created_at, updated_at, deleted_at
"""

_DELETE_BANNER_PERMANENT = """
DELETE FROM banners
WHERE
    banner_id = :banner_id
    AND deleted_at IS NOT NULL
"""

_RESTORE_ALL_BANNERS = "UPDATE banners SET deleted_at = NULL WHERE deleted_at IS NOT NULL"

_DELETE_ALL_PERMANENT_BANNERS = "DELETE FROM banners WHERE deleted_at IS NOT NULL"


def _parse_date(value: str, error: AppError) -> date:
    try:
        return date.fromisoformat(value)
    except ValueError as exc:
        raise error.with_internal(exc) from exc


def _parse_time(value: str, error: AppError) -> time:
    try:
        return time.fromisoformat(value)
    except ValueError as exc:
        raise error.with_internal(exc) from exc


class BannerCommandRepositoryImpl:
    def __init__(self, db: Database) -> None:
        self._db = db

    async def create(self, request: CreateBannerRequest) -> CreateBannerRow:
        params = {
            "name": request.name,
            "start_date": _parse_date(request.start_date, err_banner_start_date),
            "end_date": _parse_date(request.end_date, err_banner_end_date),
            "start_time": _parse_time(request.start_time, err_banner_start_time),
            "end_time": _parse_time(request.end_time, err_banner_end_time),
            "is_active": request.is_active,
        }
        try:
            row = await self._db.execute(_CREATE_BANNER, params)
        except AppError:
            raise
        except Exception as exc:
            raise err_constraint_or_failed(exc, "Banner", "create banner") from exc
        if row is None:
            raise err_no_rows_or_failed(NoRowsError(), "Banner", "create banner")
        return CreateBannerRow.from_row(row)

    async def update(self, request: UpdateBannerRequest) -> UpdateBannerRow:
        if request.banner_id is None:
            raise err_no_rows_or_failed(NoRowsError(), "Banner", "update banner")
        params = {
            "banner_id": request.banner_id,
            "name": request.name,
            "start_date": _parse_date(request.start_date, err_banner_start_date),
            "end_date": _parse_date(request.end_date, err_banner_end_date),
            "start_time": _parse_time(request.start_time, err_banner_start_time),
            "end_time": _parse_time(request.end_time, err_banner_end_time),
            "is_active": request.is_active,
        }
        try:
            row = await self._db.execute(_UPDATE_BANNER, params)
        except AppError:
            raise
        except Exception as exc:
            raise err_constraint_or_failed(exc, "Banner", "update banner") from exc
        if row is None:
            raise err_no_rows_or_failed(NoRowsError(), "Banner", "update banner")
        return UpdateBannerRow.from_row(row)

    async def trash(self, banner_id: int) -> Banner:
        row = await self._db.execute(_TRASH_BANNER, {"banner_id": banner_id})
        if row is None:
            raise err_no_rows_or_failed(NoRowsError(), "Banner", "trash banner")
        return Banner.from_row(row)

    async def restore(self, banner_id: int) -> Banner:
        row = await self._db.execute(_RESTORE_BANNER, {"banner_id": banner_id})
        if row is None:
            raise err_no_rows_or_failed(NoRowsError(), "Banner", "restore banner")
        return Banner.from_row(row)

    async def delete_permanent(self, banner_id: int) -> None:
        # ignores RowsAffected here; see module docstring.
        await self._db.execute(_DELETE_BANNER_PERMANENT, {"banner_id": banner_id})

    async def restore_all(self) -> None:
        await self._db.execute(_RESTORE_ALL_BANNERS)

    async def delete_all_permanent(self) -> None:
        await self._db.execute(_DELETE_ALL_PERMANENT_BANNERS)


__all__ = ["BannerCommandRepositoryImpl"]

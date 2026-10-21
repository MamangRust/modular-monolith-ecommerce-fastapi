"""Review detail write repository. `create`/`update` parse the request's fields into the SQL params and map a failure to the matching error. Soft delete uses `deleted_at`; `delete_permanent` and the bulk operations are hard deletes., `delete_permanent` and the bulk restore/delete ignore affected rows, so operating on a missing review detail still reports success. `caption` is nullable and passed through unchanged (a None caption becomes a SQL NULL, matching the `convert.StringPtr`)."""

from __future__ import annotations

from pkg.database.database import Database
from pkg.database.schema.review_detail import (
    CreateReviewDetailRow,
    ReviewDetail,
    UpdateReviewDetailRow,
)
from shared.domain.requests.review_detail import (
    CreateReviewDetailRequest,
    UpdateReviewDetailRequest,
)
from shared.errors import (
    AppError,
    err_create_review_detail,
    err_delete_all_permanent_review_details,
    err_delete_permanent_review_detail,
    err_restore_all_review_details,
    err_restore_review_detail,
    err_review_detail_not_found,
    err_trash_review_detail,
    err_update_review_detail,
)

_CREATE_REVIEW_DETAIL = """
INSERT INTO review_details (review_id, type, url, caption)
VALUES (:review_id, :type, :url, :caption)
RETURNING
    review_detail_id, review_id, type, url, caption, created_at, updated_at
"""

_UPDATE_REVIEW_DETAIL = """
UPDATE review_details
SET
    type = :type,
    url = :url,
    caption = :caption
WHERE
    review_detail_id = :review_detail_id
    AND deleted_at IS NULL
RETURNING
    review_detail_id, review_id, type, url, caption, created_at, updated_at
"""

_TRASH_REVIEW_DETAIL = """
UPDATE review_details
SET
    deleted_at = CURRENT_TIMESTAMP
WHERE
    review_detail_id = :review_detail_id
    AND deleted_at IS NULL
RETURNING
    review_detail_id, review_id, type, url, caption,
    created_at, updated_at, deleted_at
"""

_RESTORE_REVIEW_DETAIL = """
UPDATE review_details
SET
    deleted_at = NULL
WHERE
    review_detail_id = :review_detail_id
    AND deleted_at IS NOT NULL
RETURNING
    review_detail_id, review_id, type, url, caption,
    created_at, updated_at, deleted_at
"""

_DELETE_REVIEW_DETAIL_PERMANENT = """
DELETE FROM review_details
WHERE review_detail_id = :review_detail_id AND deleted_at IS NOT NULL
"""

_RESTORE_ALL_REVIEW_DETAILS = (
    "UPDATE review_details SET deleted_at = NULL WHERE deleted_at IS NOT NULL"
)

_DELETE_ALL_PERMANENT_REVIEW_DETAILS = (
    "DELETE FROM review_details WHERE deleted_at IS NOT NULL"
)


class ReviewDetailCommandRepositoryImpl:
    def __init__(self, db: Database) -> None:
        self._db = db

    async def create(self, request: CreateReviewDetailRequest) -> CreateReviewDetailRow:
        params = {
            "review_id": request.review_id,
            "type": request.type,
            "url": request.url,
            "caption": request.caption,
        }
        try:
            row = await self._db.execute(_CREATE_REVIEW_DETAIL, params)
        except AppError:
            raise
        except Exception as exc:
            raise err_create_review_detail.with_internal(exc) from exc
        if row is None:
            raise err_create_review_detail
        return CreateReviewDetailRow.from_row(row)

    async def update(self, request: UpdateReviewDetailRequest) -> UpdateReviewDetailRow:
        if request.review_detail_id is None:
            raise err_review_detail_not_found
        params = {
            "review_detail_id": request.review_detail_id,
            "type": request.type,
            "url": request.url,
            "caption": request.caption,
        }
        try:
            row = await self._db.execute(_UPDATE_REVIEW_DETAIL, params)
        except AppError:
            raise
        except Exception as exc:
            raise err_update_review_detail.with_internal(exc) from exc
        if row is None:
            raise err_review_detail_not_found
        return UpdateReviewDetailRow.from_row(row)

    async def trash(self, review_detail_id: int) -> ReviewDetail:
        try:
            row = await self._db.execute(
                _TRASH_REVIEW_DETAIL, {"review_detail_id": review_detail_id}
            )
        except AppError:
            raise
        except Exception as exc:
            raise err_trash_review_detail.with_internal(exc) from exc
        if row is None:
            raise err_review_detail_not_found
        return ReviewDetail.from_row(row)

    async def restore(self, review_detail_id: int) -> ReviewDetail:
        try:
            row = await self._db.execute(
                _RESTORE_REVIEW_DETAIL, {"review_detail_id": review_detail_id}
            )
        except AppError:
            raise
        except Exception as exc:
            raise err_restore_review_detail.with_internal(exc) from exc
        if row is None:
            raise err_review_detail_not_found
        return ReviewDetail.from_row(row)

    async def delete_permanent(self, review_detail_id: int) -> bool:
        # ignores RowsAffected here; see module docstring.
        try:
            await self._db.execute(
                _DELETE_REVIEW_DETAIL_PERMANENT, {"review_detail_id": review_detail_id}
            )
        except AppError:
            raise
        except Exception as exc:
            raise err_delete_permanent_review_detail.with_internal(exc) from exc
        return True

    async def restore_all(self) -> bool:
        try:
            await self._db.execute(_RESTORE_ALL_REVIEW_DETAILS)
        except AppError:
            raise
        except Exception as exc:
            raise err_restore_all_review_details.with_internal(exc) from exc
        return True

    async def delete_all_permanent(self) -> bool:
        try:
            await self._db.execute(_DELETE_ALL_PERMANENT_REVIEW_DETAILS)
        except AppError:
            raise
        except Exception as exc:
            raise err_delete_all_permanent_review_details.with_internal(exc) from exc
        return True


__all__ = ["ReviewDetailCommandRepositoryImpl"]

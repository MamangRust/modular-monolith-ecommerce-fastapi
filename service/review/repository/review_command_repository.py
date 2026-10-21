from __future__ import annotations

from pkg.database.database import Database
from pkg.database.schema.review import (
    CreateReviewRow,
    Review,
    UpdateReviewRow,
)
from shared.domain.requests.review import CreateReviewRecord, UpdateReviewRequest
from shared.errors import (
    err_create_review,
    err_delete_all_permanent_review,
    err_delete_review_permanent,
    err_restore_all_reviews,
    err_restore_review,
    err_review_not_found,
    err_trash_review,
    err_update_review,
)

_CREATE_REVIEW = """
INSERT INTO reviews (
    user_id,
    product_id,
    name,
    comment,
    rating
)
VALUES (
    :user_id,
    :product_id,
    :name,
    :comment,
    :rating
)
RETURNING
    review_id,
    user_id,
    product_id,
    name,
    comment,
    rating,
    created_at,
    updated_at
"""

_UPDATE_REVIEW = """
UPDATE reviews
SET
    name = :name,
    comment = :comment,
    rating = :rating,
    updated_at = CURRENT_TIMESTAMP
WHERE
    review_id = :review_id
    AND deleted_at IS NULL
RETURNING
    review_id,
    user_id,
    product_id,
    name,
    comment,
    rating,
    created_at,
    updated_at
"""

_TRASH_REVIEW = """
UPDATE reviews
SET
    deleted_at = CURRENT_TIMESTAMP
WHERE
    review_id = :review_id
    AND deleted_at IS NULL
RETURNING
    review_id,
    user_id,
    product_id,
    name,
    comment,
    rating,
    created_at,
    updated_at,
    deleted_at
"""

_RESTORE_REVIEW = """
UPDATE reviews
SET
    deleted_at = NULL
WHERE
    review_id = :review_id
    AND deleted_at IS NOT NULL
RETURNING
    review_id,
    user_id,
    product_id,
    name,
    comment,
    rating,
    created_at,
    updated_at,
    deleted_at
"""

_DELETE_REVIEW_PERMANENTLY = """
DELETE FROM reviews WHERE review_id = :review_id AND deleted_at IS NOT NULL
"""

_RESTORE_ALL_REVIEWS = """
UPDATE reviews SET deleted_at = NULL WHERE deleted_at IS NOT NULL
"""

_DELETE_ALL_PERMANENT_REVIEWS = """
DELETE FROM reviews WHERE deleted_at IS NOT NULL
"""


class ReviewCommandRepositoryImpl:
    def __init__(self, db: Database) -> None:
        self._db = db

    async def create(self, request: CreateReviewRecord) -> CreateReviewRow:
        params = {
            "user_id": request.user_id,
            "product_id": request.product_id,
            "name": request.name,
            "comment": request.comment,
            "rating": request.rating,
        }
        try:
            row = await self._db.execute(_CREATE_REVIEW, params)
        except Exception as exc:
            raise err_create_review.with_internal(exc) from exc
        if row is None:
            raise err_review_not_found
        return CreateReviewRow.from_row(row)

    async def update(self, request: UpdateReviewRequest) -> UpdateReviewRow:
        params = {
            "review_id": request.review_id,
            "name": request.name,
            "comment": request.comment,
            "rating": request.rating,
        }
        try:
            row = await self._db.execute(_UPDATE_REVIEW, params)
        except Exception as exc:
            raise err_update_review.with_internal(exc) from exc
        if row is None:
            raise err_review_not_found
        return UpdateReviewRow.from_row(row)

    async def trash(self, review_id: int) -> Review:
        try:
            row = await self._db.execute(_TRASH_REVIEW, {"review_id": review_id})
        except Exception as exc:
            raise err_trash_review.with_internal(exc) from exc
        if row is None:
            raise err_review_not_found
        return Review.from_row(row)

    async def restore(self, review_id: int) -> Review:
        try:
            row = await self._db.execute(_RESTORE_REVIEW, {"review_id": review_id})
        except Exception as exc:
            raise err_restore_review.with_internal(exc) from exc
        if row is None:
            raise err_review_not_found
        return Review.from_row(row)

    async def delete_permanent(self, review_id: int) -> bool:
        try:
            await self._db.execute(_DELETE_REVIEW_PERMANENTLY, {"review_id": review_id})
        except Exception as exc:
            raise err_delete_review_permanent.with_internal(exc) from exc
        return True

    async def restore_all(self) -> bool:
        try:
            await self._db.execute(_RESTORE_ALL_REVIEWS)
        except Exception as exc:
            raise err_restore_all_reviews.with_internal(exc) from exc
        return True

    async def delete_all(self) -> bool:
        try:
            await self._db.execute(_DELETE_ALL_PERMANENT_REVIEWS)
        except Exception as exc:
            raise err_delete_all_permanent_review.with_internal(exc) from exc
        return True


__all__ = ["ReviewCommandRepositoryImpl"]

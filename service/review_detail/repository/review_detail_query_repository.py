"""Review detail read repository. SQL is kept verbatim from the reference, including the `COUNT(*) OVER` window that supplies `total_count` in the same round trip as the page. Unlike banner/slider, review_detail's `FindAll` does **not** filter `deleted_at` — it returns every row (active + trashed), matching the `getReviewDetails` SQL. `FindActive`/`FindTrashed` apply the deleted_at filter. `FindById` returns only live rows; `FindByIdTrashed` only trashed rows. The bind is always a string, avoiding the asyncpg `:search IS NULL` ambiguity."""

from __future__ import annotations

from pkg.database.database import Database
from pkg.database.schema.review_detail import (
    GetReviewDetailByIDRow,
    GetReviewDetailsActiveRow,
    GetReviewDetailsRow,
    ReviewDetail,
)
from shared.errors import (
    err_find_active_review_details,
    err_find_all_review_details,
    err_find_review_detail_by_id,
    err_find_review_detail_by_id_trashed,
    err_find_trashed_review_details,
)

_GET_REVIEW_DETAILS = """
SELECT
    review_detail_id,
    review_id,
    type,
    url,
    caption,
    created_at,
    updated_at,
    COUNT(*) OVER () AS total_count
FROM review_details
WHERE
    COALESCE(caption, '') ILIKE '%' || :search || '%'
ORDER BY created_at DESC
LIMIT :limit
OFFSET :offset
"""

_GET_REVIEW_DETAILS_ACTIVE = """
SELECT
    review_detail_id,
    review_id,
    type,
    url,
    caption,
    created_at,
    updated_at,
    deleted_at,
    COUNT(*) OVER () AS total_count
FROM review_details
WHERE
    deleted_at IS NULL
    AND COALESCE(caption, '') ILIKE '%' || :search || '%'
ORDER BY created_at DESC
LIMIT :limit
OFFSET :offset
"""

_GET_REVIEW_DETAILS_TRASHED = """
SELECT
    review_detail_id,
    review_id,
    type,
    url,
    caption,
    created_at,
    updated_at,
    deleted_at,
    COUNT(*) OVER () AS total_count
FROM review_details
WHERE
    deleted_at IS NOT NULL
    AND COALESCE(caption, '') ILIKE '%' || :search || '%'
ORDER BY created_at DESC
LIMIT :limit
OFFSET :offset
"""

_GET_REVIEW_DETAIL = """
SELECT
    review_detail_id,
    review_id,
    type,
    url,
    caption,
    created_at,
    updated_at
FROM review_details
WHERE
    review_detail_id = :review_detail_id
    AND deleted_at IS NULL
"""

_GET_REVIEW_DETAIL_TRASHED = """
SELECT
    review_detail_id,
    review_id,
    type,
    url,
    caption,
    created_at,
    updated_at,
    deleted_at
FROM review_details
WHERE
    review_detail_id = :review_detail_id
    AND deleted_at IS NOT NULL
"""


class ReviewDetailQueryRepositoryImpl:
    def __init__(self, db: Database) -> None:
        self._db = db

    async def find_all(
        self, search: str, page: int, page_size: int
    ) -> list[GetReviewDetailsRow]:
        offset = (page - 1) * page_size
        try:
            rows = await self._db.select(
                _GET_REVIEW_DETAILS,
                {"search": search, "limit": page_size, "offset": offset},
            )
        except Exception as exc:
            raise err_find_all_review_details.with_internal(exc) from exc
        return [GetReviewDetailsRow.from_row(row) for row in rows]

    async def find_active(
        self, search: str, page: int, page_size: int
    ) -> list[GetReviewDetailsActiveRow]:
        offset = (page - 1) * page_size
        try:
            rows = await self._db.select(
                _GET_REVIEW_DETAILS_ACTIVE,
                {"search": search, "limit": page_size, "offset": offset},
            )
        except Exception as exc:
            raise err_find_active_review_details.with_internal(exc) from exc
        return [GetReviewDetailsActiveRow.from_row(row) for row in rows]

    async def find_trashed(
        self, search: str, page: int, page_size: int
    ) -> list[GetReviewDetailsActiveRow]:
        offset = (page - 1) * page_size
        try:
            rows = await self._db.select(
                _GET_REVIEW_DETAILS_TRASHED,
                {"search": search, "limit": page_size, "offset": offset},
            )
        except Exception as exc:
            raise err_find_trashed_review_details.with_internal(exc) from exc
        return [GetReviewDetailsActiveRow.from_row(row) for row in rows]

    async def find_by_id(self, review_detail_id: int) -> GetReviewDetailByIDRow:
        try:
            row = await self._db.scalar(
                _GET_REVIEW_DETAIL, {"review_detail_id": review_detail_id}
            )
        except Exception as exc:
            raise err_find_review_detail_by_id.with_internal(exc) from exc
        if row is None:
            raise err_find_review_detail_by_id
        return GetReviewDetailByIDRow.from_row(row)

    async def find_by_id_trashed(self, review_detail_id: int) -> ReviewDetail:
        try:
            row = await self._db.scalar(
                _GET_REVIEW_DETAIL_TRASHED, {"review_detail_id": review_detail_id}
            )
        except Exception as exc:
            raise err_find_review_detail_by_id_trashed.with_internal(exc) from exc
        if row is None:
            raise err_find_review_detail_by_id_trashed
        return ReviewDetail.from_row(row)


__all__ = ["ReviewDetailQueryRepositoryImpl"]

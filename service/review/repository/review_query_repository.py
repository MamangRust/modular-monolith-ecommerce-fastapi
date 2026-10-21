"""review read repository. SQL is kept verbatim from the reference where practical, including the `COUNT(*) OVER` window that supplies `total_count` in the same round trip as the page, and the `json_agg` sub-select that aggregates each review's attachments into `review_details`. Named-parameter adaptations (documented): - the `$1::TEXT IS NULL OR...` search guards are dropped: binds a plain `string` (never nil) and an empty search already matches every row via `ILIKE '%%'`; - the rating filter is normalised to "0 means all ratings" (`NULLIF(:rating, 0) IS NULL OR r.rating =:rating`). binds `int32(req.Rating)` (0 when the caller omits it) and tests `r.rating = 0`, so `FindByProduct`/`FindByMerchant` return no rows unless a rating is supplied — and the proto/gateway never supply one. treats 0 as "ignore", matching the product repository's price-filter normalisation. - `FindByProduct`/`FindByMerchant` accept a `search` for the cache key only; the SQL has no search filter, so ignores it in the query too. `find_by_id` maps a missing row to `err_review_not_found` (404) and any other failure to `err_find_review_by_id` (500)."""

from __future__ import annotations

from pkg.database.database import Database
from pkg.database.schema.review import (
    GetReviewByIDRow,
    GetReviewByMerchantIdRow,
    GetReviewByProductIdRow,
    GetReviewsActiveRow,
    GetReviewsRow,
    GetReviewsTrashedRow,
)
from shared.domain.requests.review import (
    FindAllReviews,
    FindAllReviewsByMerchant,
    FindAllReviewsByProduct,
)
from shared.errors import (
    err_find_active_reviews,
    err_find_all_reviews,
    err_find_review_by_id,
    err_find_reviews_by_merchant,
    err_find_reviews_by_product,
    err_find_trashed_reviews,
    err_review_not_found,
)

_GET_REVIEWS = """
SELECT
    review_id,
    user_id,
    product_id,
    name,
    comment,
    rating,
    created_at,
    updated_at,
    COUNT(*) OVER () AS total_count
FROM reviews
WHERE
    deleted_at IS NULL
    AND (
        review_id::TEXT ILIKE '%' || :search || '%'
        OR name ILIKE '%' || :search || '%'
    )
ORDER BY created_at DESC
LIMIT :limit
OFFSET
    :offset
"""

_GET_REVIEWS_ACTIVE = """
SELECT
    review_id,
    user_id,
    product_id,
    name,
    comment,
    rating,
    created_at,
    updated_at,
    deleted_at,
    COUNT(*) OVER () AS total_count
FROM reviews
WHERE
    deleted_at IS NULL
    AND (
        review_id::TEXT ILIKE '%' || :search || '%'
        OR name ILIKE '%' || :search || '%'
    )
ORDER BY created_at DESC
LIMIT :limit
OFFSET
    :offset
"""

_GET_REVIEWS_TRASHED = """
SELECT
    review_id,
    user_id,
    product_id,
    name,
    comment,
    rating,
    created_at,
    updated_at,
    deleted_at,
    COUNT(*) OVER () AS total_count
FROM reviews
WHERE
    deleted_at IS NOT NULL
    AND (
        review_id::TEXT ILIKE '%' || :search || '%'
        OR name ILIKE '%' || :search || '%'
    )
ORDER BY created_at DESC
LIMIT :limit
OFFSET
    :offset
"""

_GET_REVIEW_BY_PRODUCT = """
SELECT
    r.review_id,
    r.user_id,
    r.product_id,
    r.name,
    r.comment,
    r.rating,
    r.created_at,
    r.updated_at,
    r.deleted_at,
    COUNT(*) OVER () AS total_count,
    COALESCE(
        (
            SELECT json_agg(
                    jsonb_build_object(
                        'detail_id', rd.review_detail_id, 'type', rd.type, 'url', rd.url, 'caption', rd.caption, 'created_at', rd.created_at
                    )
                )
            FROM review_details rd
            WHERE
                rd.review_id = r.review_id
        ),
        '[]'
    ) AS review_details
FROM reviews r
WHERE
    r.deleted_at IS NULL
    AND r.product_id = :product_id
    AND (
        NULLIF(:rating, 0) IS NULL
        OR r.rating = :rating
    )
ORDER BY r.created_at DESC
LIMIT :limit
OFFSET
    :offset
"""

_GET_REVIEW_BY_MERCHANT = """
SELECT
    r.review_id,
    r.user_id,
    r.product_id,
    r.name,
    r.comment,
    r.rating,
    r.created_at,
    r.updated_at,
    r.deleted_at,
    COUNT(*) OVER () AS total_count,
    COALESCE(
        (
            SELECT json_agg(
                    jsonb_build_object(
                        'detail_id', rd.review_detail_id, 'type', rd.type, 'url', rd.url, 'caption', rd.caption, 'created_at', rd.created_at
                    )
                )
            FROM review_details rd
            WHERE
                rd.review_id = r.review_id
        ),
        '[]'
    ) AS review_details
FROM reviews r
    JOIN products p ON r.product_id = p.product_id
WHERE
    r.deleted_at IS NULL
    AND p.merchant_id = :merchant_id
    AND (
        NULLIF(:rating, 0) IS NULL
        OR r.rating = :rating
    )
ORDER BY r.created_at DESC
LIMIT :limit
OFFSET
    :offset
"""

_GET_REVIEW_BY_ID = """
SELECT
    review_id,
    user_id,
    product_id,
    name,
    comment,
    rating,
    created_at,
    updated_at
FROM reviews
WHERE
    review_id = :review_id
    AND deleted_at IS NULL
"""


class ReviewQueryRepositoryImpl:
    def __init__(self, db: Database) -> None:
        self._db = db

    async def find_all(self, request: FindAllReviews) -> list[GetReviewsRow]:
        params = {
            "search": request.search,
            "limit": request.page_size,
            "offset": (request.page - 1) * request.page_size,
        }
        try:
            rows = await self._db.select(_GET_REVIEWS, params)
        except Exception as exc:
            raise err_find_all_reviews.with_internal(exc) from exc
        return [GetReviewsRow.from_row(row) for row in rows]

    async def find_by_product(self, request: FindAllReviewsByProduct) -> list[GetReviewByProductIdRow]:
        params = {
            "product_id": request.product_id,
            "rating": request.rating,
            "limit": request.page_size,
            "offset": (request.page - 1) * request.page_size,
        }
        try:
            rows = await self._db.select(_GET_REVIEW_BY_PRODUCT, params)
        except Exception as exc:
            raise err_find_reviews_by_product.with_internal(exc) from exc
        return [GetReviewByProductIdRow.from_row(row) for row in rows]

    async def find_by_merchant(self, request: FindAllReviewsByMerchant) -> list[GetReviewByMerchantIdRow]:
        params = {
            "merchant_id": request.merchant_id,
            "rating": request.rating,
            "limit": request.page_size,
            "offset": (request.page - 1) * request.page_size,
        }
        try:
            rows = await self._db.select(_GET_REVIEW_BY_MERCHANT, params)
        except Exception as exc:
            raise err_find_reviews_by_merchant.with_internal(exc) from exc
        return [GetReviewByMerchantIdRow.from_row(row) for row in rows]

    async def find_active(self, request: FindAllReviews) -> list[GetReviewsActiveRow]:
        params = {
            "search": request.search,
            "limit": request.page_size,
            "offset": (request.page - 1) * request.page_size,
        }
        try:
            rows = await self._db.select(_GET_REVIEWS_ACTIVE, params)
        except Exception as exc:
            raise err_find_active_reviews.with_internal(exc) from exc
        return [GetReviewsActiveRow.from_row(row) for row in rows]

    async def find_trashed(self, request: FindAllReviews) -> list[GetReviewsTrashedRow]:
        params = {
            "search": request.search,
            "limit": request.page_size,
            "offset": (request.page - 1) * request.page_size,
        }
        try:
            rows = await self._db.select(_GET_REVIEWS_TRASHED, params)
        except Exception as exc:
            raise err_find_trashed_reviews.with_internal(exc) from exc
        return [GetReviewsTrashedRow.from_row(row) for row in rows]

    async def find_by_id(self, review_id: int) -> GetReviewByIDRow:
        try:
            row = await self._db.scalar(_GET_REVIEW_BY_ID, {"review_id": review_id})
        except Exception as exc:
            raise err_find_review_by_id.with_internal(exc) from exc
        if row is None:
            raise err_review_not_found
        return GetReviewByIDRow.from_row(row)


__all__ = ["ReviewQueryRepositoryImpl"]

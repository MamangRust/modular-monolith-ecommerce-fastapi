"""review query cache.

Reads/writes never raise: `CacheStore` swallows Redis errors so a cache outage
degrades to a DB read. Each list page stores `{data, total_records}`; the by-id
entry stores the row directly."""

from __future__ import annotations

from collections.abc import Callable
from typing import Any

from pkg.database.schema.review import (
    GetReviewByProductIdRow,
    GetReviewsActiveRow,
    GetReviewsRow,
    ReviewRow,
)
from pkg.logger.logger import Logger
from service.review.redis.cache import (
    review_by_id_from_dict,
    review_by_id_to_dict,
    review_detail_row_from_dict,
    review_detail_row_to_dict,
    reviews_active_row_from_dict,
    reviews_active_row_to_dict,
    reviews_row_from_dict,
    reviews_row_to_dict,
)
from service.review.redis.common import (
    TTL_DEFAULT,
    review_active_key,
    review_all_key,
    review_by_id_key,
    review_merchant_key,
    review_product_key,
    review_trashed_key,
)
from shared.cache import CacheStore
from shared.domain.requests.review import (
    FindAllReviews,
    FindAllReviewsByMerchant,
    FindAllReviewsByProduct,
)


def _encode[T](rows: list[T], total: int, to_dict: Callable[[T], dict[str, Any]]) -> dict[str, Any]:
    return {"data": [to_dict(row) for row in rows], "total_records": total}


def _decode[T](payload: Any, from_dict: Callable[[dict[str, Any], int], T]) -> tuple[list[T], int] | None:
    if not isinstance(payload, dict):
        return None
    data = payload.get("data")
    if not isinstance(data, list):
        return None
    total = int(payload.get("total_records") or 0)
    return [from_dict(item, total) for item in data], total


class ReviewQueryCacheImpl:
    def __init__(self, store: CacheStore, logger: Logger) -> None:
        self._store = store
        self._logger = logger

    # ---- FindAll ----

    async def get_all(self, request: FindAllReviews) -> tuple[list[GetReviewsRow], int] | None:
        payload = await self._store.get_json(review_all_key(request.page, request.page_size, request.search))
        return _decode(payload, reviews_row_from_dict)

    async def set_all(self, request: FindAllReviews, rows: list[GetReviewsRow], total: int) -> None:
        await self._store.set_json(
            review_all_key(request.page, request.page_size, request.search),
            _encode(rows, total, reviews_row_to_dict),
            TTL_DEFAULT,
        )

    # ---- FindByProduct ----

    async def get_by_product(
        self, request: FindAllReviewsByProduct
    ) -> tuple[list[GetReviewByProductIdRow], int] | None:
        payload = await self._store.get_json(
            review_product_key(request.product_id, request.page, request.page_size, request.search)
        )
        return _decode(payload, review_detail_row_from_dict)

    async def set_by_product(
        self,
        request: FindAllReviewsByProduct,
        rows: list[GetReviewByProductIdRow],
        total: int,
    ) -> None:
        await self._store.set_json(
            review_product_key(request.product_id, request.page, request.page_size, request.search),
            _encode(rows, total, review_detail_row_to_dict),
            TTL_DEFAULT,
        )

    # ---- FindByMerchant ----

    async def get_by_merchant(
        self, request: FindAllReviewsByMerchant
    ) -> tuple[list[GetReviewByProductIdRow], int] | None:
        payload = await self._store.get_json(
            review_merchant_key(request.merchant_id, request.page, request.page_size, request.search)
        )
        return _decode(payload, review_detail_row_from_dict)

    async def set_by_merchant(
        self,
        request: FindAllReviewsByMerchant,
        rows: list[GetReviewByProductIdRow],
        total: int,
    ) -> None:
        await self._store.set_json(
            review_merchant_key(request.merchant_id, request.page, request.page_size, request.search),
            _encode(rows, total, review_detail_row_to_dict),
            TTL_DEFAULT,
        )

    # ---- FindActive ----

    async def get_active(self, request: FindAllReviews) -> tuple[list[GetReviewsActiveRow], int] | None:
        payload = await self._store.get_json(
            review_active_key(request.page, request.page_size, request.search)
        )
        return _decode(payload, reviews_active_row_from_dict)

    async def set_active(self, request: FindAllReviews, rows: list[GetReviewsActiveRow], total: int) -> None:
        await self._store.set_json(
            review_active_key(request.page, request.page_size, request.search),
            _encode(rows, total, reviews_active_row_to_dict),
            TTL_DEFAULT,
        )

    # ---- FindTrashed ----

    async def get_trashed(self, request: FindAllReviews) -> tuple[list[GetReviewsActiveRow], int] | None:
        payload = await self._store.get_json(
            review_trashed_key(request.page, request.page_size, request.search)
        )
        return _decode(payload, reviews_active_row_from_dict)

    async def set_trashed(self, request: FindAllReviews, rows: list[GetReviewsActiveRow], total: int) -> None:
        await self._store.set_json(
            review_trashed_key(request.page, request.page_size, request.search),
            _encode(rows, total, reviews_active_row_to_dict),
            TTL_DEFAULT,
        )

    # ---- FindByID ----

    async def get_by_id(self, review_id: int) -> ReviewRow | None:
        payload = await self._store.get_json(review_by_id_key(review_id))
        return review_by_id_from_dict(payload)

    async def set_by_id(self, row: ReviewRow) -> None:
        await self._store.set_json(
            review_by_id_key(row.review_id),
            review_by_id_to_dict(row),
            TTL_DEFAULT,
        )


__all__ = ["ReviewQueryCacheImpl"]

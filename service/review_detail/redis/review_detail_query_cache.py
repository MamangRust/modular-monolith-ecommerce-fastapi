"""Review detail query cache. Every list cache written here is also read (the review detail cache reads all of them, so this is a straight port). Reads/writes never raise: `CacheStore` swallows Redis errors so a cache outage degrades to a DB read."""

from __future__ import annotations

from pkg.database.schema.review_detail import (
    GetReviewDetailByIDRow,
    GetReviewDetailsActiveRow,
    GetReviewDetailsRow,
    ReviewDetail,
)
from pkg.logger.logger import Logger
from service.review_detail.redis.cache import (
    active_row_from_dict,
    active_row_to_dict,
    review_detail_by_id_from_dict,
    review_detail_by_id_to_dict,
    review_detail_row_from_dict,
    review_detail_row_to_dict,
    trashed_row_from_dict,
    trashed_row_to_dict,
)
from service.review_detail.redis.common import (
    TTL_DEFAULT,
    review_detail_active_key,
    review_detail_all_key,
    review_detail_by_id_key,
    review_detail_trashed_key,
)
from shared.cache import CacheStore


class ReviewDetailQueryCacheImpl:
    def __init__(self, store: CacheStore, logger: Logger) -> None:
        self._store = store
        self._logger = logger

    async def get_review_details(
        self, page: int, page_size: int, search: str
    ) -> tuple[list[GetReviewDetailsRow], int] | None:
        payload = await self._store.get_json(
            review_detail_all_key(page, page_size, search)
        )
        return _decode_page(payload, review_detail_row_from_dict)

    async def set_review_details(
        self,
        page: int,
        page_size: int,
        search: str,
        rows: list[GetReviewDetailsRow],
        total: int,
    ) -> None:
        await self._store.set_json(
            review_detail_all_key(page, page_size, search),
            _encode_page(rows, total, review_detail_row_to_dict),
            TTL_DEFAULT,
        )

    async def get_review_detail_by_id(
        self, review_detail_id: int
    ) -> GetReviewDetailByIDRow | None:
        payload = await self._store.get_json(review_detail_by_id_key(review_detail_id))
        if not isinstance(payload, dict):
            return None
        return review_detail_by_id_from_dict(payload)

    async def set_review_detail_by_id(self, row: GetReviewDetailByIDRow) -> None:
        await self._store.set_json(
            review_detail_by_id_key(row.review_detail_id),
            review_detail_by_id_to_dict(row),
            TTL_DEFAULT,
        )

    async def get_active(
        self, page: int, page_size: int, search: str
    ) -> tuple[list[GetReviewDetailsActiveRow], int] | None:
        payload = await self._store.get_json(
            review_detail_active_key(page, page_size, search)
        )
        return _decode_page(payload, active_row_from_dict)

    async def set_active(
        self,
        page: int,
        page_size: int,
        search: str,
        rows: list[GetReviewDetailsActiveRow],
        total: int,
    ) -> None:
        await self._store.set_json(
            review_detail_active_key(page, page_size, search),
            _encode_page(rows, total, active_row_to_dict),
            TTL_DEFAULT,
        )

    async def get_trashed(
        self, page: int, page_size: int, search: str
    ) -> tuple[list[GetReviewDetailsActiveRow], int] | None:
        payload = await self._store.get_json(
            review_detail_trashed_key(page, page_size, search)
        )
        return _decode_page(payload, trashed_row_from_dict)

    async def set_trashed(
        self,
        page: int,
        page_size: int,
        search: str,
        rows: list[GetReviewDetailsActiveRow],
        total: int,
    ) -> None:
        await self._store.set_json(
            review_detail_trashed_key(page, page_size, search),
            _encode_page(rows, total, trashed_row_to_dict),
            TTL_DEFAULT,
        )

    async def get_trashed_by_id(self, review_detail_id: int) -> ReviewDetail | None:
        payload = await self._store.get_json(review_detail_by_id_key(review_detail_id))
        if not isinstance(payload, dict):
            return None
        return ReviewDetail.from_row(payload)


def _encode_page(rows: list, total: int, to_dict) -> dict:
    return {"data": [to_dict(row) for row in rows], "total_records": total}


def _decode_page(payload, from_dict):
    if not isinstance(payload, dict):
        return None
    data = payload.get("data")
    if not isinstance(data, list):
        return None
    total = int(payload.get("total_records") or 0)
    return [from_dict(item, total) for item in data], total


__all__ = ["ReviewDetailQueryCacheImpl"]

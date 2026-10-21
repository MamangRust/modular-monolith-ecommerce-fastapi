"""Review detail cache"""

from __future__ import annotations

from typing import Protocol

from pkg.database.schema.review_detail import (
    GetReviewDetailByIDRow,
    GetReviewDetailsActiveRow,
    GetReviewDetailsRow,
)


class ReviewDetailQueryCache(Protocol):
    async def get_review_details(
        self, page: int, page_size: int, search: str
    ) -> tuple[list[GetReviewDetailsRow], int] | None: ...

    async def set_review_details(
        self,
        page: int,
        page_size: int,
        search: str,
        rows: list[GetReviewDetailsRow],
        total: int,
    ) -> None: ...

    async def get_review_detail_by_id(
        self, review_detail_id: int
    ) -> GetReviewDetailByIDRow | None: ...

    async def set_review_detail_by_id(self, row: GetReviewDetailByIDRow) -> None: ...

    async def get_active(
        self, page: int, page_size: int, search: str
    ) -> tuple[list[GetReviewDetailsActiveRow], int] | None: ...

    async def set_active(
        self,
        page: int,
        page_size: int,
        search: str,
        rows: list[GetReviewDetailsActiveRow],
        total: int,
    ) -> None: ...

    async def get_trashed(
        self, page: int, page_size: int, search: str
    ) -> tuple[list[GetReviewDetailsActiveRow], int] | None: ...

    async def set_trashed(
        self,
        page: int,
        page_size: int,
        search: str,
        rows: list[GetReviewDetailsActiveRow],
        total: int,
    ) -> None: ...


class ReviewDetailCommandCache(Protocol):
    async def delete_review_detail_cache(self, review_detail_id: int) -> int: ...

    async def invalidate_review_detail_cache(self) -> int: ...


__all__ = ["ReviewDetailCommandCache", "ReviewDetailQueryCache"]

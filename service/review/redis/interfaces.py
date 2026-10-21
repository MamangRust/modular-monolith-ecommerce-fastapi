"""review cache"""

from __future__ import annotations

from typing import Protocol

from pkg.database.schema.review import (
    GetReviewByProductIdRow,
    GetReviewsActiveRow,
    GetReviewsRow,
    ReviewRow,
)
from shared.domain.requests.review import (
    FindAllReviews,
    FindAllReviewsByMerchant,
    FindAllReviewsByProduct,
)


class ReviewQueryCache(Protocol):
    async def get_all(self, request: FindAllReviews) -> tuple[list[GetReviewsRow], int] | None: ...

    async def set_all(self, request: FindAllReviews, rows: list[GetReviewsRow], total: int) -> None: ...

    async def get_by_product(
        self, request: FindAllReviewsByProduct
    ) -> tuple[list[GetReviewByProductIdRow], int] | None: ...

    async def set_by_product(
        self,
        request: FindAllReviewsByProduct,
        rows: list[GetReviewByProductIdRow],
        total: int,
    ) -> None: ...

    async def get_by_merchant(
        self, request: FindAllReviewsByMerchant
    ) -> tuple[list[GetReviewByProductIdRow], int] | None: ...

    async def set_by_merchant(
        self,
        request: FindAllReviewsByMerchant,
        rows: list[GetReviewByProductIdRow],
        total: int,
    ) -> None: ...

    async def get_active(self, request: FindAllReviews) -> tuple[list[GetReviewsActiveRow], int] | None: ...

    async def set_active(
        self, request: FindAllReviews, rows: list[GetReviewsActiveRow], total: int
    ) -> None: ...

    async def get_trashed(self, request: FindAllReviews) -> tuple[list[GetReviewsActiveRow], int] | None: ...

    async def set_trashed(
        self, request: FindAllReviews, rows: list[GetReviewsActiveRow], total: int
    ) -> None: ...

    async def get_by_id(self, review_id: int) -> ReviewRow | None: ...

    async def set_by_id(self, row: ReviewRow) -> None: ...


class ReviewCommandCache(Protocol):
    async def delete_cached_review(self, review_id: int) -> int: ...


__all__ = [
    "ReviewCommandCache",
    "ReviewQueryCache",
]

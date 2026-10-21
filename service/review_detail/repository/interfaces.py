"""Review detail repository"""

from __future__ import annotations

from typing import Protocol

from pkg.database.schema.review_detail import (
    CreateReviewDetailRow,
    GetReviewDetailByIDRow,
    GetReviewDetailsActiveRow,
    GetReviewDetailsRow,
    ReviewDetail,
    UpdateReviewDetailRow,
)
from shared.domain.requests.review_detail import (
    CreateReviewDetailRequest,
    UpdateReviewDetailRequest,
)


class ReviewDetailQueryRepository(Protocol):
    async def find_all(
        self, search: str, page: int, page_size: int
    ) -> list[GetReviewDetailsRow]: ...

    async def find_active(
        self, search: str, page: int, page_size: int
    ) -> list[GetReviewDetailsActiveRow]: ...

    async def find_trashed(
        self, search: str, page: int, page_size: int
    ) -> list[GetReviewDetailsActiveRow]: ...

    async def find_by_id(self, review_detail_id: int) -> GetReviewDetailByIDRow: ...

    async def find_by_id_trashed(self, review_detail_id: int) -> ReviewDetail: ...


class ReviewDetailCommandRepository(Protocol):
    async def create(self, request: CreateReviewDetailRequest) -> CreateReviewDetailRow: ...

    async def update(self, request: UpdateReviewDetailRequest) -> UpdateReviewDetailRow: ...

    async def trash(self, review_detail_id: int) -> ReviewDetail: ...

    async def restore(self, review_detail_id: int) -> ReviewDetail: ...

    async def delete_permanent(self, review_detail_id: int) -> bool: ...

    async def restore_all(self) -> bool: ...

    async def delete_all_permanent(self) -> bool: ...


__all__ = ["ReviewDetailCommandRepository", "ReviewDetailQueryRepository"]

"""review service"""

from __future__ import annotations

from typing import Protocol

from pkg.database.schema.review import (
    CreateReviewRow,
    GetReviewByIDRow,
    GetReviewByMerchantIdRow,
    GetReviewByProductIdRow,
    GetReviewsActiveRow,
    GetReviewsRow,
    GetReviewsTrashedRow,
    Review,
    UpdateReviewRow,
)
from shared.domain.requests.review import (
    CreateReviewRequest,
    FindAllReviews,
    FindAllReviewsByMerchant,
    FindAllReviewsByProduct,
    UpdateReviewRequest,
)


class ReviewQueryService(Protocol):
    async def find_all(self, request: FindAllReviews) -> tuple[list[GetReviewsRow], int]: ...

    async def find_by_product(
        self, request: FindAllReviewsByProduct
    ) -> tuple[list[GetReviewByProductIdRow], int]: ...

    async def find_by_merchant(
        self, request: FindAllReviewsByMerchant
    ) -> tuple[list[GetReviewByMerchantIdRow], int]: ...

    async def find_active(self, request: FindAllReviews) -> tuple[list[GetReviewsActiveRow], int]: ...

    async def find_trashed(self, request: FindAllReviews) -> tuple[list[GetReviewsTrashedRow], int]: ...

    async def find_by_id(self, review_id: int) -> GetReviewByIDRow: ...


class ReviewCommandService(Protocol):
    async def create(self, request: CreateReviewRequest) -> CreateReviewRow: ...

    async def update(self, request: UpdateReviewRequest) -> UpdateReviewRow: ...

    async def trash(self, review_id: int) -> Review: ...

    async def restore(self, review_id: int) -> Review: ...

    async def delete_permanent(self, review_id: int) -> bool: ...

    async def restore_all(self) -> bool: ...

    async def delete_all(self) -> bool: ...


__all__ = [
    "ReviewCommandService",
    "ReviewQueryService",
]

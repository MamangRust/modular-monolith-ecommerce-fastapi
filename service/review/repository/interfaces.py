"""The other two repositories are SQL-backed. Both adapters are consumed by the command service's `Create` (user existence + product existence)."""

from __future__ import annotations

from typing import Protocol

from pkg.database.schema.product import GetProductByIDRow
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
from pkg.database.schema.user import GetUserByIDRow
from shared.domain.requests.review import (
    CreateReviewRecord,
    FindAllReviews,
    FindAllReviewsByMerchant,
    FindAllReviewsByProduct,
    UpdateReviewRequest,
)


class UserQueryRepository(Protocol):
    async def find_by_id(self, user_id: int) -> GetUserByIDRow: ...


class ProductQueryRepository(Protocol):
    async def find_by_id(self, product_id: int) -> GetProductByIDRow: ...


class ReviewQueryRepository(Protocol):
    async def find_all(self, request: FindAllReviews) -> list[GetReviewsRow]: ...

    async def find_by_product(self, request: FindAllReviewsByProduct) -> list[GetReviewByProductIdRow]: ...

    async def find_by_merchant(self, request: FindAllReviewsByMerchant) -> list[GetReviewByMerchantIdRow]: ...

    async def find_active(self, request: FindAllReviews) -> list[GetReviewsActiveRow]: ...

    async def find_trashed(self, request: FindAllReviews) -> list[GetReviewsTrashedRow]: ...

    async def find_by_id(self, review_id: int) -> GetReviewByIDRow: ...


class ReviewCommandRepository(Protocol):
    async def create(self, request: CreateReviewRecord) -> CreateReviewRow: ...

    async def update(self, request: UpdateReviewRequest) -> UpdateReviewRow: ...

    async def trash(self, review_id: int) -> Review: ...

    async def restore(self, review_id: int) -> Review: ...

    async def delete_permanent(self, review_id: int) -> bool: ...

    async def restore_all(self) -> bool: ...

    async def delete_all(self) -> bool: ...


__all__ = [
    "ProductQueryRepository",
    "ReviewCommandRepository",
    "ReviewQueryRepository",
    "UserQueryRepository",
]

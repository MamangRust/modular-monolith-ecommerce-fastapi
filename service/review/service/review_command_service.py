"""review command service. `Create` validates the user and the product through the gRPC adapters (user first, then product) before writing; the repository `name` column is left empty because `CreateReviewRequest` carries no name. `Update` first loads the review through the query repository."""

from __future__ import annotations

from pkg.database.schema.review import (
    CreateReviewRow,
    Review,
    UpdateReviewRow,
)
from pkg.logger.logger import Logger
from service.review.redis.interfaces import ReviewCommandCache
from service.review.repository.interfaces import (
    ProductQueryRepository,
    ReviewCommandRepository,
    ReviewQueryRepository,
    UserQueryRepository,
)
from shared.domain.requests.review import (
    CreateReviewRecord,
    CreateReviewRequest,
    UpdateReviewRequest,
)
from shared.errors import (
    err_failed_create_review,
    err_failed_restore_all_reviews,
    err_failed_update_review,
    err_review_not_found,
)
from shared.observability import Observability


class ReviewCommandServiceImpl:
    def __init__(
        self,
        repo: ReviewCommandRepository,
        query_repo: ReviewQueryRepository,
        user_repo: UserQueryRepository,
        product_repo: ProductQueryRepository,
        cache: ReviewCommandCache,
        logger: Logger,
        obs: Observability,
    ) -> None:
        self._repo = repo
        self._query_repo = query_repo
        self._user_repo = user_repo
        self._product_repo = product_repo
        self._cache = cache
        self._logger = logger
        self._obs = obs

    async def create(self, request: CreateReviewRequest) -> CreateReviewRow:
        with self._obs.span(
            "review.command.create",
            user_id=request.user_id,
            product_id=request.product_id,
        ):
            await self._user_repo.find_by_id(request.user_id)
            await self._product_repo.find_by_id(request.product_id)

            record = CreateReviewRecord(
                user_id=request.user_id,
                product_id=request.product_id,
                name="",
                comment=request.comment,
                rating=request.rating,
            )
            try:
                row = await self._repo.create(record)
            except Exception as exc:
                raise err_failed_create_review.with_internal(exc) from exc

            await self._cache.delete_cached_review(row.review_id)
            return row

    async def update(self, request: UpdateReviewRequest) -> UpdateReviewRow:
        review_id = request.review_id or 0
        with self._obs.span("review.command.update", review_id=review_id):
            try:
                await self._query_repo.find_by_id(review_id)
            except Exception as exc:
                raise err_review_not_found from exc

            try:
                row = await self._repo.update(request)
            except Exception as exc:
                raise err_failed_update_review.with_internal(exc) from exc

            await self._cache.delete_cached_review(row.review_id)
            return row

    async def trash(self, review_id: int) -> Review:
        with self._obs.span("review.command.trash", review_id=review_id):
            row = await self._repo.trash(review_id)
            await self._cache.delete_cached_review(row.review_id)
            return row

    async def restore(self, review_id: int) -> Review:
        with self._obs.span("review.command.restore", review_id=review_id):
            row = await self._repo.restore(review_id)
            await self._cache.delete_cached_review(row.review_id)
            return row

    async def delete_permanent(self, review_id: int) -> bool:
        with self._obs.span("review.command.delete_permanent", review_id=review_id):
            success = await self._repo.delete_permanent(review_id)
            await self._cache.delete_cached_review(review_id)
            return success

    async def restore_all(self) -> bool:
        with self._obs.span("review.command.restore_all"):
            try:
                return await self._repo.restore_all()
            except Exception as exc:
                raise err_failed_restore_all_reviews.with_internal(exc) from exc

    async def delete_all(self) -> bool:
        with self._obs.span("review.command.delete_all"):
            return await self._repo.delete_all()


__all__ = ["ReviewCommandServiceImpl"]

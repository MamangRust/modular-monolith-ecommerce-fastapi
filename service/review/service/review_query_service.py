"""review query service. Reads are cache-first: a miss loads from the DB and populates the cache with the page and its window `total_count` (taken from the first row; 0 when the page is empty). NORMALISATION: clamps `page <= 0 → 1` / `pageSize <= 0 → 10` inside the service (`reviewQueryService.FindAll` and siblings). Like the other domains, that clamp lives in the gRPC handler (`normalize_page`), so the service receives already-normalised paging."""

from __future__ import annotations

from pkg.database.schema.review import (
    GetReviewByIDRow,
    GetReviewByMerchantIdRow,
    GetReviewByProductIdRow,
    GetReviewsActiveRow,
    GetReviewsRow,
    GetReviewsTrashedRow,
)
from pkg.logger.logger import Logger
from service.review.redis.interfaces import ReviewQueryCache
from service.review.repository.interfaces import ReviewQueryRepository
from shared.domain.requests.review import (
    FindAllReviews,
    FindAllReviewsByMerchant,
    FindAllReviewsByProduct,
)
from shared.errors import (
    err_failed_find_active_reviews,
    err_failed_find_all_reviews,
    err_failed_find_by_merchant_reviews,
    err_failed_find_by_product_reviews,
    err_failed_find_trashed_reviews,
    err_review_not_found,
)
from shared.observability import Observability


class ReviewQueryServiceImpl:
    def __init__(
        self,
        repo: ReviewQueryRepository,
        cache: ReviewQueryCache,
        logger: Logger,
        obs: Observability,
    ) -> None:
        self._repo = repo
        self._cache = cache
        self._logger = logger
        self._obs = obs

    async def find_all(self, request: FindAllReviews) -> tuple[list[GetReviewsRow], int]:
        with self._obs.span(
            "review.query.find_all",
            page=request.page,
            page_size=request.page_size,
            search=request.search,
        ):
            cached = await self._cache.get_all(request)
            if cached is not None:
                return cached
            try:
                rows = await self._repo.find_all(request)
            except Exception as exc:
                raise err_failed_find_all_reviews.with_internal(exc) from exc
            total = rows[0].total_count if rows else 0
            await self._cache.set_all(request, rows, total)
            return rows, total

    async def find_by_product(
        self, request: FindAllReviewsByProduct
    ) -> tuple[list[GetReviewByProductIdRow], int]:
        with self._obs.span(
            "review.query.find_by_product",
            product_id=request.product_id,
            page=request.page,
            page_size=request.page_size,
            search=request.search,
        ):
            cached = await self._cache.get_by_product(request)
            if cached is not None:
                return cached
            try:
                rows = await self._repo.find_by_product(request)
            except Exception as exc:
                raise err_failed_find_by_product_reviews.with_internal(exc) from exc
            total = rows[0].total_count if rows else 0
            await self._cache.set_by_product(request, rows, total)
            return rows, total

    async def find_by_merchant(
        self, request: FindAllReviewsByMerchant
    ) -> tuple[list[GetReviewByMerchantIdRow], int]:
        with self._obs.span(
            "review.query.find_by_merchant",
            merchant_id=request.merchant_id,
            page=request.page,
            page_size=request.page_size,
            search=request.search,
        ):
            cached = await self._cache.get_by_merchant(request)
            if cached is not None:
                return cached
            try:
                rows = await self._repo.find_by_merchant(request)
            except Exception as exc:
                raise err_failed_find_by_merchant_reviews.with_internal(exc) from exc
            total = rows[0].total_count if rows else 0
            await self._cache.set_by_merchant(request, rows, total)
            return rows, total

    async def find_active(self, request: FindAllReviews) -> tuple[list[GetReviewsActiveRow], int]:
        with self._obs.span(
            "review.query.find_active",
            page=request.page,
            page_size=request.page_size,
            search=request.search,
        ):
            cached = await self._cache.get_active(request)
            if cached is not None:
                return cached
            try:
                rows = await self._repo.find_active(request)
            except Exception as exc:
                raise err_failed_find_active_reviews.with_internal(exc) from exc
            total = rows[0].total_count if rows else 0
            await self._cache.set_active(request, rows, total)
            return rows, total

    async def find_trashed(self, request: FindAllReviews) -> tuple[list[GetReviewsTrashedRow], int]:
        with self._obs.span(
            "review.query.find_trashed",
            page=request.page,
            page_size=request.page_size,
            search=request.search,
        ):
            cached = await self._cache.get_trashed(request)
            if cached is not None:
                return cached
            try:
                rows = await self._repo.find_trashed(request)
            except Exception as exc:
                raise err_failed_find_trashed_reviews.with_internal(exc) from exc
            total = rows[0].total_count if rows else 0
            await self._cache.set_trashed(request, rows, total)
            return rows, total

    async def find_by_id(self, review_id: int) -> GetReviewByIDRow:
        with self._obs.span("review.query.find_by_id", review_id=review_id):
            cached = await self._cache.get_by_id(review_id)
            if cached is not None:
                return cached
            try:
                row = await self._repo.find_by_id(review_id)
            except Exception as exc:
                raise err_review_not_found.with_internal(exc) from exc
            await self._cache.set_by_id(row)
            return row


__all__ = ["ReviewQueryServiceImpl"]

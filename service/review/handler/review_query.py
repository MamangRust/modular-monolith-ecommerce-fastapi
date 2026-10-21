"""review query gRPC handler. `FindAll`/`FindByProduct`/`FindByMerchant`/`FindByActive`/`FindByTrashed` normalise paging via `normalize_page` and read the window `total` from the service. The proto never supplies a `rating`, so leaves `FindAllReviewByProduct`/`...ByMerchant`'s `Rating` at its zero value; does the same. There is no `FindById` RPC on `ReviewQueryService` (the proto omits it), so the service's `find_by_id` is not served here."""

from __future__ import annotations

from typing import Any

from pb.review import review_common_pb2, review_query_pb2_grpc
from pkg.logger.logger import Logger
from pkg.middleware import grpc_method
from service.review.handler.mapping import (
    fill_review_response,
    fill_review_response_delete_at,
    fill_reviews_detail_response,
    normalize_page,
    pagination_meta,
)
from service.review.service.interfaces import ReviewQueryService
from service.review.service.service import SERVICE_NAME
from shared.domain.requests.review import (
    FindAllReviews,
    FindAllReviewsByMerchant,
    FindAllReviewsByProduct,
)


class ReviewQueryHandler(review_query_pb2_grpc.ReviewQueryServiceServicer):
    def __init__(self, service: ReviewQueryService, logger: Logger) -> None:
        self._service = service
        self.logger = logger

    @grpc_method("ReviewQueryService.FindAll", SERVICE_NAME)
    async def FindAll(self, request: Any, context: Any) -> Any:
        page, page_size = normalize_page(request.page, request.page_size)
        rows, total = await self._service.find_all(
            FindAllReviews(search=request.search, page=page, page_size=page_size)
        )
        response = review_common_pb2.ApiResponsePaginationReview(
            status="success", message="Successfully fetched reviews"
        )
        for row in rows:
            fill_review_response(response.data.add(), row)
        response.pagination.CopyFrom(pagination_meta(page, page_size, total))
        return response

    @grpc_method("ReviewQueryService.FindByProduct", SERVICE_NAME)
    async def FindByProduct(self, request: Any, context: Any) -> Any:
        page, page_size = normalize_page(request.page, request.page_size)
        rows, total = await self._service.find_by_product(
            FindAllReviewsByProduct(
                product_id=request.product_id,
                rating=0,
                search=request.search,
                page=page,
                page_size=page_size,
            )
        )
        response = review_common_pb2.ApiResponsePaginationReviewDetail(
            status="success", message="Successfully fetched product reviews"
        )
        for row in rows:
            fill_reviews_detail_response(response.data.add(), row)
        response.pagination.CopyFrom(pagination_meta(page, page_size, total))
        return response

    @grpc_method("ReviewQueryService.FindByMerchant", SERVICE_NAME)
    async def FindByMerchant(self, request: Any, context: Any) -> Any:
        page, page_size = normalize_page(request.page, request.page_size)
        rows, total = await self._service.find_by_merchant(
            FindAllReviewsByMerchant(
                merchant_id=request.merchant_id,
                rating=0,
                search=request.search,
                page=page,
                page_size=page_size,
            )
        )
        response = review_common_pb2.ApiResponsePaginationReviewDetail(
            status="success", message="Successfully fetched merchant reviews"
        )
        for row in rows:
            fill_reviews_detail_response(response.data.add(), row)
        response.pagination.CopyFrom(pagination_meta(page, page_size, total))
        return response

    @grpc_method("ReviewQueryService.FindByActive", SERVICE_NAME)
    async def FindByActive(self, request: Any, context: Any) -> Any:
        page, page_size = normalize_page(request.page, request.page_size)
        rows, total = await self._service.find_active(
            FindAllReviews(search=request.search, page=page, page_size=page_size)
        )
        response = review_common_pb2.ApiResponsePaginationReviewDeleteAt(
            status="success", message="Successfully fetched active reviews"
        )
        for row in rows:
            fill_review_response_delete_at(response.data.add(), row)
        response.pagination.CopyFrom(pagination_meta(page, page_size, total))
        return response

    @grpc_method("ReviewQueryService.FindByTrashed", SERVICE_NAME)
    async def FindByTrashed(self, request: Any, context: Any) -> Any:
        page, page_size = normalize_page(request.page, request.page_size)
        rows, total = await self._service.find_trashed(
            FindAllReviews(search=request.search, page=page, page_size=page_size)
        )
        response = review_common_pb2.ApiResponsePaginationReviewDeleteAt(
            status="success", message="Successfully fetched trashed reviews"
        )
        for row in rows:
            fill_review_response_delete_at(response.data.add(), row)
        response.pagination.CopyFrom(pagination_meta(page, page_size, total))
        return response


__all__ = ["ReviewQueryHandler"]

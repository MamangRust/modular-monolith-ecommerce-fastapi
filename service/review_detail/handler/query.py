"""Review detail query gRPC handler. Review detail timestamps are emitted as date-only strings (`%Y-%m-%d`), matching the `2006-01-02` layout. A NULL `deleted_at` is rendered with no wrapper (the mapping only attaches it when `DeletedAt.Valid`), so the gateway emits `deleted_at: null` rather than an empty string. `caption` may be NULL on the row, but proto3 `string` cannot be `None`, so it is coerced to `""`. `FindById` guards `id <= 0` with `err_grpc_invalid_id` (400) — unlike slider, whose source has no such guard. `FindAll`/`FindByActive`/`FindByTrashed` take the shared `pb.review.FindAllReviewRequest`."""

from __future__ import annotations

import math
from typing import Any

from google.protobuf import wrappers_pb2

from pb.common import api_pb2 as common_pb2
from pb.review_detail import review_detail_common_pb2, review_detail_query_pb2_grpc
from pkg.logger.logger import Logger
from pkg.middleware import grpc_method
from service.review_detail.service.interfaces import ReviewDetailQueryService
from service.review_detail.service.service import SERVICE_NAME
from shared.convert.convert import format_date
from shared.errors.review_detail_errors import err_grpc_invalid_id


def _fill_review_detail(message: Any, review_detail: Any) -> None:
    message.id = review_detail.review_detail_id
    message.review_id = review_detail.review_id
    message.type = review_detail.type
    message.url = review_detail.url
    message.caption = review_detail.caption or ""
    message.created_at = format_date(review_detail.created_at)
    message.updated_at = format_date(review_detail.updated_at)


def _fill_review_detail_delete_at(message: Any, review_detail: Any) -> None:
    _fill_review_detail(message, review_detail)
    deleted_at = format_date(review_detail.deleted_at)
    if deleted_at:
        message.deleted_at.CopyFrom(wrappers_pb2.StringValue(value=deleted_at))


def _total_pages(total: int, page_size: int) -> int:
    return math.ceil(total / page_size) if page_size else 0


def _normalize(page: int, page_size: int) -> tuple[int, int]:
    if page <= 0:
        page = 1
    if page_size <= 0:
        page_size = 10
    return page, page_size


def _pagination(page: int, page_size: int, total: int) -> Any:
    return common_pb2.PaginationMeta(
        current_page=page,
        page_size=page_size,
        total_pages=_total_pages(total, page_size),
        total_records=total,
    )


class ReviewDetailQueryHandler(
    review_detail_query_pb2_grpc.ReviewDetailQueryServiceServicer
):
    def __init__(self, service: ReviewDetailQueryService, logger: Logger) -> None:
        self._service = service
        self.logger = logger

    @grpc_method("ReviewDetailQueryService.FindAll", SERVICE_NAME)
    async def FindAll(self, request: Any, context: Any) -> Any:
        page, page_size = _normalize(request.page, request.page_size)
        rows, total = await self._service.find_all(request.search, page, page_size)
        response = review_detail_common_pb2.ApiResponsePaginationReviewDetails(
            status="success", message="Successfully fetched review details"
        )
        for row in rows:
            _fill_review_detail(response.data.add(), row)
        response.pagination.CopyFrom(_pagination(page, page_size, total))
        return response

    @grpc_method("ReviewDetailQueryService.FindById", SERVICE_NAME)
    async def FindById(self, request: Any, context: Any) -> Any:
        if request.id <= 0:
            raise err_grpc_invalid_id
        review_detail = await self._service.find_by_id(request.id)
        response = review_detail_common_pb2.ApiResponseReviewDetail(
            status="success", message="Successfully fetched review detail"
        )
        _fill_review_detail(response.data, review_detail)
        return response

    @grpc_method("ReviewDetailQueryService.FindByActive", SERVICE_NAME)
    async def FindByActive(self, request: Any, context: Any) -> Any:
        page, page_size = _normalize(request.page, request.page_size)
        rows, total = await self._service.find_active(request.search, page, page_size)
        response = review_detail_common_pb2.ApiResponsePaginationReviewDetailsDeleteAt(
            status="success", message="Successfully fetched active review details"
        )
        for row in rows:
            _fill_review_detail_delete_at(response.data.add(), row)
        response.pagination.CopyFrom(_pagination(page, page_size, total))
        return response

    @grpc_method("ReviewDetailQueryService.FindByTrashed", SERVICE_NAME)
    async def FindByTrashed(self, request: Any, context: Any) -> Any:
        page, page_size = _normalize(request.page, request.page_size)
        rows, total = await self._service.find_trashed(request.search, page, page_size)
        response = review_detail_common_pb2.ApiResponsePaginationReviewDetailsDeleteAt(
            status="success", message="Successfully fetched trashed review details"
        )
        for row in rows:
            _fill_review_detail_delete_at(response.data.add(), row)
        response.pagination.CopyFrom(_pagination(page, page_size, total))
        return response


__all__ = ["ReviewDetailQueryHandler"]

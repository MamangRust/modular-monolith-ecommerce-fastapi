"""Review detail command gRPC handler. the create/update requests carry no `validate` tags, so there is no request-shape validation here — the handler forwards the proto fields straight to the service. The `id <= 0` guard uses `err_grpc_invalid_id` (400) on every command that carries an id (`Update`, `Trashed`, `Restore`, `DeletePermanent`); `Create` and the bulk `RestoreAll`/`DeleteAll` have no id to guard. `DeleteReviewDetailPermanent` returns `pb.review.ApiResponseReviewDelete` and the two bulk ops return `pb.review.ApiResponseReviewAll` (shared review responses), matching the command service. Every failure other than the id guard is propagated from the service and mapped to its original code by the `grpc_method` decorator (a 404 `review detail not found` stays `NOT_FOUND`)."""

from __future__ import annotations

from typing import Any

from pb.review import review_common_pb2
from pb.review_detail import (
    review_detail_command_pb2_grpc,
    review_detail_common_pb2,
)
from pkg.logger.logger import Logger
from pkg.middleware import grpc_method
from service.review_detail.handler.query import (
    _fill_review_detail,
    _fill_review_detail_delete_at,
)
from service.review_detail.service.interfaces import ReviewDetailCommandService
from service.review_detail.service.service import SERVICE_NAME
from shared.domain.requests.review_detail import (
    CreateReviewDetailRequest,
    UpdateReviewDetailRequest,
)
from shared.errors.review_detail_errors import err_grpc_invalid_id


class ReviewDetailCommandHandler(
    review_detail_command_pb2_grpc.ReviewDetailCommandServiceServicer
):
    def __init__(self, service: ReviewDetailCommandService, logger: Logger) -> None:
        self._service = service
        self.logger = logger

    @grpc_method("ReviewDetailCommandService.Create", SERVICE_NAME)
    async def Create(self, request: Any, context: Any) -> Any:
        create_request = CreateReviewDetailRequest(
            review_id=request.review_id,
            type=request.type,
            url=request.url,
            caption=request.caption,
        )
        review_detail = await self._service.create(create_request)
        response = review_detail_common_pb2.ApiResponseReviewDetail(
            status="success", message="Successfully created review detail"
        )
        _fill_review_detail(response.data, review_detail)
        return response

    @grpc_method("ReviewDetailCommandService.Update", SERVICE_NAME)
    async def Update(self, request: Any, context: Any) -> Any:
        if request.review_detail_id <= 0:
            raise err_grpc_invalid_id
        update_request = UpdateReviewDetailRequest(
            review_detail_id=request.review_detail_id,
            type=request.type,
            url=request.url,
            caption=request.caption,
        )
        review_detail = await self._service.update(update_request)
        response = review_detail_common_pb2.ApiResponseReviewDetail(
            status="success", message="Successfully updated review detail"
        )
        _fill_review_detail(response.data, review_detail)
        return response

    @grpc_method("ReviewDetailCommandService.TrashedReviewDetail", SERVICE_NAME)
    async def TrashedReviewDetail(self, request: Any, context: Any) -> Any:
        if request.id <= 0:
            raise err_grpc_invalid_id
        review_detail = await self._service.trash(request.id)
        response = review_detail_common_pb2.ApiResponseReviewDetailDeleteAt(
            status="success", message="Successfully trashed review detail"
        )
        _fill_review_detail_delete_at(response.data, review_detail)
        return response

    @grpc_method("ReviewDetailCommandService.RestoreReviewDetail", SERVICE_NAME)
    async def RestoreReviewDetail(self, request: Any, context: Any) -> Any:
        if request.id <= 0:
            raise err_grpc_invalid_id
        review_detail = await self._service.restore(request.id)
        response = review_detail_common_pb2.ApiResponseReviewDetailDeleteAt(
            status="success", message="Successfully restored review detail"
        )
        _fill_review_detail_delete_at(response.data, review_detail)
        return response

    @grpc_method("ReviewDetailCommandService.DeleteReviewDetailPermanent", SERVICE_NAME)
    async def DeleteReviewDetailPermanent(self, request: Any, context: Any) -> Any:
        if request.id <= 0:
            raise err_grpc_invalid_id
        await self._service.delete_permanent(request.id)
        return review_common_pb2.ApiResponseReviewDelete(
            status="success",
            message="Successfully deleted review detail permanently",
        )

    @grpc_method("ReviewDetailCommandService.RestoreAllReviewDetail", SERVICE_NAME)
    async def RestoreAllReviewDetail(self, request: Any, context: Any) -> Any:
        await self._service.restore_all()
        return review_common_pb2.ApiResponseReviewAll(
            status="success",
            message="Successfully restored all review details",
        )

    @grpc_method("ReviewDetailCommandService.DeleteAllReviewDetailPermanent", SERVICE_NAME)
    async def DeleteAllReviewDetailPermanent(self, request: Any, context: Any) -> Any:
        await self._service.delete_all_permanent()
        return review_common_pb2.ApiResponseReviewAll(
            status="success",
            message="Successfully deleted all review details permanently",
        )


__all__ = ["ReviewDetailCommandHandler"]

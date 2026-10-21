"""review command gRPC handler. `Create`/`Update` build the request DTO and validate it; a validation failure raises the matching sentinel (`err_grpc_validate_create_review` / `err_grpc_validate_update_review`). The proto `CreateReviewRequest.name` field is ignored, matching (only user_id/product_id/rating/comment are read)."""

from __future__ import annotations

from typing import Any

from pydantic import ValidationError

from pb.review import review_command_pb2_grpc, review_common_pb2
from pkg.logger.logger import Logger
from pkg.middleware import grpc_method
from service.review.handler.mapping import (
    fill_review_response,
    fill_review_response_delete_at,
)
from service.review.service.interfaces import ReviewCommandService
from service.review.service.service import SERVICE_NAME
from shared.domain.requests.review import (
    CreateReviewRequest,
    UpdateReviewRequest,
)
from shared.errors.review_errors import (
    err_grpc_invalid_id,
    err_grpc_validate_create_review,
    err_grpc_validate_update_review,
)


class ReviewCommandHandler(review_command_pb2_grpc.ReviewCommandServiceServicer):
    def __init__(self, service: ReviewCommandService, logger: Logger) -> None:
        self._service = service
        self.logger = logger

    @grpc_method("ReviewCommandService.Create", SERVICE_NAME)
    async def Create(self, request: Any, context: Any) -> Any:
        try:
            create_request = CreateReviewRequest(
                user_id=request.user_id,
                product_id=request.product_id,
                rating=request.rating,
                comment=request.comment,
            )
        except ValidationError as exc:
            raise err_grpc_validate_create_review from exc
        review = await self._service.create(create_request)
        response = review_common_pb2.ApiResponseReview(
            status="success", message="Successfully created review"
        )
        fill_review_response(response.data, review)
        return response

    @grpc_method("ReviewCommandService.Update", SERVICE_NAME)
    async def Update(self, request: Any, context: Any) -> Any:
        if request.review_id == 0:
            raise err_grpc_invalid_id
        try:
            update_request = UpdateReviewRequest(
                review_id=request.review_id,
                name=request.name,
                rating=request.rating,
                comment=request.comment,
            )
        except ValidationError as exc:
            raise err_grpc_validate_update_review from exc
        review = await self._service.update(update_request)
        response = review_common_pb2.ApiResponseReview(
            status="success", message="Successfully updated review"
        )
        fill_review_response(response.data, review)
        return response

    @grpc_method("ReviewCommandService.TrashedReview", SERVICE_NAME)
    async def TrashedReview(self, request: Any, context: Any) -> Any:
        if request.id == 0:
            raise err_grpc_invalid_id
        review = await self._service.trash(request.id)
        response = review_common_pb2.ApiResponseReviewDeleteAt(
            status="success", message="Successfully trashed review"
        )
        fill_review_response_delete_at(response.data, review)
        return response

    @grpc_method("ReviewCommandService.RestoreReview", SERVICE_NAME)
    async def RestoreReview(self, request: Any, context: Any) -> Any:
        if request.id == 0:
            raise err_grpc_invalid_id
        review = await self._service.restore(request.id)
        response = review_common_pb2.ApiResponseReviewDeleteAt(
            status="success", message="Successfully restored review"
        )
        fill_review_response_delete_at(response.data, review)
        return response

    @grpc_method("ReviewCommandService.DeleteReviewPermanent", SERVICE_NAME)
    async def DeleteReviewPermanent(self, request: Any, context: Any) -> Any:
        if request.id == 0:
            raise err_grpc_invalid_id
        await self._service.delete_permanent(request.id)
        return review_common_pb2.ApiResponseReviewDelete(
            status="success",
            message="Successfully deleted review permanently",
        )

    @grpc_method("ReviewCommandService.RestoreAllReview", SERVICE_NAME)
    async def RestoreAllReview(self, request: Any, context: Any) -> Any:
        await self._service.restore_all()
        return review_common_pb2.ApiResponseReviewAll(
            status="success", message="Successfully restored all reviews"
        )

    @grpc_method("ReviewCommandService.DeleteAllReviewPermanent", SERVICE_NAME)
    async def DeleteAllReviewPermanent(self, request: Any, context: Any) -> Any:
        await self._service.delete_all()
        return review_common_pb2.ApiResponseReviewAll(
            status="success",
            message="Successfully deleted all reviews permanently",
        )


__all__ = ["ReviewCommandHandler"]

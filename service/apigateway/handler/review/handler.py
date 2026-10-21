"""Gateway review handler: REST <-> review gRPC. Only transport concerns live here: build the proto request, call the domain over gRPC, convert a gRPC failure back to its original AppError, and map the proto response to the shared response envelope. No SQL, no business rules. Like the other domains, deliberately does not cache in the gateway. gateway review handler caches under its own `review:` namespace and invalidates on every mutation; drops that layer, so every request goes straight to the review service, which serves/invalidates its own cache. `Create` takes the author id from the JWT (`request.state.user_id`, set by the auth middleware) and never from the body — a missing subject is a 401 (`err_unauthorized`), matching `user_id` context check. `Update` uses the path id and ignores the body's `review_id`/`name`,. the gateway's `strconv.Atoi` guards on the product/merchant/id path params (400 "Invalid Product ID" / "Invalid Merchant ID" / "Invalid ID") are only reachable for a non-numeric segment; FastAPI's typed `int` path params reject those with 422 before this handler runs, so those exact 400 messages are unreachable in. Numeric `0`/negative ids pass through,, and the gRPC handler's own `id == 0` guard answers 400 `invalid ID`."""

from __future__ import annotations

import grpc
from google.protobuf import empty_pb2

from pb.review import (
    review_command_pb2,
    review_command_pb2_grpc,
    review_common_pb2,
    review_query_pb2,
    review_query_pb2_grpc,
)
from service.apigateway.app.client import ServiceConnections
from shared.domain.response.responses import ApiResponse, APIResponsePagination
from shared.domain.response.review import (
    ReviewResponse,
    ReviewResponseDeleteAt,
    ReviewsDetailResponse,
)
from shared.errors import err_unauthorized, parse_grpc_error
from shared.mapper.review import (
    to_api_response_pagination_review,
    to_api_response_pagination_review_delete_at,
    to_api_response_pagination_reviews_detail,
    to_api_response_review,
    to_api_response_review_all,
    to_api_response_review_delete,
    to_api_response_review_delete_at,
)

RPC_TIMEOUT = 30.0


def normalize_pagination(page: int, page_size: int) -> tuple[int, int]:
    """Gateway-side clamping."""
    if page <= 0:
        page = 1
    if page_size <= 0:
        page_size = 10
    return page, page_size


class ReviewHandler:
    def __init__(self, connections: ServiceConnections) -> None:
        channel = connections.channel("review")
        self._query = review_query_pb2_grpc.ReviewQueryServiceStub(channel)
        self._command = review_command_pb2_grpc.ReviewCommandServiceStub(channel)

    # ---- query ----

    async def find_all(
        self, page: int, page_size: int, search: str
    ) -> APIResponsePagination[list[ReviewResponse]]:
        page, page_size = normalize_pagination(page, page_size)
        request = review_query_pb2.FindAllReviewRequest(page=page, page_size=page_size, search=search or "")
        try:
            response = await self._query.FindAll(request, timeout=RPC_TIMEOUT)
        except grpc.aio.AioRpcError as exc:
            raise parse_grpc_error(exc) from exc
        return to_api_response_pagination_review(response)

    async def find_by_product(
        self, product_id: int, page: int, page_size: int, search: str
    ) -> APIResponsePagination[list[ReviewsDetailResponse]]:
        page, page_size = normalize_pagination(page, page_size)
        request = review_query_pb2.FindAllReviewProductRequest(
            product_id=product_id, page=page, page_size=page_size, search=search or ""
        )
        try:
            response = await self._query.FindByProduct(request, timeout=RPC_TIMEOUT)
        except grpc.aio.AioRpcError as exc:
            raise parse_grpc_error(exc) from exc
        return to_api_response_pagination_reviews_detail(response)

    async def find_by_merchant(
        self, merchant_id: int, page: int, page_size: int, search: str
    ) -> APIResponsePagination[list[ReviewsDetailResponse]]:
        page, page_size = normalize_pagination(page, page_size)
        request = review_query_pb2.FindAllReviewMerchantRequest(
            merchant_id=merchant_id,
            page=page,
            page_size=page_size,
            search=search or "",
        )
        try:
            response = await self._query.FindByMerchant(request, timeout=RPC_TIMEOUT)
        except grpc.aio.AioRpcError as exc:
            raise parse_grpc_error(exc) from exc
        return to_api_response_pagination_reviews_detail(response)

    async def find_by_active(
        self, page: int, page_size: int, search: str
    ) -> APIResponsePagination[list[ReviewResponseDeleteAt]]:
        page, page_size = normalize_pagination(page, page_size)
        request = review_query_pb2.FindAllReviewRequest(page=page, page_size=page_size, search=search or "")
        try:
            response = await self._query.FindByActive(request, timeout=RPC_TIMEOUT)
        except grpc.aio.AioRpcError as exc:
            raise parse_grpc_error(exc) from exc
        return to_api_response_pagination_review_delete_at(response)

    async def find_by_trashed(
        self, page: int, page_size: int, search: str
    ) -> APIResponsePagination[list[ReviewResponseDeleteAt]]:
        page, page_size = normalize_pagination(page, page_size)
        request = review_query_pb2.FindAllReviewRequest(page=page, page_size=page_size, search=search or "")
        try:
            response = await self._query.FindByTrashed(request, timeout=RPC_TIMEOUT)
        except grpc.aio.AioRpcError as exc:
            raise parse_grpc_error(exc) from exc
        return to_api_response_pagination_review_delete_at(response)

    # ---- command ----

    async def create(
        self, user_id: int | None, product_id: int, rating: int, comment: str
    ) -> ApiResponse[ReviewResponse]:
        if not user_id or user_id <= 0:
            raise err_unauthorized
        request = review_command_pb2.CreateReviewRequest(
            user_id=user_id,
            product_id=product_id,
            comment=comment,
            rating=rating,
        )
        try:
            response = await self._command.Create(request, timeout=RPC_TIMEOUT)
        except grpc.aio.AioRpcError as exc:
            raise parse_grpc_error(exc) from exc
        return to_api_response_review(response)

    async def update(self, review_id: int, rating: int, comment: str) -> ApiResponse[ReviewResponse]:
        request = review_command_pb2.UpdateReviewRequest(
            review_id=review_id,
            comment=comment,
            rating=rating,
        )
        try:
            response = await self._command.Update(request, timeout=RPC_TIMEOUT)
        except grpc.aio.AioRpcError as exc:
            raise parse_grpc_error(exc) from exc
        return to_api_response_review(response)

    async def trash(self, review_id: int) -> ApiResponse[ReviewResponseDeleteAt]:
        request = review_common_pb2.FindByIdReviewRequest(id=review_id)
        try:
            response = await self._command.TrashedReview(request, timeout=RPC_TIMEOUT)
        except grpc.aio.AioRpcError as exc:
            raise parse_grpc_error(exc) from exc
        return to_api_response_review_delete_at(response)

    async def restore(self, review_id: int) -> ApiResponse[ReviewResponseDeleteAt]:
        request = review_common_pb2.FindByIdReviewRequest(id=review_id)
        try:
            response = await self._command.RestoreReview(request, timeout=RPC_TIMEOUT)
        except grpc.aio.AioRpcError as exc:
            raise parse_grpc_error(exc) from exc
        return to_api_response_review_delete_at(response)

    async def delete_permanent(self, review_id: int) -> ApiResponse[None]:
        request = review_common_pb2.FindByIdReviewRequest(id=review_id)
        try:
            response = await self._command.DeleteReviewPermanent(request, timeout=RPC_TIMEOUT)
        except grpc.aio.AioRpcError as exc:
            raise parse_grpc_error(exc) from exc
        return to_api_response_review_delete(response)

    async def restore_all(self) -> ApiResponse[None]:
        try:
            response = await self._command.RestoreAllReview(empty_pb2.Empty(), timeout=RPC_TIMEOUT)
        except grpc.aio.AioRpcError as exc:
            raise parse_grpc_error(exc) from exc
        return to_api_response_review_all(response)

    async def delete_all_permanent(self) -> ApiResponse[None]:
        try:
            response = await self._command.DeleteAllReviewPermanent(empty_pb2.Empty(), timeout=RPC_TIMEOUT)
        except grpc.aio.AioRpcError as exc:
            raise parse_grpc_error(exc) from exc
        return to_api_response_review_all(response)


__all__ = ["ReviewHandler", "normalize_pagination"]

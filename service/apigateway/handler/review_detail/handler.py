"""Gateway review_detail handler: REST <-> review_detail gRPC. Only transport concerns live here: build the proto request, call the domain over gRPC, convert a gRPC failure back to its original AppError, and map the proto response to the shared response envelope. No SQL, no business rules. the gateway's form validation is replicated here: a present-but-invalid `review_id` (non-numeric or `<= 0`) is 400 `"Invalid Review ID"`, `type` and `caption` must be non-empty, and `url` is either an uploaded file (`pkg.upload_image` -> `uploads/review_detail`) or, when no file is sent, a plain URL string. reads both from the same `url` form field, so the route hands the raw form value here."""

from __future__ import annotations

from typing import Any

import grpc

from pb.review import review_query_pb2
from pb.review_detail import (
    review_detail_command_pb2,
    review_detail_command_pb2_grpc,
    review_detail_common_pb2,
    review_detail_query_pb2_grpc,
)
from pkg.upload_image import ImageUpload
from service.apigateway.app.client import ServiceConnections
from shared.errors import new_bad_request_error, parse_grpc_error
from shared.mapper.review_detail import (
    to_api_response_pagination_review_detail,
    to_api_response_pagination_review_detail_delete_at,
    to_api_response_review_detail,
    to_api_response_review_detail_all,
    to_api_response_review_detail_delete,
    to_api_response_review_detail_delete_at,
)

RPC_TIMEOUT = 30.0

_UPLOAD_DIR = "uploads/review_detail"


def normalize_pagination(page: int, page_size: int) -> tuple[int, int]:
    """Gateway-side clamping."""
    if page <= 0:
        page = 1
    if page_size <= 0:
        page_size = 10
    return page, page_size


def require_positive_id(review_detail_id: int) -> None:
    """Reject a non-positive path id before the gRPC hop (command routes). The query `find_by_id` route deliberately does NOT use this — gateway `FindById` forwards `id == 0` to the gRPC handler, whose own `FindById` guards `id == 0` and returns 400 `invalid ID`."""
    if review_detail_id <= 0:
        raise new_bad_request_error("Invalid ID")


def parse_review_id(raw: Any) -> int:
    """An absent/empty value yields 0 (only validates when the field is present); a non-numeric or `<= 0` value is 400 `"Invalid Review ID"`."""
    if raw is None or raw == "":
        return 0
    try:
        review_id = int(raw)
    except (TypeError, ValueError):
        raise new_bad_request_error("Invalid Review ID") from None
    if review_id <= 0:
        raise new_bad_request_error("Invalid Review ID")
    return review_id


class ReviewDetailHandler:
    def __init__(self, connections: ServiceConnections, upload: ImageUpload) -> None:
        channel = connections.channel("review_detail")
        self._query = review_detail_query_pb2_grpc.ReviewDetailQueryServiceStub(channel)
        self._command = review_detail_command_pb2_grpc.ReviewDetailCommandServiceStub(
            channel
        )
        self._upload = upload

    async def _resolve_url(self, url: Any) -> str:
        """Uploaded file wins; otherwise a plain URL string; else empty."""
        if url is None:
            return ""
        if isinstance(url, str):
            return url
        return await self._upload.process_image_upload(_UPLOAD_DIR, url, False)

    # ---- query ----

    async def find_all(
        self, page: int, page_size: int, search: str
    ):
        page, page_size = normalize_pagination(page, page_size)
        request = review_query_pb2.FindAllReviewRequest(
            page=page, page_size=page_size, search=search or ""
        )
        try:
            response = await self._query.FindAll(request, timeout=RPC_TIMEOUT)
        except grpc.aio.AioRpcError as exc:
            raise parse_grpc_error(exc) from exc
        return to_api_response_pagination_review_detail(response)

    async def find_by_id(self, review_detail_id: int):
        # No id guard — forwards 0 to gRPC, whose FindById guards `id == 0` and
        # returns 400 `invalid ID`,.
        request = review_detail_common_pb2.FindByIdReviewDetailRequest(
            id=review_detail_id
        )
        try:
            response = await self._query.FindById(request, timeout=RPC_TIMEOUT)
        except grpc.aio.AioRpcError as exc:
            raise parse_grpc_error(exc) from exc
        return to_api_response_review_detail(response)

    async def find_by_active(
        self, page: int, page_size: int, search: str
    ):
        page, page_size = normalize_pagination(page, page_size)
        request = review_query_pb2.FindAllReviewRequest(
            page=page, page_size=page_size, search=search or ""
        )
        try:
            response = await self._query.FindByActive(request, timeout=RPC_TIMEOUT)
        except grpc.aio.AioRpcError as exc:
            raise parse_grpc_error(exc) from exc
        return to_api_response_pagination_review_detail_delete_at(response)

    async def find_by_trashed(
        self, page: int, page_size: int, search: str
    ):
        page, page_size = normalize_pagination(page, page_size)
        request = review_query_pb2.FindAllReviewRequest(
            page=page, page_size=page_size, search=search or ""
        )
        try:
            response = await self._query.FindByTrashed(request, timeout=RPC_TIMEOUT)
        except grpc.aio.AioRpcError as exc:
            raise parse_grpc_error(exc) from exc
        return to_api_response_pagination_review_detail_delete_at(response)

    # ---- command ----

    async def create(
        self,
        review_id_raw: Any,
        type: str,
        url: Any,
        caption: str | None,
    ):
        review_id = parse_review_id(review_id_raw)
        if not type or not type.strip():
            raise new_bad_request_error("Type is required")
        if not caption or not caption.strip():
            raise new_bad_request_error("Caption is required")
        resolved_url = await self._resolve_url(url)
        request = review_detail_command_pb2.CreateReviewDetailRequest(
            review_id=review_id, type=type, url=resolved_url, caption=caption
        )
        try:
            response = await self._command.Create(request, timeout=RPC_TIMEOUT)
        except grpc.aio.AioRpcError as exc:
            raise parse_grpc_error(exc) from exc
        return to_api_response_review_detail(response)

    async def update(
        self, review_detail_id: int, type: str, url: Any, caption: str | None
    ):
        require_positive_id(review_detail_id)
        if not type or not type.strip():
            raise new_bad_request_error("Type is required")
        if not caption or not caption.strip():
            raise new_bad_request_error("Caption is required")
        resolved_url = await self._resolve_url(url)
        request = review_detail_command_pb2.UpdateReviewDetailRequest(
            review_detail_id=review_detail_id,
            type=type,
            url=resolved_url,
            caption=caption,
        )
        try:
            response = await self._command.Update(request, timeout=RPC_TIMEOUT)
        except grpc.aio.AioRpcError as exc:
            raise parse_grpc_error(exc) from exc
        return to_api_response_review_detail(response)

    async def trash(self, review_detail_id: int):
        require_positive_id(review_detail_id)
        request = review_detail_common_pb2.FindByIdReviewDetailRequest(
            id=review_detail_id
        )
        try:
            response = await self._command.TrashedReviewDetail(
                request, timeout=RPC_TIMEOUT
            )
        except grpc.aio.AioRpcError as exc:
            raise parse_grpc_error(exc) from exc
        return to_api_response_review_detail_delete_at(response)

    async def restore(self, review_detail_id: int):
        require_positive_id(review_detail_id)
        request = review_detail_common_pb2.FindByIdReviewDetailRequest(
            id=review_detail_id
        )
        try:
            response = await self._command.RestoreReviewDetail(
                request, timeout=RPC_TIMEOUT
            )
        except grpc.aio.AioRpcError as exc:
            raise parse_grpc_error(exc) from exc
        return to_api_response_review_detail_delete_at(response)

    async def delete_permanent(self, review_detail_id: int):
        require_positive_id(review_detail_id)
        request = review_detail_common_pb2.FindByIdReviewDetailRequest(
            id=review_detail_id
        )
        try:
            response = await self._command.DeleteReviewDetailPermanent(
                request, timeout=RPC_TIMEOUT
            )
        except grpc.aio.AioRpcError as exc:
            raise parse_grpc_error(exc) from exc
        return to_api_response_review_detail_delete(response)

    async def restore_all(self):
        try:
            response = await self._command.RestoreAllReviewDetail(
                _empty(), timeout=RPC_TIMEOUT
            )
        except grpc.aio.AioRpcError as exc:
            raise parse_grpc_error(exc) from exc
        return to_api_response_review_detail_all(response)

    async def delete_all_permanent(self):
        try:
            response = await self._command.DeleteAllReviewDetailPermanent(
                _empty(), timeout=RPC_TIMEOUT
            )
        except grpc.aio.AioRpcError as exc:
            raise parse_grpc_error(exc) from exc
        return to_api_response_review_detail_all(response)


def _empty():
    from google.protobuf import empty_pb2

    return empty_pb2.Empty()


__all__ = [
    "ReviewDetailHandler",
    "normalize_pagination",
    "parse_review_id",
    "require_positive_id",
]

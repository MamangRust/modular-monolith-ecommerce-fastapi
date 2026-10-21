"""Gateway banner handler: REST <-> banner gRPC. Only transport concerns live here: build the proto request, call the domain over gRPC, convert a gRPC failure back to its original AppError, and map the proto response to the shared response envelope. No SQL, no business rules. Like the banner gateway (and unlike user), a non-positive path id is rejected before the gRPC hop with a 400 `"Invalid ID"`."""

from __future__ import annotations

import grpc

from pb.banner import (
    banner_command_pb2,
    banner_command_pb2_grpc,
    banner_common_pb2,
    banner_query_pb2,
    banner_query_pb2_grpc,
)
from service.apigateway.app.client import ServiceConnections
from shared.domain.response.banner import (
    BannerResponse,
    BannerResponseDeleteAt,
)
from shared.domain.response.responses import ApiResponse, APIResponsePagination
from shared.errors import new_bad_request_error, parse_grpc_error
from shared.mapper.banner import (
    to_api_response_banner,
    to_api_response_banner_all,
    to_api_response_banner_delete,
    to_api_response_banner_delete_at,
    to_api_response_pagination_banner,
    to_api_response_pagination_banner_delete_at,
)

RPC_TIMEOUT = 30.0


def normalize_pagination(page: int, page_size: int) -> tuple[int, int]:
    """Gateway-side clamping."""
    if page <= 0:
        page = 1
    if page_size <= 0:
        page_size = 10
    return page, page_size


def require_positive_id(banner_id: int) -> None:
    """Reject a non-positive path id before the gRPC hop. parses the path param with `strconv.Atoi` and returns `NewHTTPError(400, "Invalid ID")` when it fails or is <= 0."""
    if banner_id <= 0:
        raise new_bad_request_error("Invalid ID")


class BannerHandler:
    def __init__(self, connections: ServiceConnections) -> None:
        channel = connections.channel("banner")
        self._query = banner_query_pb2_grpc.BannerQueryServiceStub(channel)
        self._command = banner_command_pb2_grpc.BannerCommandServiceStub(channel)

    # ---- query ----

    async def find_all(
        self, page: int, page_size: int, search: str
    ) -> APIResponsePagination[list[BannerResponse]]:
        page, page_size = normalize_pagination(page, page_size)
        request = banner_query_pb2.FindAllBannerRequest(
            page=page, page_size=page_size, search=search or ""
        )
        try:
            response = await self._query.FindAll(request, timeout=RPC_TIMEOUT)
        except grpc.aio.AioRpcError as exc:
            raise parse_grpc_error(exc) from exc
        return to_api_response_pagination_banner(response)

    async def find_by_id(self, banner_id: int) -> ApiResponse[BannerResponse]:
        require_positive_id(banner_id)
        request = banner_common_pb2.FindByIdBannerRequest(id=banner_id)
        try:
            response = await self._query.FindById(request, timeout=RPC_TIMEOUT)
        except grpc.aio.AioRpcError as exc:
            raise parse_grpc_error(exc) from exc
        return to_api_response_banner(response)

    async def find_by_active(
        self, page: int, page_size: int, search: str
    ) -> APIResponsePagination[list[BannerResponseDeleteAt]]:
        page, page_size = normalize_pagination(page, page_size)
        request = banner_query_pb2.FindAllBannerRequest(
            page=page, page_size=page_size, search=search or ""
        )
        try:
            response = await self._query.FindByActive(request, timeout=RPC_TIMEOUT)
        except grpc.aio.AioRpcError as exc:
            raise parse_grpc_error(exc) from exc
        return to_api_response_pagination_banner_delete_at(response)

    async def find_by_trashed(
        self, page: int, page_size: int, search: str
    ) -> APIResponsePagination[list[BannerResponseDeleteAt]]:
        page, page_size = normalize_pagination(page, page_size)
        request = banner_query_pb2.FindAllBannerRequest(
            page=page, page_size=page_size, search=search or ""
        )
        try:
            response = await self._query.FindByTrashed(request, timeout=RPC_TIMEOUT)
        except grpc.aio.AioRpcError as exc:
            raise parse_grpc_error(exc) from exc
        return to_api_response_pagination_banner_delete_at(response)

    # ---- command ----

    async def create(
        self,
        name: str,
        start_date: str,
        end_date: str,
        start_time: str,
        end_time: str,
        is_active: bool,
    ) -> ApiResponse[BannerResponse]:
        request = banner_command_pb2.CreateBannerRequest(
            name=name,
            start_date=start_date,
            end_date=end_date,
            start_time=start_time,
            end_time=end_time,
            is_active=is_active,
        )
        try:
            response = await self._command.Create(request, timeout=RPC_TIMEOUT)
        except grpc.aio.AioRpcError as exc:
            raise parse_grpc_error(exc) from exc
        return to_api_response_banner(response)

    async def update(
        self,
        banner_id: int,
        name: str,
        start_date: str,
        end_date: str,
        start_time: str,
        end_time: str,
        is_active: bool,
    ) -> ApiResponse[BannerResponse]:
        require_positive_id(banner_id)
        request = banner_command_pb2.UpdateBannerRequest(
            banner_id=banner_id,
            name=name,
            start_date=start_date,
            end_date=end_date,
            start_time=start_time,
            end_time=end_time,
            is_active=is_active,
        )
        try:
            response = await self._command.Update(request, timeout=RPC_TIMEOUT)
        except grpc.aio.AioRpcError as exc:
            raise parse_grpc_error(exc) from exc
        return to_api_response_banner(response)

    async def trash(self, banner_id: int) -> ApiResponse[BannerResponseDeleteAt]:
        require_positive_id(banner_id)
        request = banner_common_pb2.FindByIdBannerRequest(id=banner_id)
        try:
            response = await self._command.Trash(request, timeout=RPC_TIMEOUT)
        except grpc.aio.AioRpcError as exc:
            raise parse_grpc_error(exc) from exc
        return to_api_response_banner_delete_at(response)

    async def restore(self, banner_id: int) -> ApiResponse[BannerResponseDeleteAt]:
        require_positive_id(banner_id)
        request = banner_common_pb2.FindByIdBannerRequest(id=banner_id)
        try:
            response = await self._command.Restore(request, timeout=RPC_TIMEOUT)
        except grpc.aio.AioRpcError as exc:
            raise parse_grpc_error(exc) from exc
        return to_api_response_banner_delete_at(response)

    async def delete_permanent(self, banner_id: int) -> ApiResponse[None]:
        require_positive_id(banner_id)
        request = banner_common_pb2.FindByIdBannerRequest(id=banner_id)
        try:
            response = await self._command.DeletePermanent(request, timeout=RPC_TIMEOUT)
        except grpc.aio.AioRpcError as exc:
            raise parse_grpc_error(exc) from exc
        return to_api_response_banner_delete(response)

    async def restore_all(self) -> ApiResponse[None]:
        try:
            response = await self._command.RestoreAll(_empty(), timeout=RPC_TIMEOUT)
        except grpc.aio.AioRpcError as exc:
            raise parse_grpc_error(exc) from exc
        return to_api_response_banner_all(response)

    async def delete_all_permanent(self) -> ApiResponse[None]:
        try:
            response = await self._command.DeleteAll(_empty(), timeout=RPC_TIMEOUT)
        except grpc.aio.AioRpcError as exc:
            raise parse_grpc_error(exc) from exc
        return to_api_response_banner_all(response)


def _empty():
    from google.protobuf import empty_pb2

    return empty_pb2.Empty()


__all__ = ["BannerHandler", "normalize_pagination", "require_positive_id"]

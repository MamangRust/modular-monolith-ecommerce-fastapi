"""Gateway role handler: REST <-> role gRPC. Only transport concerns live here: build the proto request, call the domain over gRPC, convert a gRPC failure back to its original AppError, and map the proto response to the shared response envelope. No SQL, no business rules."""

from __future__ import annotations

import grpc

from pb.role import (
    role_command_pb2,
    role_command_pb2_grpc,
    role_common_pb2,
    role_query_pb2,
    role_query_pb2_grpc,
)
from service.apigateway.app.client import ServiceConnections
from shared.domain.response.responses import ApiResponse, APIResponsePagination
from shared.domain.response.role import RoleResponse, RoleResponseDeleteAt
from shared.errors import new_bad_request_error, parse_grpc_error
from shared.mapper.role import (
    to_api_response_pagination_role,
    to_api_response_pagination_role_delete_at,
    to_api_response_role,
    to_api_response_role_all,
    to_api_response_role_delete,
    to_api_responses_role,
)

RPC_TIMEOUT = 30.0


def normalize_pagination(page: int, page_size: int) -> tuple[int, int]:
    """Gateway-side clamping."""
    if page <= 0:
        page = 1
    if page_size <= 0:
        page_size = 10
    return page, page_size


def require_positive_id(value: int, field: str) -> None:
    """Reject a non-positive path id before the gRPC hop. parses the path param with `strconv.Atoi` and returns `NewBadRequestError("<field> is required")` when it fails or is <= 0, so a bad id is a gateway 400 with `type=BAD_REQUEST` rather than the domain's `Invalid... ID` gRPC error."""
    if value <= 0:
        raise new_bad_request_error(f"{field} is required")


class RoleHandler:
    def __init__(self, connections: ServiceConnections) -> None:
        channel = connections.channel("role")
        self._query = role_query_pb2_grpc.RoleQueryServiceStub(channel)
        self._command = role_command_pb2_grpc.RoleCommandServiceStub(channel)

    # ---- query ----

    async def find_all(
        self, page: int, page_size: int, search: str
    ) -> APIResponsePagination[list[RoleResponse]]:
        page, page_size = normalize_pagination(page, page_size)
        request = role_query_pb2.FindAllRoleRequest(
            page=page, page_size=page_size, search=search or ""
        )
        try:
            response = await self._query.FindAllRole(request, timeout=RPC_TIMEOUT)
        except grpc.aio.AioRpcError as exc:
            raise parse_grpc_error(exc) from exc
        return to_api_response_pagination_role(response)

    async def find_by_id(self, role_id: int) -> ApiResponse[RoleResponse]:
        require_positive_id(role_id, "id")
        request = role_common_pb2.FindByIdRoleRequest(role_id=role_id)
        try:
            response = await self._query.FindByIdRole(request, timeout=RPC_TIMEOUT)
        except grpc.aio.AioRpcError as exc:
            raise parse_grpc_error(exc) from exc
        return to_api_response_role(response)

    async def find_by_active(
        self, page: int, page_size: int, search: str
    ) -> APIResponsePagination[list[RoleResponseDeleteAt]]:
        page, page_size = normalize_pagination(page, page_size)
        request = role_query_pb2.FindAllRoleRequest(
            page=page, page_size=page_size, search=search or ""
        )
        try:
            response = await self._query.FindByActive(request, timeout=RPC_TIMEOUT)
        except grpc.aio.AioRpcError as exc:
            raise parse_grpc_error(exc) from exc
        return to_api_response_pagination_role_delete_at(response)

    async def find_by_trashed(
        self, page: int, page_size: int, search: str
    ) -> APIResponsePagination[list[RoleResponseDeleteAt]]:
        page, page_size = normalize_pagination(page, page_size)
        request = role_query_pb2.FindAllRoleRequest(
            page=page, page_size=page_size, search=search or ""
        )
        try:
            response = await self._query.FindByTrashed(request, timeout=RPC_TIMEOUT)
        except grpc.aio.AioRpcError as exc:
            raise parse_grpc_error(exc) from exc
        return to_api_response_pagination_role_delete_at(response)

    async def find_by_user_id(self, user_id: int) -> ApiResponse[list[RoleResponse]]:
        require_positive_id(user_id, "user_id")
        request = role_query_pb2.FindByIdUserRoleRequest(user_id=user_id)
        try:
            response = await self._query.FindByUserId(request, timeout=RPC_TIMEOUT)
        except grpc.aio.AioRpcError as exc:
            raise parse_grpc_error(exc) from exc
        return to_api_responses_role(response)

    # ---- command ----

    async def create(self, name: str) -> ApiResponse[RoleResponse]:
        request = role_command_pb2.CreateRoleRequest(name=name)
        try:
            response = await self._command.CreateRole(request, timeout=RPC_TIMEOUT)
        except grpc.aio.AioRpcError as exc:
            raise parse_grpc_error(exc) from exc
        return to_api_response_role(response)

    async def update(self, role_id: int, name: str) -> ApiResponse[RoleResponse]:
        require_positive_id(role_id, "id")
        request = role_command_pb2.UpdateRoleRequest(id=role_id, name=name)
        try:
            response = await self._command.UpdateRole(request, timeout=RPC_TIMEOUT)
        except grpc.aio.AioRpcError as exc:
            raise parse_grpc_error(exc) from exc
        return to_api_response_role(response)

    async def trash(self, role_id: int) -> ApiResponse[RoleResponse]:
        require_positive_id(role_id, "id")
        request = role_common_pb2.FindByIdRoleRequest(role_id=role_id)
        try:
            response = await self._command.TrashedRole(request, timeout=RPC_TIMEOUT)
        except grpc.aio.AioRpcError as exc:
            raise parse_grpc_error(exc) from exc
        return to_api_response_role(response)

    async def restore(self, role_id: int) -> ApiResponse[RoleResponse]:
        require_positive_id(role_id, "id")
        request = role_common_pb2.FindByIdRoleRequest(role_id=role_id)
        try:
            response = await self._command.RestoreRole(request, timeout=RPC_TIMEOUT)
        except grpc.aio.AioRpcError as exc:
            raise parse_grpc_error(exc) from exc
        return to_api_response_role(response)

    async def delete_permanent(self, role_id: int) -> ApiResponse[None]:
        require_positive_id(role_id, "id")
        request = role_common_pb2.FindByIdRoleRequest(role_id=role_id)
        try:
            response = await self._command.DeleteRolePermanent(request, timeout=RPC_TIMEOUT)
        except grpc.aio.AioRpcError as exc:
            raise parse_grpc_error(exc) from exc
        return to_api_response_role_delete(response)

    async def restore_all(self) -> ApiResponse[None]:
        try:
            response = await self._command.RestoreAllRole(_empty(), timeout=RPC_TIMEOUT)
        except grpc.aio.AioRpcError as exc:
            raise parse_grpc_error(exc) from exc
        return to_api_response_role_all(response)

    async def delete_all_permanent(self) -> ApiResponse[None]:
        try:
            response = await self._command.DeleteAllRolePermanent(
                _empty(), timeout=RPC_TIMEOUT
            )
        except grpc.aio.AioRpcError as exc:
            raise parse_grpc_error(exc) from exc
        return to_api_response_role_all(response)


def _empty():
    from google.protobuf import empty_pb2

    return empty_pb2.Empty()


__all__ = ["RoleHandler", "normalize_pagination"]

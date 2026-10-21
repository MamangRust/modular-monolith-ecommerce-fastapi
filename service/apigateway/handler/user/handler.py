"""Gateway user handler: REST <-> user gRPC. Only transport concerns live here: build the proto request, call the domain over gRPC, convert a gRPC failure back to its original AppError, and map the proto response to the shared response envelope. No SQL, no business rules. Unlike role, the user gateway does not clamp path ids to positive values (it only checks `strconv.Atoi`), so leaves that to the domain handler, which rejects `id <= 0` with "Invalid user ID"."""

from __future__ import annotations

import grpc

from pb.user import (
    user_command_pb2,
    user_command_pb2_grpc,
    user_common_pb2,
    user_query_pb2,
    user_query_pb2_grpc,
)
from service.apigateway.app.client import ServiceConnections
from shared.domain.response.responses import ApiResponse, APIResponsePagination
from shared.domain.response.user import UserResponse, UserResponseDeleteAt
from shared.errors import parse_grpc_error
from shared.mapper.user import (
    to_api_response_pagination_user,
    to_api_response_pagination_user_delete_at,
    to_api_response_user,
    to_api_response_user_all,
    to_api_response_user_delete,
    to_api_response_user_delete_at,
)

RPC_TIMEOUT = 30.0


def normalize_pagination(page: int, page_size: int) -> tuple[int, int]:
    """Gateway-side clamping."""
    if page <= 0:
        page = 1
    if page_size <= 0:
        page_size = 10
    return page, page_size


class UserHandler:
    def __init__(self, connections: ServiceConnections) -> None:
        channel = connections.channel("user")
        self._query = user_query_pb2_grpc.UserQueryServiceStub(channel)
        self._command = user_command_pb2_grpc.UserCommandServiceStub(channel)

    # ---- query ----

    async def find_all(
        self, page: int, page_size: int, search: str
    ) -> APIResponsePagination[list[UserResponse]]:
        page, page_size = normalize_pagination(page, page_size)
        request = user_query_pb2.FindAllUserRequest(
            page=page, page_size=page_size, search=search or ""
        )
        try:
            response = await self._query.FindAll(request, timeout=RPC_TIMEOUT)
        except grpc.aio.AioRpcError as exc:
            raise parse_grpc_error(exc) from exc
        return to_api_response_pagination_user(response)

    async def find_by_id(self, user_id: int) -> ApiResponse[UserResponse]:
        request = user_common_pb2.FindByIdUserRequest(id=user_id)
        try:
            response = await self._query.FindById(request, timeout=RPC_TIMEOUT)
        except grpc.aio.AioRpcError as exc:
            raise parse_grpc_error(exc) from exc
        return to_api_response_user(response)

    async def find_by_active(
        self, page: int, page_size: int, search: str
    ) -> APIResponsePagination[list[UserResponseDeleteAt]]:
        page, page_size = normalize_pagination(page, page_size)
        request = user_query_pb2.FindAllUserRequest(
            page=page, page_size=page_size, search=search or ""
        )
        try:
            response = await self._query.FindByActive(request, timeout=RPC_TIMEOUT)
        except grpc.aio.AioRpcError as exc:
            raise parse_grpc_error(exc) from exc
        return to_api_response_pagination_user_delete_at(response)

    async def find_by_trashed(
        self, page: int, page_size: int, search: str
    ) -> APIResponsePagination[list[UserResponseDeleteAt]]:
        page, page_size = normalize_pagination(page, page_size)
        request = user_query_pb2.FindAllUserRequest(
            page=page, page_size=page_size, search=search or ""
        )
        try:
            response = await self._query.FindByTrashed(request, timeout=RPC_TIMEOUT)
        except grpc.aio.AioRpcError as exc:
            raise parse_grpc_error(exc) from exc
        return to_api_response_pagination_user_delete_at(response)

    # ---- command ----

    async def create(
        self,
        firstname: str,
        lastname: str,
        email: str,
        password: str,
        confirm_password: str,
    ) -> ApiResponse[UserResponse]:
        request = user_command_pb2.CreateUserRequest(
            firstname=firstname,
            lastname=lastname,
            email=email,
            password=password,
            confirm_password=confirm_password,
        )
        try:
            response = await self._command.Create(request, timeout=RPC_TIMEOUT)
        except grpc.aio.AioRpcError as exc:
            raise parse_grpc_error(exc) from exc
        return to_api_response_user(response)

    async def update(
        self,
        user_id: int,
        firstname: str,
        lastname: str,
        email: str,
        password: str,
        confirm_password: str,
    ) -> ApiResponse[UserResponse]:
        request = user_command_pb2.UpdateUserRequest(
            id=user_id,
            firstname=firstname,
            lastname=lastname,
            email=email,
            password=password,
            confirm_password=confirm_password,
        )
        try:
            response = await self._command.Update(request, timeout=RPC_TIMEOUT)
        except grpc.aio.AioRpcError as exc:
            raise parse_grpc_error(exc) from exc
        return to_api_response_user(response)

    async def trash(self, user_id: int) -> ApiResponse[UserResponseDeleteAt]:
        request = user_common_pb2.FindByIdUserRequest(id=user_id)
        try:
            response = await self._command.TrashedUser(request, timeout=RPC_TIMEOUT)
        except grpc.aio.AioRpcError as exc:
            raise parse_grpc_error(exc) from exc
        return to_api_response_user_delete_at(response)

    async def restore(self, user_id: int) -> ApiResponse[UserResponseDeleteAt]:
        request = user_common_pb2.FindByIdUserRequest(id=user_id)
        try:
            response = await self._command.RestoreUser(request, timeout=RPC_TIMEOUT)
        except grpc.aio.AioRpcError as exc:
            raise parse_grpc_error(exc) from exc
        return to_api_response_user_delete_at(response)

    async def delete_permanent(self, user_id: int) -> ApiResponse[None]:
        request = user_common_pb2.FindByIdUserRequest(id=user_id)
        try:
            response = await self._command.DeleteUserPermanent(request, timeout=RPC_TIMEOUT)
        except grpc.aio.AioRpcError as exc:
            raise parse_grpc_error(exc) from exc
        return to_api_response_user_delete(response)

    async def restore_all(self) -> ApiResponse[None]:
        try:
            response = await self._command.RestoreAllUser(_empty(), timeout=RPC_TIMEOUT)
        except grpc.aio.AioRpcError as exc:
            raise parse_grpc_error(exc) from exc
        return to_api_response_user_all(response)

    async def delete_all_permanent(self) -> ApiResponse[None]:
        try:
            response = await self._command.DeleteAllUserPermanent(
                _empty(), timeout=RPC_TIMEOUT
            )
        except grpc.aio.AioRpcError as exc:
            raise parse_grpc_error(exc) from exc
        return to_api_response_user_all(response)


def _empty():
    from google.protobuf import empty_pb2

    return empty_pb2.Empty()


__all__ = ["UserHandler", "normalize_pagination"]

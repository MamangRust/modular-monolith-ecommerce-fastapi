"""User command gRPC handler. Messages match the handlers exactly so REST clients see identical envelopes. Request-shape validation happens here (not in the service), which is also where put it: the shared request DTOs re-run the same rules the `validator` tags expressed."""

from __future__ import annotations

from typing import Any

from pydantic import ValidationError

from pb.user import user_command_pb2_grpc, user_common_pb2
from pkg.logger.logger import Logger
from pkg.middleware import grpc_method
from service.user.handler.query import _fill_user, _fill_user_delete_at
from service.user.service.interfaces import UserCommandService
from service.user.service.service import SERVICE_NAME
from shared.domain.requests.user import CreateUserRequest, UpdateUserRequest
from shared.errors import (
    err_grpc_user_invalid_id,
    err_grpc_validate_create_user,
    err_grpc_validate_update_user,
)


class UserCommandHandler(user_command_pb2_grpc.UserCommandServiceServicer):
    def __init__(self, service: UserCommandService, logger: Logger) -> None:
        self._service = service
        self.logger = logger

    @grpc_method("UserCommandService.Create", SERVICE_NAME)
    async def Create(self, request: Any, context: Any) -> Any:
        try:
            CreateUserRequest(
                firstname=request.firstname,
                lastname=request.lastname,
                email=request.email,
                password=request.password,
                confirm_password=request.confirm_password,
            )
        except ValidationError as exc:
            raise err_grpc_validate_create_user.with_internal(exc) from exc

        user = await self._service.create(
            request.firstname, request.lastname, request.email, request.password
        )
        response = user_common_pb2.ApiResponseUser(
            status="success", message="Successfully created user"
        )
        _fill_user(response.data, user)
        return response

    @grpc_method("UserCommandService.Update", SERVICE_NAME)
    async def Update(self, request: Any, context: Any) -> Any:
        if request.id <= 0:
            raise err_grpc_user_invalid_id
        try:
            UpdateUserRequest(
                user_id=request.id,
                firstname=request.firstname,
                lastname=request.lastname,
                email=request.email,
                password=request.password,
                confirm_password=request.confirm_password,
            )
        except ValidationError as exc:
            raise err_grpc_validate_update_user.with_internal(exc) from exc

        user = await self._service.update(
            request.id,
            request.firstname,
            request.lastname,
            request.email,
            request.password,
        )
        response = user_common_pb2.ApiResponseUser(
            status="success", message="Successfully updated user"
        )
        _fill_user(response.data, user)
        return response

    @grpc_method("UserCommandService.TrashedUser", SERVICE_NAME)
    async def TrashedUser(self, request: Any, context: Any) -> Any:
        if request.id <= 0:
            raise err_grpc_user_invalid_id
        user = await self._service.trash(request.id)
        response = user_common_pb2.ApiResponseUserDeleteAt(
            status="success", message="Successfully trashed user"
        )
        _fill_user_delete_at(response.data, user)
        return response

    @grpc_method("UserCommandService.RestoreUser", SERVICE_NAME)
    async def RestoreUser(self, request: Any, context: Any) -> Any:
        if request.id <= 0:
            raise err_grpc_user_invalid_id
        user = await self._service.restore(request.id)
        response = user_common_pb2.ApiResponseUserDeleteAt(
            status="success", message="Successfully restored user"
        )
        _fill_user_delete_at(response.data, user)
        return response

    @grpc_method("UserCommandService.DeleteUserPermanent", SERVICE_NAME)
    async def DeleteUserPermanent(self, request: Any, context: Any) -> Any:
        if request.id <= 0:
            raise err_grpc_user_invalid_id
        await self._service.delete_permanent(request.id)
        return user_common_pb2.ApiResponseUserDelete(
            status="success", message="Successfully deleted user permanently"
        )

    @grpc_method("UserCommandService.RestoreAllUser", SERVICE_NAME)
    async def RestoreAllUser(self, request: Any, context: Any) -> Any:
        await self._service.restore_all()
        return user_common_pb2.ApiResponseUserAll(
            status="success", message="Successfully restored all users"
        )

    @grpc_method("UserCommandService.DeleteAllUserPermanent", SERVICE_NAME)
    async def DeleteAllUserPermanent(self, request: Any, context: Any) -> Any:
        await self._service.delete_all_permanent()
        return user_common_pb2.ApiResponseUserAll(
            status="success", message="Successfully deleted all users permanently"
        )


__all__ = ["UserCommandHandler"]

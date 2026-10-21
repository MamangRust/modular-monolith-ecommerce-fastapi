"""Role command gRPC handler. Messages match the handlers exactly so REST clients see identical envelopes. ID/name validation happens here (not in the service), which is also where put it."""

from __future__ import annotations

from typing import Any

from pb.role import role_command_pb2_grpc, role_common_pb2
from pkg.logger.logger import Logger
from pkg.middleware import grpc_method
from service.role.handler.query import _date, _fill_role
from service.role.service.interfaces import RoleCommandService
from service.role.service.service import SERVICE_NAME
from shared.domain.requests.auth import CreateUserRoleRequest
from shared.errors import (
    err_grpc_role_invalid_id,
    err_grpc_validate_create_role,
    err_grpc_validate_update_role,
)


class RoleCommandHandler(role_command_pb2_grpc.RoleCommandServiceServicer):
    def __init__(self, service: RoleCommandService, logger: Logger) -> None:
        self._service = service
        self.logger = logger

    @grpc_method("RoleCommandService.CreateRole", SERVICE_NAME)
    async def CreateRole(self, request: Any, context: Any) -> Any:
        if not request.name:
            raise err_grpc_validate_create_role
        role = await self._service.create(request.name)
        response = role_common_pb2.ApiResponseRole(
            status="success", message="Successfully created role"
        )
        _fill_role(response.data, role)
        return response

    @grpc_method("RoleCommandService.UpdateRole", SERVICE_NAME)
    async def UpdateRole(self, request: Any, context: Any) -> Any:
        if request.id <= 0:
            raise err_grpc_role_invalid_id
        if not request.name:
            raise err_grpc_validate_update_role
        role = await self._service.update(request.id, request.name)
        response = role_common_pb2.ApiResponseRole(
            status="success", message="Successfully updated role"
        )
        _fill_role(response.data, role)
        return response

    @grpc_method("RoleCommandService.TrashedRole", SERVICE_NAME)
    async def TrashedRole(self, request: Any, context: Any) -> Any:
        if request.role_id <= 0:
            raise err_grpc_role_invalid_id
        role = await self._service.trash(request.role_id)
        response = role_common_pb2.ApiResponseRole(
            status="success", message="Successfully trashed role"
        )
        _fill_role(response.data, role)
        return response

    @grpc_method("RoleCommandService.RestoreRole", SERVICE_NAME)
    async def RestoreRole(self, request: Any, context: Any) -> Any:
        if request.role_id <= 0:
            raise err_grpc_role_invalid_id
        role = await self._service.restore(request.role_id)
        response = role_common_pb2.ApiResponseRole(
            status="success", message="Successfully restored role"
        )
        _fill_role(response.data, role)
        return response

    @grpc_method("RoleCommandService.DeleteRolePermanent", SERVICE_NAME)
    async def DeleteRolePermanent(self, request: Any, context: Any) -> Any:
        if request.role_id <= 0:
            raise err_grpc_role_invalid_id
        await self._service.delete_permanent(request.role_id)
        return role_common_pb2.ApiResponseRoleDelete(
            status="success", message="Successfully deleted role permanently"
        )

    @grpc_method("RoleCommandService.RestoreAllRole", SERVICE_NAME)
    async def RestoreAllRole(self, request: Any, context: Any) -> Any:
        await self._service.restore_all()
        return role_common_pb2.ApiResponseRoleAll(
            status="success", message="Successfully restore all roles"
        )

    @grpc_method("RoleCommandService.DeleteAllRolePermanent", SERVICE_NAME)
    async def DeleteAllRolePermanent(self, request: Any, context: Any) -> Any:
        await self._service.delete_all_permanent()
        return role_common_pb2.ApiResponseRoleAll(
            status="success", message="delete all roles permanent"
        )

    @grpc_method("RoleCommandService.AssignRoleToUser", SERVICE_NAME)
    async def AssignRoleToUser(self, request: Any, context: Any) -> Any:
        if request.user_id <= 0 or request.role_id <= 0:
            raise err_grpc_role_invalid_id
        user_role = await self._service.assign_role_to_user(
            CreateUserRoleRequest(user_id=request.user_id, role_id=request.role_id)
        )
        response = role_common_pb2.ApiResponseUserRole(
            status="success", message="Successfully assigned role to user"
        )
        response.data.user_role_id = user_role.user_role_id
        response.data.user_id = user_role.user_id
        response.data.role_id = user_role.role_id
        response.data.created_at = _date(user_role.created_at)
        response.data.updated_at = _date(user_role.updated_at)
        return response


__all__ = ["RoleCommandHandler"]

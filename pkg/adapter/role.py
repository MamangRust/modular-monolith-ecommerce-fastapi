"""Role/user-role gRPC adapters. The auth service owns users and tokens but not the roles or user_roles tables: role reads and user-role writes over gRPC to the role service through these two narrow adapters. Errors map onto the same sentinels the former direct-SQL repositories used, so the auth service's error surface is unchanged."""

from __future__ import annotations

from typing import Any

import grpc.aio as grpc_aio

from pkg.adapter.guard import call as guard_call
from pkg.database.schema.auth import UserRole
from pkg.database.schema.role import Role
from pkg.resilience.dependency_guard import DependencyGuard
from shared.domain.requests.auth import CreateUserRoleRequest, RemoveUserRoleRequest
from shared.errors import (
    err_assign_role_to_user,
    err_remove_role_from_user,
    err_role_not_found_res,
)

_TIMEOUT_SECONDS = 30


def _parse_rfc3339(value: str) -> Any:
    """Mirror parseTime: an empty/invalid string yields an unset time."""
    from datetime import datetime

    if not value:
        return None
    try:
        return datetime.fromisoformat(value.replace("Z", "+00:00"))
    except ValueError:
        return None


class RoleAdapter:
    """RoleAdapter: role reads over gRPC."""

    def __init__(
        self, channel: grpc_aio.Channel, *, guard: DependencyGuard | None = None
    ) -> None:
        from pb.role import role_common_pb2, role_query_pb2, role_query_pb2_grpc

        self._pb2 = role_query_pb2  # FindByNameRoleRequest
        self._role_pb2 = role_common_pb2  # FindByIdRoleRequest lives in role.proto
        self._query = role_query_pb2_grpc.RoleQueryServiceStub(channel)
        self._guard = guard

    def set_guard(self, guard: DependencyGuard | None) -> None:
        """Implement adapter.GuardSetter."""
        self._guard = guard

    async def find_by_id(self, role_id: int) -> Role:
        async def invoke() -> Any:
            return await self._query.FindByIdRole(
                self._role_pb2.FindByIdRoleRequest(role_id=role_id),
                timeout=_TIMEOUT_SECONDS,
            )

        return self._to_role(await self._fetch(invoke))

    async def find_by_name(self, role_name: str) -> Role:
        async def invoke() -> Any:
            return await self._query.FindByNameRole(
                self._pb2.FindByNameRoleRequest(name=role_name),
                timeout=_TIMEOUT_SECONDS,
            )

        return self._to_role(await self._fetch(invoke))

    async def _fetch(self, invoke: Any) -> Any:
        try:
            resp = await guard_call(self._guard, invoke)
        except Exception as exc:
            raise err_role_not_found_res.with_internal(exc) from exc
        if not resp.HasField("data"):
            raise err_role_not_found_res
        return resp.data

    def _to_role(self, data: Any) -> Role:
        return Role(
            role_id=data.id,
            role_name=data.name,
            created_at=_parse_rfc3339(data.created_at),
            updated_at=_parse_rfc3339(data.updated_at),
            deleted_at=None,
        )


class UserRoleAdapter:
    """UserRoleAdapter: user_roles writes over gRPC."""

    def __init__(
        self, channel: grpc_aio.Channel, *, guard: DependencyGuard | None = None
    ) -> None:
        from pb.role import role_command_pb2_grpc, role_common_pb2

        self._pb2 = role_common_pb2  # Assign/Remove request types live in common
        self._command = role_command_pb2_grpc.RoleCommandServiceStub(channel)
        self._guard = guard

    def set_guard(self, guard: DependencyGuard | None) -> None:
        """Implement adapter.GuardSetter."""
        self._guard = guard

    async def assign_role_to_user(self, request: CreateUserRoleRequest) -> UserRole:
        async def invoke() -> Any:
            return await self._command.AssignRoleToUser(
                self._pb2.AssignRoleToUserRequest(
                    user_id=request.user_id, role_id=request.role_id
                ),
                timeout=_TIMEOUT_SECONDS,
            )

        try:
            resp = await guard_call(self._guard, invoke)
        except Exception as exc:
            raise err_assign_role_to_user.with_internal(exc) from exc
        if not resp.HasField("data"):
            raise err_assign_role_to_user
        data = resp.data
        return UserRole(
            user_role_id=data.user_role_id,
            user_id=data.user_id,
            role_id=data.role_id,
            created_at=_parse_rfc3339(data.created_at),
            updated_at=_parse_rfc3339(data.updated_at),
            deleted_at=None,
        )

    async def remove_role_from_user(self, request: RemoveUserRoleRequest) -> None:
        async def invoke() -> None:
            await self._command.RemoveRoleFromUser(
                self._pb2.RemoveRoleFromUserRequest(
                    user_id=request.user_id, role_id=request.role_id
                ),
                timeout=_TIMEOUT_SECONDS,
            )

        try:
            await guard_call(self._guard, invoke)
        except Exception as exc:
            raise err_remove_role_from_user.with_internal(exc) from exc


__all__ = ["RoleAdapter", "UserRoleAdapter"]

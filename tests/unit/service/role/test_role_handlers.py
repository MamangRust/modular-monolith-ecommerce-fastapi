"""Unit tests for role gRPC handlers (in-process, no server/DB)."""

from __future__ import annotations

from datetime import datetime
from typing import Any

import grpc
import pytest

from pb.role import role_command_pb2, role_common_pb2, role_query_pb2
from pkg.database.schema.auth import UserRole
from pkg.database.schema.role import GetActiveRolesRow, GetRolesRow, Role
from pkg.logger.logger import Logger
from service.role.handler.command import RoleCommandHandler
from service.role.handler.query import RoleQueryHandler

CREATED = datetime(2026, 1, 1)
UPDATED = datetime(2026, 1, 2)
DELETED = datetime(2026, 2, 3)


class FakeAbort(Exception):
    def __init__(self, code: grpc.StatusCode, message: str) -> None:
        self.code = code
        self.message = message
        super().__init__(message)


class FakeContext:
    def __init__(self) -> None:
        self.metadata: tuple[Any, ...] = ()
        self.aborted: FakeAbort | None = None

    def set_trailing_metadata(self, metadata: tuple[Any, ...]) -> None:
        self.metadata = metadata

    async def abort(self, code: grpc.StatusCode, message: str) -> None:
        self.aborted = FakeAbort(code, message)
        raise self.aborted


class FakeQueryService:
    async def find_all(self, search, page, page_size):
        return [
            GetRolesRow(1, "Admin", CREATED, UPDATED, 11)
        ], 11

    async def find_by_id(self, role_id):
        return Role(role_id, "Admin", CREATED, UPDATED, None)

    async def find_by_user_id(self, user_id):
        return [Role(1, "Admin", CREATED, UPDATED, None)]

    async def find_active(self, search, page, page_size):
        return [GetActiveRolesRow(1, "Admin", CREATED, UPDATED, None, 1)], 1

    async def find_trashed(self, search, page, page_size):
        return [GetActiveRolesRow(2, "Old", CREATED, UPDATED, DELETED, 1)], 1

    async def find_by_name(self, role_name):
        return Role(1, role_name, CREATED, UPDATED, None)


class FakeCommandService:
    async def create(self, role_name):
        return Role(1, role_name, CREATED, UPDATED, None)

    async def update(self, role_id, role_name):
        return Role(role_id, role_name, CREATED, UPDATED, None)

    async def trash(self, role_id):
        return Role(role_id, "Admin", CREATED, UPDATED, DELETED)

    async def restore(self, role_id):
        return Role(role_id, "Admin", CREATED, UPDATED, None)

    async def delete_permanent(self, role_id):
        return None

    async def restore_all(self):
        return None

    async def delete_all_permanent(self):
        return None

    async def assign_role_to_user(self, request):
        return UserRole(11, request.user_id, request.role_id, CREATED, UPDATED, None)
        return None


def _query_handler() -> RoleQueryHandler:
    return RoleQueryHandler(FakeQueryService(), Logger("test", "error"))


def _command_handler() -> RoleCommandHandler:
    return RoleCommandHandler(FakeCommandService(), Logger("test", "error"))


async def test_find_all_role_normalizes_and_computes_total_pages() -> None:
    request = role_query_pb2.FindAllRoleRequest(page=0, page_size=0, search="")
    response = await _query_handler().FindAllRole(request, FakeContext())

    assert response.status == "success"
    assert response.pagination.current_page == 1
    assert response.pagination.page_size == 10
    assert response.pagination.total_pages == 2
    assert response.pagination.total_records == 11
    assert response.data[0].created_at == "2026-01-01"


async def test_find_by_id_role_rejects_non_positive_id() -> None:
    context = FakeContext()
    with pytest.raises(FakeAbort) as excinfo:
        await _query_handler().FindByIdRole(
            role_common_pb2.FindByIdRoleRequest(role_id=0), context
        )
    assert excinfo.value.code is grpc.StatusCode.INVALID_ARGUMENT
    assert excinfo.value.message == "Invalid Role ID"
    assert context.metadata  # ErrorResponse detail attached


async def test_find_by_id_role_returns_role() -> None:
    response = await _query_handler().FindByIdRole(
        role_common_pb2.FindByIdRoleRequest(role_id=1), FakeContext()
    )
    assert response.data.id == 1
    assert response.data.updated_at == "2026-01-02"


async def test_find_by_active_omits_deleted_at_when_null() -> None:
    response = await _query_handler().FindByActive(
        role_query_pb2.FindAllRoleRequest(page=1, page_size=10), FakeContext()
    )
    assert response.data[0].HasField("deleted_at") is False


async def test_find_by_trashed_includes_deleted_at() -> None:
    response = await _query_handler().FindByTrashed(
        role_query_pb2.FindAllRoleRequest(page=1, page_size=10), FakeContext()
    )
    assert response.data[0].deleted_at.value == "2026-02-03"


async def test_find_by_user_id_returns_many() -> None:
    response = await _query_handler().FindByUserId(
        role_query_pb2.FindByIdUserRoleRequest(user_id=1), FakeContext()
    )
    assert len(response.data) == 1
    assert response.data[0].name == "Admin"


async def test_create_role_rejects_empty_name() -> None:
    context = FakeContext()
    with pytest.raises(FakeAbort) as excinfo:
        await _command_handler().CreateRole(role_command_pb2.CreateRoleRequest(name=""), context)
    assert excinfo.value.code is grpc.StatusCode.INVALID_ARGUMENT


async def test_create_role_returns_envelope() -> None:
    response = await _command_handler().CreateRole(
        role_command_pb2.CreateRoleRequest(name="NewRole"), FakeContext()
    )
    assert response.status == "success"
    assert response.message == "Successfully created role"
    assert response.data.name == "NewRole"


async def test_update_role_rejects_non_positive_id() -> None:
    with pytest.raises(FakeAbort):
        await _command_handler().UpdateRole(
            role_command_pb2.UpdateRoleRequest(id=0, name="X"), FakeContext()
        )


async def test_trashed_role_reports_basic_envelope() -> None:
    """Ecommerce contract: TrashedRole returns the basic ApiResponseRole (the
    delete-at envelope that payment-gateway used does not exist here)."""
    response = await _command_handler().TrashedRole(
        role_common_pb2.FindByIdRoleRequest(role_id=3), FakeContext()
    )
    assert response.message == "Successfully trashed role"
    assert response.data.id == 3


async def test_delete_permanent_has_no_data() -> None:
    response = await _command_handler().DeleteRolePermanent(
        role_common_pb2.FindByIdRoleRequest(role_id=3), FakeContext()
    )
    assert response.message == "Successfully deleted role permanently"


async def test_bulk_commands_report_go_messages() -> None:
    handler = _command_handler()
    restore = await handler.RestoreAllRole(None, FakeContext())
    delete = await handler.DeleteAllRolePermanent(None, FakeContext())
    assert restore.message == "Successfully restore all roles"
    assert delete.message == "delete all roles permanent"

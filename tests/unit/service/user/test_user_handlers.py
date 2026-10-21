"""Unit tests for user gRPC handlers (in-process, no server/DB)."""

from __future__ import annotations

from datetime import datetime
from typing import Any

import grpc
import pytest

from pb.user import user_command_pb2, user_common_pb2, user_query_pb2
from pkg.database.schema.user import (
    CreateUserRow,
    GetActiveUsersRow,
    GetUserByIDRow,
    GetUsersRow,
    TrashUserRow,
    UpdateUserRow,
)
from pkg.logger.logger import Logger
from service.user.handler.command import UserCommandHandler
from service.user.handler.query import UserQueryHandler

CREATED = datetime(2026, 1, 1, 10, 0, 0)
UPDATED = datetime(2026, 1, 2, 10, 0, 0)
DELETED = datetime(2026, 2, 3, 10, 0, 0)


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
            GetUsersRow(1, "John", "Doe", "john@example.com", "h", CREATED, UPDATED, 11)
        ], 11

    async def find_by_id(self, user_id):
        return GetUserByIDRow(
            user_id, "John", "Doe", "john@example.com", "h", CREATED, UPDATED
        )

    async def find_active(self, search, page, page_size):
        return [
            GetActiveUsersRow(
                1, "John", "Doe", "john@example.com", "h", CREATED, UPDATED, None, 1
            )
        ], 1

    async def find_trashed(self, search, page, page_size):
        return [
            GetActiveUsersRow(
                2, "Old", "User", "old@example.com", "h", CREATED, UPDATED, DELETED, 1
            )
        ], 1


class FakeCommandService:
    async def create(self, firstname, lastname, email, password):
        return CreateUserRow(
            1, firstname, lastname, email, "h", "v", CREATED, UPDATED
        )

    async def update(self, user_id, firstname, lastname, email, password):
        return UpdateUserRow(user_id, firstname, lastname, email, "h", CREATED, UPDATED)

    async def trash(self, user_id):
        return TrashUserRow(user_id, "John", "Doe", "john@example.com", CREATED, UPDATED, DELETED)

    async def restore(self, user_id):
        return TrashUserRow(user_id, "John", "Doe", "john@example.com", CREATED, UPDATED, None)

    async def delete_permanent(self, user_id):
        return None

    async def restore_all(self):
        return None

    async def delete_all_permanent(self):
        return None


def _query_handler() -> UserQueryHandler:
    return UserQueryHandler(FakeQueryService(), Logger("test", "error"))


def _command_handler() -> UserCommandHandler:
    return UserCommandHandler(FakeCommandService(), Logger("test", "error"))


async def test_find_all_normalizes_and_emits_rfc3339() -> None:
    request = user_query_pb2.FindAllUserRequest(page=0, page_size=0, search="")
    response = await _query_handler().FindAll(request, FakeContext())

    assert response.status == "success"
    assert response.pagination.current_page == 1
    assert response.pagination.page_size == 10
    assert response.pagination.total_pages == 2
    assert response.pagination.total_records == 11
    assert response.data[0].created_at == "2026-01-01T10:00:00Z"


async def test_find_by_id_rejects_non_positive_id() -> None:
    context = FakeContext()
    with pytest.raises(FakeAbort) as excinfo:
        await _query_handler().FindById(user_common_pb2.FindByIdUserRequest(id=0), context)
    assert excinfo.value.code is grpc.StatusCode.INVALID_ARGUMENT
    assert excinfo.value.message == "Invalid user ID"
    assert context.metadata


async def test_find_by_id_returns_user() -> None:
    response = await _query_handler().FindById(
        user_common_pb2.FindByIdUserRequest(id=1), FakeContext()
    )
    assert response.data.id == 1
    assert response.data.firstname == "John"
    assert response.data.updated_at == "2026-01-02T10:00:00Z"


async def test_find_by_active_omits_deleted_at_when_null() -> None:
    response = await _query_handler().FindByActive(
        user_query_pb2.FindAllUserRequest(page=1, page_size=10), FakeContext()
    )
    assert response.data[0].HasField("deleted_at") is False


async def test_find_by_trashed_includes_deleted_at() -> None:
    response = await _query_handler().FindByTrashed(
        user_query_pb2.FindAllUserRequest(page=1, page_size=10), FakeContext()
    )
    assert response.data[0].deleted_at.value == "2026-02-03T10:00:00Z"


async def test_create_rejects_invalid_body() -> None:
    context = FakeContext()
    request = user_command_pb2.CreateUserRequest(
        firstname="John",
        lastname="Doe",
        email="not-an-email",
        password="secret1",
        confirm_password="secret1",
    )
    with pytest.raises(FakeAbort) as excinfo:
        await _command_handler().Create(request, context)
    assert excinfo.value.code is grpc.StatusCode.INVALID_ARGUMENT
    assert excinfo.value.message == "Validation failed: invalid create user request"


async def test_create_returns_envelope() -> None:
    request = user_command_pb2.CreateUserRequest(
        firstname="John",
        lastname="Doe",
        email="john@example.com",
        password="secret1",
        confirm_password="secret1",
    )
    response = await _command_handler().Create(request, FakeContext())
    assert response.status == "success"
    assert response.message == "Successfully created user"
    assert response.data.email == "john@example.com"


async def test_update_rejects_non_positive_id() -> None:
    with pytest.raises(FakeAbort):
        await _command_handler().Update(
            user_command_pb2.UpdateUserRequest(
                id=0,
                firstname="John",
                lastname="Doe",
                email="john@example.com",
                password="secret1",
                confirm_password="secret1",
            ),
            FakeContext(),
        )


async def test_trashed_user_reports_deleted_at() -> None:
    response = await _command_handler().TrashedUser(
        user_common_pb2.FindByIdUserRequest(id=3), FakeContext()
    )
    assert response.message == "Successfully trashed user"
    assert response.data.deleted_at.value == "2026-02-03T10:00:00Z"


async def test_delete_permanent_has_no_data() -> None:
    response = await _command_handler().DeleteUserPermanent(
        user_common_pb2.FindByIdUserRequest(id=3), FakeContext()
    )
    assert response.message == "Successfully deleted user permanently"


async def test_bulk_commands_report_go_messages() -> None:
    handler = _command_handler()
    restore = await handler.RestoreAllUser(None, FakeContext())
    delete = await handler.DeleteAllUserPermanent(None, FakeContext())
    assert restore.message == "Successfully restored all users"
    assert delete.message == "Successfully deleted all users permanently"

"""User gRPC integration tests: real grpc.aio server, generated client.

Marked `integration`. Verifies the wire contract, that the `ErrorResponse`
detail survives the hop (404 stays 404), and that create never stores the
plaintext password.
"""

from __future__ import annotations

import uuid

import grpc
import pytest

from pb.user import (
    user_command_pb2,
    user_command_pb2_grpc,
    user_common_pb2,
    user_query_pb2,
    user_query_pb2_grpc,
)
from pkg.database.database import Database
from shared.errors import parse_grpc_error

pytestmark = pytest.mark.integration

EMAIL_PREFIX = "usrgrpc_"


def _email() -> str:
    return f"{EMAIL_PREFIX}{uuid.uuid4().hex[:12]}@test.example"


async def _cleanup(db: Database) -> None:
    pattern = f"{EMAIL_PREFIX}%"
    await db.execute(
        "DELETE FROM outbox_events WHERE payload->>'email' LIKE :pattern",
        {"pattern": pattern},
    )
    await db.execute("DELETE FROM users WHERE email LIKE :pattern", {"pattern": pattern})


async def test_user_grpc_lifecycle_and_error_mapping(
    db: Database, user_grpc_server: str
) -> None:
    channel = grpc.aio.insecure_channel(user_grpc_server)
    query = user_query_pb2_grpc.UserQueryServiceStub(channel)
    command = user_command_pb2_grpc.UserCommandServiceStub(channel)
    email = _email()

    try:
        created = await command.Create(
            user_command_pb2.CreateUserRequest(
                firstname="John",
                lastname="Doe",
                email=email,
                password="secret1",
                confirm_password="secret1",
            ),
            timeout=5,
        )
        assert created.status == "success"
        assert created.data.email == email
        user_id = created.data.id

        # The stored password must be a bcrypt hash, never the plaintext.
        stored = await db.scalar(
            "SELECT password FROM users WHERE user_id = :user_id", {"user_id": user_id}
        )
        assert stored is not None
        assert stored["password"] != "secret1"
        assert stored["password"].startswith("$2")

        found = await query.FindById(user_common_pb2.FindByIdUserRequest(id=user_id), timeout=5)
        assert found.data.id == user_id
        assert found.data.created_at

        listed = await query.FindAll(
            user_query_pb2.FindAllUserRequest(page=1, page_size=10, search=email), timeout=5
        )
        assert listed.pagination.total_records >= 1

        trashed = await command.TrashedUser(
            user_common_pb2.FindByIdUserRequest(id=user_id), timeout=5
        )
        assert trashed.data.HasField("deleted_at")

        restored = await command.RestoreUser(
            user_common_pb2.FindByIdUserRequest(id=user_id), timeout=5
        )
        assert restored.data.HasField("deleted_at") is False

        with pytest.raises(grpc.aio.AioRpcError) as invalid:
            await query.FindById(user_common_pb2.FindByIdUserRequest(id=0), timeout=5)
        assert invalid.value.code() is grpc.StatusCode.INVALID_ARGUMENT
        parsed_invalid = parse_grpc_error(invalid.value)
        assert parsed_invalid.code == 400
        assert parsed_invalid.message == "Invalid user ID"

        with pytest.raises(grpc.aio.AioRpcError) as missing:
            await query.FindById(user_common_pb2.FindByIdUserRequest(id=2_000_000_000), timeout=5)
        assert missing.value.code() is grpc.StatusCode.NOT_FOUND
        assert parse_grpc_error(missing.value).code == 404
    finally:
        await channel.close()
        await _cleanup(db)


async def test_duplicate_create_is_already_exists(
    db: Database, user_grpc_server: str
) -> None:
    channel = grpc.aio.insecure_channel(user_grpc_server)
    command = user_command_pb2_grpc.UserCommandServiceStub(channel)
    email = _email()
    request = user_command_pb2.CreateUserRequest(
        firstname="John",
        lastname="Doe",
        email=email,
        password="secret1",
        confirm_password="secret1",
    )
    try:
        await command.Create(request, timeout=5)
        with pytest.raises(grpc.aio.AioRpcError) as conflict:
            await command.Create(request, timeout=5)
        assert conflict.value.code() is grpc.StatusCode.ALREADY_EXISTS
        assert parse_grpc_error(conflict.value).code == 409
    finally:
        await channel.close()
        await _cleanup(db)


async def test_create_rejects_invalid_body(
    db: Database, user_grpc_server: str
) -> None:
    channel = grpc.aio.insecure_channel(user_grpc_server)
    command = user_command_pb2_grpc.UserCommandServiceStub(channel)
    try:
        with pytest.raises(grpc.aio.AioRpcError) as invalid:
            await command.Create(
                user_command_pb2.CreateUserRequest(
                    firstname="John",
                    lastname="Doe",
                    email="not-an-email",
                    password="secret1",
                    confirm_password="secret1",
                ),
                timeout=5,
            )
        assert invalid.value.code() is grpc.StatusCode.INVALID_ARGUMENT
        assert (
            parse_grpc_error(invalid.value).message
            == "Validation failed: invalid create user request"
        )
    finally:
        await channel.close()

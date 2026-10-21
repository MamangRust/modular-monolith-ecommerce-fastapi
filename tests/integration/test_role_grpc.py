"""Role gRPC integration tests: real grpc.aio server, generated client.

Marked `integration`. Verifies the wire contract and that the
`ErrorResponse` detail survives the hop so a 404 stays a 404.
"""

from __future__ import annotations

import uuid

import grpc
import pytest

from pb.role import (
    role_command_pb2,
    role_command_pb2_grpc,
    role_common_pb2,
    role_query_pb2,
    role_query_pb2_grpc,
)
from pkg.database.database import Database
from shared.errors import parse_grpc_error

pytestmark = pytest.mark.integration


async def test_role_grpc_lifecycle_and_error_mapping(
    db: Database, role_grpc_server: str
) -> None:
    channel = grpc.aio.insecure_channel(role_grpc_server)
    query = role_query_pb2_grpc.RoleQueryServiceStub(channel)
    command = role_command_pb2_grpc.RoleCommandServiceStub(channel)
    name = f"TEST_GRPC_{uuid.uuid4().hex[:10]}"

    try:
        created = await command.CreateRole(
            role_command_pb2.CreateRoleRequest(name=name), timeout=5
        )
        assert created.status == "success"
        assert created.data.name == name
        role_id = created.data.id

        found = await query.FindByIdRole(
            role_common_pb2.FindByIdRoleRequest(role_id=role_id), timeout=5
        )
        assert found.data.id == role_id
        assert found.data.created_at

        listed = await query.FindAllRole(
            role_query_pb2.FindAllRoleRequest(page=1, page_size=10, search=name), timeout=5
        )
        assert listed.pagination.total_records >= 1

        trashed = await command.TrashedRole(
            role_common_pb2.FindByIdRoleRequest(role_id=role_id), timeout=5
        )
        # Ecommerce contract: Trashed/Restore return the basic envelope
        # (RoleResponse has no deleted_at on the wire).
        assert trashed.data.id == role_id

        restored = await command.RestoreRole(
            role_common_pb2.FindByIdRoleRequest(role_id=role_id), timeout=5
        )
        assert restored.data.id == role_id

        with pytest.raises(grpc.aio.AioRpcError) as invalid:
            await query.FindByIdRole(role_common_pb2.FindByIdRoleRequest(role_id=0), timeout=5)
        assert invalid.value.code() is grpc.StatusCode.INVALID_ARGUMENT
        parsed_invalid = parse_grpc_error(invalid.value)
        assert parsed_invalid.code == 400
        assert parsed_invalid.message == "Invalid Role ID"

        with pytest.raises(grpc.aio.AioRpcError) as missing:
            await query.FindByIdRole(
                role_common_pb2.FindByIdRoleRequest(role_id=2_000_000_000), timeout=5
            )
        assert missing.value.code() is grpc.StatusCode.NOT_FOUND
        assert parse_grpc_error(missing.value).code == 404
    finally:
        await channel.close()
        await db.execute(
            "DELETE FROM roles WHERE role_name LIKE :pattern", {"pattern": "TEST_GRPC%"}
        )


async def test_duplicate_create_is_already_exists(
    db: Database, role_grpc_server: str
) -> None:
    channel = grpc.aio.insecure_channel(role_grpc_server)
    command = role_command_pb2_grpc.RoleCommandServiceStub(channel)
    name = f"TEST_GRPC_{uuid.uuid4().hex[:10]}"
    try:
        await command.CreateRole(role_command_pb2.CreateRoleRequest(name=name), timeout=5)
        with pytest.raises(grpc.aio.AioRpcError) as conflict:
            await command.CreateRole(
                role_command_pb2.CreateRoleRequest(name=name), timeout=5
            )
        assert conflict.value.code() is grpc.StatusCode.ALREADY_EXISTS
        assert parse_grpc_error(conflict.value).code == 409
    finally:
        await channel.close()
        await db.execute(
            "DELETE FROM roles WHERE role_name LIKE :pattern", {"pattern": "TEST_GRPC%"}
        )

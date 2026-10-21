"""Banner gRPC integration tests: real grpc.aio server, generated client.

Marked `integration`. Verifies the wire contract (including the banner
timestamp layout and the always-present `deleted_at` wrapper) and that the
`ErrorResponse` detail survives the hop so a 404 stays a 404.
"""

from __future__ import annotations

import uuid

import grpc
import pytest

from pb.banner import (
    banner_command_pb2,
    banner_command_pb2_grpc,
    banner_common_pb2,
    banner_query_pb2,
    banner_query_pb2_grpc,
)
from pkg.database.database import Database
from shared.errors import parse_grpc_error

pytestmark = pytest.mark.integration


def _create_request(name: str) -> banner_command_pb2.CreateBannerRequest:
    return banner_command_pb2.CreateBannerRequest(
        name=name,
        start_date="2023-01-01",
        end_date="2023-01-31",
        start_time="08:00:00",
        end_time="16:00:00",
        is_active=True,
    )


async def test_banner_grpc_lifecycle_and_error_mapping(
    db: Database, banner_grpc_server: str
) -> None:
    channel = grpc.aio.insecure_channel(banner_grpc_server)
    query = banner_query_pb2_grpc.BannerQueryServiceStub(channel)
    command = banner_command_pb2_grpc.BannerCommandServiceStub(channel)
    name = f"TEST_GRPC_{uuid.uuid4().hex[:10]}"

    try:
        created = await command.Create(_create_request(name), timeout=5)
        assert created.status == "success"
        assert created.message == "Successfully created banner"
        assert created.data.name == name
        assert created.data.start_date == "2023-01-01"
        assert created.data.start_time == "08:00:00"
        assert created.data.created_at  # banner layout, non-empty
        banner_id = created.data.banner_id

        found = await query.FindById(
            banner_common_pb2.FindByIdBannerRequest(id=banner_id), timeout=5
        )
        assert found.data.banner_id == banner_id

        listed = await query.FindAll(
            banner_query_pb2.FindAllBannerRequest(page=1, page_size=10, search=name),
            timeout=5,
        )
        assert listed.pagination.total_records >= 1

        trashed = await command.Trash(
            banner_common_pb2.FindByIdBannerRequest(id=banner_id), timeout=5
        )
        assert trashed.message == "Successfully trashed banner"
        assert trashed.data.deleted_at.value  # non-empty after trash

        # FindAll has no deleted_at filter, so the trashed row is still listed.
        listed_after_trash = await query.FindAll(
            banner_query_pb2.FindAllBannerRequest(page=1, page_size=10, search=name),
            timeout=5,
        )
        assert any(
            row.banner_id == banner_id for row in listed_after_trash.data
        )

        active = await query.FindByActive(
            banner_query_pb2.FindAllBannerRequest(page=1, page_size=10, search=name),
            timeout=5,
        )
        assert all(row.banner_id != banner_id for row in active.data)

        restored = await command.Restore(
            banner_common_pb2.FindByIdBannerRequest(id=banner_id), timeout=5
        )
        assert restored.message == "Successfully restored banner"

        with pytest.raises(grpc.aio.AioRpcError) as invalid:
            await query.FindById(
                banner_common_pb2.FindByIdBannerRequest(id=0), timeout=5
            )
        assert invalid.value.code() is grpc.StatusCode.INVALID_ARGUMENT
        parsed_invalid = parse_grpc_error(invalid.value)
        assert parsed_invalid.code == 400
        assert parsed_invalid.message == "Invalid Banner ID"

        with pytest.raises(grpc.aio.AioRpcError) as missing:
            await query.FindById(
                banner_common_pb2.FindByIdBannerRequest(id=2_000_000_000), timeout=5
            )
        assert missing.value.code() is grpc.StatusCode.NOT_FOUND
        assert parse_grpc_error(missing.value).code == 404

        with pytest.raises(grpc.aio.AioRpcError) as invalid_date:
            await command.Create(
                banner_command_pb2.CreateBannerRequest(
                    name="bad",
                    start_date="2023/01/01",
                    end_date="2023-01-31",
                    start_time="08:00:00",
                    end_time="16:00:00",
                ),
                timeout=5,
            )
        assert invalid_date.value.code() is grpc.StatusCode.INVALID_ARGUMENT
        assert (
            parse_grpc_error(invalid_date.value).message
            == "Validation failed: invalid create banner request"
        )
    finally:
        await channel.close()
        await db.execute(
            "DELETE FROM banners WHERE name LIKE :pattern",
            {"pattern": "TEST_GRPC%"},
        )


async def test_delete_permanent_removes_trashed_row(
    db: Database, banner_grpc_server: str
) -> None:
    channel = grpc.aio.insecure_channel(banner_grpc_server)
    query = banner_query_pb2_grpc.BannerQueryServiceStub(channel)
    command = banner_command_pb2_grpc.BannerCommandServiceStub(channel)
    name = f"TEST_GRPC_{uuid.uuid4().hex[:10]}"
    try:
        created = await command.Create(_create_request(name), timeout=5)
        banner_id = created.data.banner_id
        await command.Trash(
            banner_common_pb2.FindByIdBannerRequest(id=banner_id), timeout=5
        )
        deleted = await command.DeletePermanent(
            banner_common_pb2.FindByIdBannerRequest(id=banner_id), timeout=5
        )
        assert deleted.message == "Successfully deleted banner permanently"

        trashed = await query.FindByTrashed(
            banner_query_pb2.FindAllBannerRequest(page=1, page_size=10, search=name),
            timeout=5,
        )
        assert all(row.banner_id != banner_id for row in trashed.data)
    finally:
        await channel.close()
        await db.execute(
            "DELETE FROM banners WHERE name LIKE :pattern",
            {"pattern": "TEST_GRPC%"},
        )

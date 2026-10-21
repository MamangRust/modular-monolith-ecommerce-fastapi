"""Slider gRPC integration tests: real grpc.aio server, generated client.

Marked `integration`. Verifies the wire contract (date-only timestamps, the
`deleted_at` wrapper only on the `...DeleteAt` projections, `image` field) and
that the `ErrorResponse` detail survives the hop, so a 400/404 stays a 400/404.

Unlike shipping_address, slider `FindById` has **no** id==0 guard, so a zero id
reaches the repository and surfaces as `NOT_FOUND`; the command handlers
(`Update`/`TrashedSlider`/`RestoreSlider`/`DeleteSliderPermanent`) do guard
`id == 0` with a bare 400 `invalid ID`.
"""

from __future__ import annotations

import uuid

import grpc
import pytest
from google.protobuf import empty_pb2

from pb.slider import (
    slider_command_pb2,
    slider_command_pb2_grpc,
    slider_common_pb2,
    slider_query_pb2,
    slider_query_pb2_grpc,
)
from pkg.database.database import Database
from shared.errors import parse_grpc_error

pytestmark = pytest.mark.integration


def _name() -> str:
    return f"Hero {uuid.uuid4().hex[:10]}"


async def _cleanup(db: Database, slider_id: int) -> None:
    await db.execute(
        "DELETE FROM sliders WHERE slider_id = :slider_id", {"slider_id": slider_id}
    )


async def test_slider_grpc_lifecycle_and_error_mapping(
    db: Database, slider_grpc_server: str
) -> None:
    channel = grpc.aio.insecure_channel(slider_grpc_server)
    query = slider_query_pb2_grpc.SliderQueryServiceStub(channel)
    command = slider_command_pb2_grpc.SliderCommandServiceStub(channel)
    name = _name()

    try:
        created = await command.Create(
            slider_command_pb2.CreateSliderRequest(name=name, image="/img/a.png"),
            timeout=5,
        )
        assert created.status == "success"
        assert created.message == "Successfully created slider"
        assert created.data.name == name
        assert created.data.image == "/img/a.png"
        assert created.data.created_at
        assert len(created.data.created_at) == 10  # date-only
        slider_id = created.data.id

        found = await query.FindById(
            slider_common_pb2.FindByIdSliderRequest(id=slider_id), timeout=5
        )
        assert found.message == "Successfully fetched slider by ID"
        assert found.data.id == slider_id

        listed = await query.FindAll(
            slider_query_pb2.FindAllSliderRequest(page=1, page_size=10, search=name),
            timeout=5,
        )
        assert listed.pagination.total_records >= 1

        trashed = await command.TrashedSlider(
            slider_common_pb2.FindByIdSliderRequest(id=slider_id), timeout=5
        )
        assert trashed.message == "Successfully trashed slider"
        assert trashed.data.deleted_at.value

        listed_after = await query.FindAll(
            slider_query_pb2.FindAllSliderRequest(page=1, page_size=10, search=name),
            timeout=5,
        )
        assert all(row.id != slider_id for row in listed_after.data)

        trashed_rows = await query.FindByTrashed(
            slider_query_pb2.FindAllSliderRequest(page=1, page_size=10, search=name),
            timeout=5,
        )
        assert any(
            row.id == slider_id and row.deleted_at.value for row in trashed_rows.data
        )

        restored = await command.RestoreSlider(
            slider_common_pb2.FindByIdSliderRequest(id=slider_id), timeout=5
        )
        assert restored.message == "Successfully restored slider"

        # Command handlers guard id == 0 with a bare 400 invalid ID.
        with pytest.raises(grpc.aio.AioRpcError) as invalid:
            await command.TrashedSlider(
                slider_common_pb2.FindByIdSliderRequest(id=0), timeout=5
            )
        assert invalid.value.code() is grpc.StatusCode.INVALID_ARGUMENT
        parsed_invalid = parse_grpc_error(invalid.value)
        assert parsed_invalid.code == 400
        assert parsed_invalid.message == "invalid ID"

        # FindById has NO guard: a zero id reaches the repo and is NOT_FOUND.
        with pytest.raises(grpc.aio.AioRpcError) as invalid_query:
            await query.FindById(
                slider_common_pb2.FindByIdSliderRequest(id=0), timeout=5
            )
        assert invalid_query.value.code() is grpc.StatusCode.NOT_FOUND

        # A repository 404 is preserved as NOT_FOUND (ToGrpcError semantics).
        with pytest.raises(grpc.aio.AioRpcError) as missing:
            await command.TrashedSlider(
                slider_common_pb2.FindByIdSliderRequest(id=2_000_000_000), timeout=5
            )
        assert missing.value.code() is grpc.StatusCode.NOT_FOUND
        assert parse_grpc_error(missing.value).code == 404

        await command.TrashedSlider(
            slider_common_pb2.FindByIdSliderRequest(id=slider_id), timeout=5
        )
        deleted = await command.DeleteSliderPermanent(
            slider_common_pb2.FindByIdSliderRequest(id=slider_id), timeout=5
        )
        assert deleted.message == "Successfully deleted slider permanently"
    finally:
        await channel.close()
        await _cleanup(db, slider_id)


async def test_restore_all_and_delete_all_over_grpc(
    db: Database, slider_grpc_server: str
) -> None:
    channel = grpc.aio.insecure_channel(slider_grpc_server)
    command = slider_command_pb2_grpc.SliderCommandServiceStub(channel)
    query = slider_query_pb2_grpc.SliderQueryServiceStub(channel)
    name = _name()
    created = await command.Create(
        slider_command_pb2.CreateSliderRequest(name=name, image="/img/a.png"),
        timeout=5,
    )
    slider_id = created.data.id
    try:
        await command.TrashedSlider(
            slider_common_pb2.FindByIdSliderRequest(id=slider_id), timeout=5
        )

        restored_all = await command.RestoreAllSlider(empty_pb2.Empty(), timeout=5)
        assert restored_all.message == "Successfully restored all sliders"

        active = await query.FindByActive(
            slider_query_pb2.FindAllSliderRequest(page=1, page_size=10, search=name),
            timeout=5,
        )
        assert any(row.id == slider_id for row in active.data)

        await command.TrashedSlider(
            slider_common_pb2.FindByIdSliderRequest(id=slider_id), timeout=5
        )
        deleted_all = await command.DeleteAllSliderPermanent(
            empty_pb2.Empty(), timeout=5
        )
        assert deleted_all.message == "Successfully deleted all sliders permanently"

        trashed_rows = await query.FindByTrashed(
            slider_query_pb2.FindAllSliderRequest(page=1, page_size=10, search=name),
            timeout=5,
        )
        assert all(row.id != slider_id for row in trashed_rows.data)
    finally:
        await channel.close()
        await _cleanup(db, slider_id)


__all__ = []

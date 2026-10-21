"""Unit tests for slider gRPC handlers (in-process, no server/DB). Slider timestamps are emitted as date-only strings (`%Y-%m-%d`), matching Unlike the query `FindById`, the gRPC command handlers (`Update`/`TrashedSlider`/`RestoreSlider`/`DeleteSliderPermanent`) reject an `id == 0` with a bare `invalid ID` gRPC error, while `FindById` has no guard (it forwards a 404 from the repository when the id is missing)."""

from __future__ import annotations

from datetime import datetime
from typing import Any

import grpc
import pytest

from pb.slider import slider_command_pb2, slider_common_pb2, slider_query_pb2
from pkg.database.schema.slider import (
    CreateSliderRow,
    GetSliderByIDRow,
    GetSlidersActiveRow,
    GetSlidersRow,
    Slider,
)
from pkg.logger.logger import Logger
from service.slider.handler.command import SliderCommandHandler
from service.slider.handler.query import SliderQueryHandler

CREATED = datetime(2026, 1, 2)
UPDATED = datetime(2026, 1, 3)
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


def _row(slider_id: int = 1, total: int = 11) -> GetSlidersRow:
    return GetSlidersRow(
        slider_id=slider_id,
        name="Hero",
        image="/img/a.png",
        created_at=CREATED,
        updated_at=UPDATED,
        total_count=total,
    )


def _active_row(deleted_at: datetime | None = None) -> GetSlidersActiveRow:
    return GetSlidersActiveRow(
        slider_id=1,
        name="Hero",
        image="/img/a.png",
        created_at=CREATED,
        updated_at=UPDATED,
        deleted_at=deleted_at,
        total_count=1,
    )


def _by_id_row() -> GetSliderByIDRow:
    return GetSliderByIDRow(
        slider_id=1,
        name="Hero",
        image="/img/a.png",
        created_at=CREATED,
        updated_at=UPDATED,
    )


class FakeQueryService:
    async def find_all(self, search, page, page_size):
        return [_row()], 11

    async def find_active(self, search, page, page_size):
        return [_active_row()], 1

    async def find_trashed(self, search, page, page_size):
        return [_active_row(deleted_at=DELETED)], 1

    async def find_by_id(self, slider_id):
        return _by_id_row()


class FakeCommandService:
    async def create(self, request):
        return CreateSliderRow(
            slider_id=1,
            name=request.name,
            image=request.image,
            created_at=CREATED,
            updated_at=UPDATED,
        )

    async def update(self, request):
        return CreateSliderRow(
            slider_id=request.slider_id or 1,
            name=request.name,
            image=request.image,
            created_at=CREATED,
            updated_at=UPDATED,
        )

    async def trash(self, slider_id):
        return Slider(
            slider_id=slider_id,
            name="Hero",
            image="/img/a.png",
            created_at=CREATED,
            updated_at=UPDATED,
            deleted_at=DELETED,
        )

    async def restore(self, slider_id):
        return Slider(
            slider_id=slider_id,
            name="Hero",
            image="/img/a.png",
            created_at=CREATED,
            updated_at=UPDATED,
            deleted_at=None,
        )

    async def delete_permanent(self, slider_id):
        return True

    async def restore_all(self):
        return True

    async def delete_all_permanent(self):
        return True


def _logger() -> Logger:
    return Logger("test", "error")


def _query_handler() -> SliderQueryHandler:
    return SliderQueryHandler(FakeQueryService(), _logger())


def _command_handler() -> SliderCommandHandler:
    return SliderCommandHandler(FakeCommandService(), _logger())


async def test_find_all_date_only() -> None:
    request = slider_query_pb2.FindAllSliderRequest(page=0, page_size=0, search="")
    response = await _query_handler().FindAll(request, FakeContext())

    assert response.status == "success"
    assert response.message == "Successfully fetched slider records"
    assert response.pagination.current_page == 1
    assert response.pagination.page_size == 10
    assert response.pagination.total_pages == 2
    assert response.pagination.total_records == 11
    # Date-only layout.
    assert response.data[0].created_at == "2026-01-02"
    assert response.data[0].updated_at == "2026-01-03"
    assert response.data[0].name == "Hero"
    assert response.data[0].image == "/img/a.png"


async def test_find_by_active_omits_deleted_at_wrapper_when_null() -> None:
    response = await _query_handler().FindByActive(
        slider_query_pb2.FindAllSliderRequest(page=1, page_size=10), FakeContext()
    )
    assert response.message == "Successfully fetched active slider records"
    assert response.data[0].HasField("deleted_at") is False


async def test_find_by_trashed_includes_deleted_at() -> None:
    response = await _query_handler().FindByTrashed(
        slider_query_pb2.FindAllSliderRequest(page=1, page_size=10), FakeContext()
    )
    assert response.message == "Successfully fetched trashed slider records"
    assert response.data[0].HasField("deleted_at") is True
    assert response.data[0].deleted_at.value == "2026-02-03"


async def test_find_by_id_success_no_guard() -> None:
    # slider FindById has no id==0 guard; the handler forwards to the
    # service which raises a 404 repository error for a missing row.
    response = await _query_handler().FindById(
        slider_common_pb2.FindByIdSliderRequest(id=1), FakeContext()
    )
    assert response.message == "Successfully fetched slider by ID"
    assert response.data.id == 1


async def test_create_success() -> None:
    response = await _command_handler().Create(
        slider_command_pb2.CreateSliderRequest(name="Hero", image="/img/a.png"),
        FakeContext(),
    )
    assert response.message == "Successfully created slider"
    assert response.data.id == 1
    assert response.data.name == "Hero"
    assert response.data.image == "/img/a.png"


async def test_update_rejects_zero_id() -> None:
    context = FakeContext()
    with pytest.raises(FakeAbort) as excinfo:
        await _command_handler().Update(
            slider_command_pb2.UpdateSliderRequest(id=0, name="Hero", image="/a.png"),
            context,
        )
    assert excinfo.value.code is grpc.StatusCode.INVALID_ARGUMENT
    assert excinfo.value.message == "invalid ID"
    assert context.metadata


async def test_update_success() -> None:
    response = await _command_handler().Update(
        slider_command_pb2.UpdateSliderRequest(id=1, name="Hero", image="/a.png"),
        FakeContext(),
    )
    assert response.message == "Successfully updated slider"
    assert response.data.id == 1


async def test_trashed_rejects_zero_id() -> None:
    context = FakeContext()
    with pytest.raises(FakeAbort) as excinfo:
        await _command_handler().TrashedSlider(
            slider_common_pb2.FindByIdSliderRequest(id=0), context
        )
    assert excinfo.value.code is grpc.StatusCode.INVALID_ARGUMENT
    assert excinfo.value.message == "invalid ID"


async def test_trashed_returns_delete_at_shape() -> None:
    response = await _command_handler().TrashedSlider(
        slider_common_pb2.FindByIdSliderRequest(id=1), FakeContext()
    )
    assert response.message == "Successfully trashed slider"
    assert response.data.id == 1
    assert response.data.deleted_at.value == "2026-02-03"


async def test_restore_success() -> None:
    response = await _command_handler().RestoreSlider(
        slider_common_pb2.FindByIdSliderRequest(id=1), FakeContext()
    )
    assert response.message == "Successfully restored slider"
    assert response.data.HasField("deleted_at") is False


async def test_delete_permanent_rejects_zero_id() -> None:
    context = FakeContext()
    with pytest.raises(FakeAbort) as excinfo:
        await _command_handler().DeleteSliderPermanent(
            slider_common_pb2.FindByIdSliderRequest(id=0), context
        )
    assert excinfo.value.code is grpc.StatusCode.INVALID_ARGUMENT
    assert excinfo.value.message == "invalid ID"


async def test_delete_permanent_success() -> None:
    response = await _command_handler().DeleteSliderPermanent(
        slider_common_pb2.FindByIdSliderRequest(id=1), FakeContext()
    )
    assert response.message == "Successfully deleted slider permanently"


async def test_restore_all() -> None:
    from google.protobuf import empty_pb2

    response = await _command_handler().RestoreAllSlider(
        empty_pb2.Empty(), FakeContext()
    )
    assert response.message == "Successfully restored all sliders"


async def test_delete_all_permanent() -> None:
    from google.protobuf import empty_pb2

    response = await _command_handler().DeleteAllSliderPermanent(
        empty_pb2.Empty(), FakeContext()
    )
    assert response.message == "Successfully deleted all sliders permanently"


__all__ = []

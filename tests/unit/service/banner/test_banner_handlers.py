"""Unit tests for banner gRPC handlers (in-process, no server/DB)."""

from __future__ import annotations

from datetime import date, datetime, time
from typing import Any

import grpc
import pytest

from pb.banner import banner_command_pb2, banner_common_pb2, banner_query_pb2
from pkg.database.schema.banner import (
    Banner,
    CreateBannerRow,
    GetBannerRow,
    GetBannersActiveRow,
    GetBannersRow,
    UpdateBannerRow,
)
from pkg.logger.logger import Logger
from service.banner.handler.command import BannerCommandHandler
from service.banner.handler.query import BannerQueryHandler

CREATED = datetime(2026, 1, 1, 10, 0, 0, 123000)
UPDATED = datetime(2026, 1, 2, 10, 0, 0, 456000)
DELETED = datetime(2026, 2, 3, 11, 22, 33, 789000)


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


def _row() -> GetBannersRow:
    return GetBannersRow(
        banner_id=1,
        name="Banner 1",
        start_date=date(2023, 1, 1),
        end_date=date(2023, 1, 31),
        start_time=time(8, 0),
        end_time=time(16, 0),
        is_active=True,
        created_at=CREATED,
        updated_at=UPDATED,
        total_count=11,
    )


def _active_row() -> GetBannersActiveRow:
    return GetBannersActiveRow(
        banner_id=1,
        name="Banner 1",
        start_date=date(2023, 1, 1),
        end_date=date(2023, 1, 31),
        start_time=time(8, 0),
        end_time=time(16, 0),
        is_active=True,
        created_at=CREATED,
        updated_at=UPDATED,
        deleted_at=None,
        total_count=1,
    )


def _trashed_row() -> GetBannersActiveRow:
    return GetBannersActiveRow(
        banner_id=2,
        name="Banner 2",
        start_date=date(2023, 2, 1),
        end_date=date(2023, 2, 28),
        start_time=time(9, 0),
        end_time=time(17, 0),
        is_active=False,
        created_at=CREATED,
        updated_at=UPDATED,
        deleted_at=DELETED,
        total_count=1,
    )


class FakeQueryService:
    async def find_all(self, search, page, page_size):
        return [_row()], 11

    async def find_by_id(self, banner_id):
        return GetBannerRow(
            banner_id=banner_id,
            name="Banner 1",
            start_date=date(2023, 1, 1),
            end_date=date(2023, 1, 31),
            start_time=time(8, 0),
            end_time=time(16, 0),
            is_active=True,
            created_at=CREATED,
            updated_at=UPDATED,
        )

    async def find_active(self, search, page, page_size):
        return [_active_row()], 1

    async def find_trashed(self, search, page, page_size):
        return [_trashed_row()], 1


class FakeCommandService:
    async def create(self, request):
        return CreateBannerRow(
            banner_id=1,
            name=request.name,
            start_date=date(2023, 1, 1),
            end_date=date(2023, 1, 31),
            start_time=time(8, 0),
            end_time=time(16, 0),
            is_active=request.is_active,
            created_at=CREATED,
            updated_at=UPDATED,
        )

    async def update(self, request):
        return UpdateBannerRow(
            banner_id=request.banner_id or 0,
            name=request.name,
            start_date=date(2023, 1, 1),
            end_date=date(2023, 1, 31),
            start_time=time(8, 0),
            end_time=time(16, 0),
            is_active=request.is_active,
            created_at=CREATED,
            updated_at=UPDATED,
        )

    async def trash(self, banner_id):
        return Banner(
            banner_id=banner_id,
            name="Banner 1",
            start_date=date(2023, 1, 1),
            end_date=date(2023, 1, 31),
            start_time=time(8, 0),
            end_time=time(16, 0),
            is_active=True,
            created_at=CREATED,
            updated_at=UPDATED,
            deleted_at=DELETED,
        )

    async def restore(self, banner_id):
        return Banner(
            banner_id=banner_id,
            name="Banner 1",
            start_date=date(2023, 1, 1),
            end_date=date(2023, 1, 31),
            start_time=time(8, 0),
            end_time=time(16, 0),
            is_active=True,
            created_at=CREATED,
            updated_at=UPDATED,
            deleted_at=None,
        )

    async def delete_permanent(self, banner_id):
        return None

    async def restore_all(self):
        return None

    async def delete_all_permanent(self):
        return None


def _query_handler() -> BannerQueryHandler:
    return BannerQueryHandler(FakeQueryService(), Logger("test", "error"))


def _command_handler() -> BannerCommandHandler:
    return BannerCommandHandler(FakeCommandService(), Logger("test", "error"))


async def test_find_all_banner_normalizes_and_computes_total_pages() -> None:
    request = banner_query_pb2.FindAllBannerRequest(page=0, page_size=0, search="")
    response = await _query_handler().FindAll(request, FakeContext())

    assert response.status == "success"
    assert response.message == "Successfully fetched banners"
    assert response.pagination.current_page == 1
    assert response.pagination.page_size == 10
    assert response.pagination.total_pages == 2
    assert response.pagination.total_records == 11
    assert response.data[0].start_date == "2023-01-01"
    assert response.data[0].start_time == "08:00:00"
    assert response.data[0].created_at == "2026-01-01 10:00:00.123"


async def test_find_by_id_rejects_non_positive_id() -> None:
    context = FakeContext()
    with pytest.raises(FakeAbort) as excinfo:
        await _query_handler().FindById(
            banner_common_pb2.FindByIdBannerRequest(id=0), context
        )
    assert excinfo.value.code is grpc.StatusCode.INVALID_ARGUMENT
    assert excinfo.value.message == "Invalid Banner ID"
    assert context.metadata  # ErrorResponse detail attached


async def test_find_by_id_returns_banner() -> None:
    response = await _query_handler().FindById(
        banner_common_pb2.FindByIdBannerRequest(id=1), FakeContext()
    )
    assert response.data.banner_id == 1
    assert response.message == "Successfully fetched banner"
    assert response.data.updated_at == "2026-01-02 10:00:00.456"


async def test_find_by_active_always_attaches_deleted_at_wrapper() -> None:
    """banner mapping always sets the wrapper ("" when NULL)."""
    response = await _query_handler().FindByActive(
        banner_query_pb2.FindAllBannerRequest(page=1, page_size=10), FakeContext()
    )
    assert response.data[0].HasField("deleted_at") is True
    assert response.data[0].deleted_at.value == ""


async def test_find_by_trashed_includes_deleted_at() -> None:
    response = await _query_handler().FindByTrashed(
        banner_query_pb2.FindAllBannerRequest(page=1, page_size=10), FakeContext()
    )
    assert response.data[0].deleted_at.value == "2026-02-03 11:22:33.789"


async def test_create_banner_rejects_invalid_date() -> None:
    context = FakeContext()
    with pytest.raises(FakeAbort) as excinfo:
        await _command_handler().Create(
            banner_command_pb2.CreateBannerRequest(
                name="B",
                start_date="2023/01/01",
                end_date="2023-01-31",
                start_time="08:00:00",
                end_time="16:00:00",
            ),
            context,
        )
    assert excinfo.value.code is grpc.StatusCode.INVALID_ARGUMENT
    assert excinfo.value.message == "Validation failed: invalid create banner request"


async def test_create_banner_rejects_empty_name() -> None:
    with pytest.raises(FakeAbort):
        await _command_handler().Create(
            banner_command_pb2.CreateBannerRequest(
                name="",
                start_date="2023-01-01",
                end_date="2023-01-31",
                start_time="08:00:00",
                end_time="16:00:00",
            ),
            FakeContext(),
        )


async def test_create_banner_returns_envelope() -> None:
    response = await _command_handler().Create(
        banner_command_pb2.CreateBannerRequest(
            name="New",
            start_date="2023-01-01",
            end_date="2023-01-31",
            start_time="08:00:00",
            end_time="16:00:00",
            is_active=True,
        ),
        FakeContext(),
    )
    assert response.status == "success"
    assert response.message == "Successfully created banner"
    assert response.data.name == "New"
    assert response.data.is_active is True


async def test_update_banner_rejects_non_positive_id() -> None:
    with pytest.raises(FakeAbort):
        await _command_handler().Update(
            banner_command_pb2.UpdateBannerRequest(
                banner_id=0,
                name="X",
                start_date="2023-01-01",
                end_date="2023-01-31",
                start_time="08:00:00",
                end_time="16:00:00",
            ),
            FakeContext(),
        )


async def test_update_banner_returns_envelope() -> None:
    response = await _command_handler().Update(
        banner_command_pb2.UpdateBannerRequest(
            banner_id=3,
            name="Updated",
            start_date="2023-01-01",
            end_date="2023-01-31",
            start_time="08:00:00",
            end_time="16:00:00",
        ),
        FakeContext(),
    )
    assert response.message == "Successfully updated banner"
    assert response.data.banner_id == 3
    assert response.data.name == "Updated"


async def test_trash_and_restore_report_delete_at_envelope() -> None:
    handler = _command_handler()
    trashed = await handler.Trash(
        banner_common_pb2.FindByIdBannerRequest(id=3), FakeContext()
    )
    assert trashed.message == "Successfully trashed banner"
    assert trashed.data.banner_id == 3
    assert trashed.data.deleted_at.value == "2026-02-03 11:22:33.789"

    restored = await handler.Restore(
        banner_common_pb2.FindByIdBannerRequest(id=3), FakeContext()
    )
    assert restored.message == "Successfully restored banner"
    assert restored.data.banner_id == 3


async def test_delete_permanent_has_no_data() -> None:
    response = await _command_handler().DeletePermanent(
        banner_common_pb2.FindByIdBannerRequest(id=3), FakeContext()
    )
    assert response.message == "Successfully deleted banner permanently"


async def test_bulk_commands_report_go_messages() -> None:
    handler = _command_handler()
    restore = await handler.RestoreAll(None, FakeContext())
    delete = await handler.DeleteAll(None, FakeContext())
    assert restore.message == "Successfully restored all banners"
    assert delete.message == "Successfully deleted all banners permanently"

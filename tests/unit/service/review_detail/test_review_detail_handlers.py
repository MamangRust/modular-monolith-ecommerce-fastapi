"""Unit tests for review detail gRPC handlers (in-process, no server/DB). Review detail timestamps are emitted as date-only strings (`%Y-%m-%d`), matching, the gRPC `FindById` handler *does* guard `id == 0` with a bare `invalid ID` gRPC error (400), while the command handlers (`Update`/`TrashedReviewDetail`/`RestoreReviewDetail`/ `DeleteReviewDetailPermanent`) also guard `id <= 0`. `Create` and the bulk `RestoreAll`/`DeleteAll` carry no id to guard."""

from __future__ import annotations

from datetime import datetime
from typing import Any

import grpc
import pytest
from google.protobuf import empty_pb2

from pb.review import review_query_pb2
from pb.review_detail import review_detail_command_pb2, review_detail_common_pb2
from pkg.database.schema.review_detail import (
    CreateReviewDetailRow,
    GetReviewDetailByIDRow,
    GetReviewDetailsActiveRow,
    GetReviewDetailsRow,
    ReviewDetail,
)
from pkg.logger.logger import Logger
from service.review_detail.handler.command import ReviewDetailCommandHandler
from service.review_detail.handler.query import ReviewDetailQueryHandler

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


def _row(review_detail_id: int = 1, total: int = 11) -> GetReviewDetailsRow:
    return GetReviewDetailsRow(
        review_detail_id=review_detail_id,
        review_id=10,
        type="photo",
        url="/img/a.png",
        caption="Nice",
        created_at=CREATED,
        updated_at=UPDATED,
        total_count=total,
    )


def _active_row(deleted_at: datetime | None = None) -> GetReviewDetailsActiveRow:
    return GetReviewDetailsActiveRow(
        review_detail_id=1,
        review_id=11,
        type="video",
        url="/img/b.png",
        caption="Bad",
        created_at=CREATED,
        updated_at=UPDATED,
        deleted_at=deleted_at,
        total_count=1,
    )


def _by_id_row() -> GetReviewDetailByIDRow:
    return GetReviewDetailByIDRow(
        review_detail_id=1,
        review_id=12,
        type="photo",
        url="/img/a.png",
        caption="cap",
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

    async def find_by_id(self, review_detail_id):
        return _by_id_row()


class FakeCommandService:
    async def create(self, request):
        return CreateReviewDetailRow(
            review_detail_id=1,
            review_id=request.review_id,
            type=request.type,
            url=request.url,
            caption=request.caption,
            created_at=CREATED,
            updated_at=UPDATED,
        )

    async def update(self, request):
        return GetReviewDetailByIDRow(
            review_detail_id=request.review_detail_id or 1,
            review_id=12,
            type=request.type,
            url=request.url,
            caption=request.caption,
            created_at=CREATED,
            updated_at=UPDATED,
        )

    async def trash(self, review_detail_id):
        return ReviewDetail(
            review_detail_id=review_detail_id,
            review_id=12,
            type="photo",
            url="/img/a.png",
            caption="cap",
            created_at=CREATED,
            updated_at=UPDATED,
            deleted_at=DELETED,
        )

    async def restore(self, review_detail_id):
        return ReviewDetail(
            review_detail_id=review_detail_id,
            review_id=12,
            type="photo",
            url="/img/a.png",
            caption="cap",
            created_at=CREATED,
            updated_at=UPDATED,
            deleted_at=None,
        )

    async def delete_permanent(self, review_detail_id):
        return True

    async def restore_all(self):
        return True

    async def delete_all_permanent(self):
        return True


def _logger() -> Logger:
    return Logger("test", "error")


def _query_handler() -> ReviewDetailQueryHandler:
    return ReviewDetailQueryHandler(FakeQueryService(), _logger())


def _command_handler() -> ReviewDetailCommandHandler:
    return ReviewDetailCommandHandler(FakeCommandService(), _logger())


async def test_find_all_date_only() -> None:
    request = review_query_pb2.FindAllReviewRequest(page=0, page_size=0, search="")
    response = await _query_handler().FindAll(request, FakeContext())

    assert response.status == "success"
    assert response.message == "Successfully fetched review details"
    assert response.pagination.current_page == 1
    assert response.pagination.page_size == 10
    assert response.pagination.total_pages == 2
    assert response.pagination.total_records == 11
    # Date-only layout.
    assert response.data[0].created_at == "2026-01-02"
    assert response.data[0].updated_at == "2026-01-03"
    assert response.data[0].type == "photo"


async def test_find_by_active_omits_deleted_at_wrapper_when_null() -> None:
    response = await _query_handler().FindByActive(
        review_query_pb2.FindAllReviewRequest(page=1, page_size=10), FakeContext()
    )
    assert response.message == "Successfully fetched active review details"
    assert response.data[0].HasField("deleted_at") is False


async def test_find_by_trashed_includes_deleted_at() -> None:
    response = await _query_handler().FindByTrashed(
        review_query_pb2.FindAllReviewRequest(page=1, page_size=10), FakeContext()
    )
    assert response.message == "Successfully fetched trashed review details"
    assert response.data[0].HasField("deleted_at") is True
    assert response.data[0].deleted_at.value == "2026-02-03"


async def test_find_by_id_success() -> None:
    response = await _query_handler().FindById(
        review_detail_common_pb2.FindByIdReviewDetailRequest(id=1), FakeContext()
    )
    assert response.message == "Successfully fetched review detail"
    assert response.data.id == 1


async def test_find_by_id_rejects_zero_id() -> None:
    context = FakeContext()
    with pytest.raises(FakeAbort) as excinfo:
        await _query_handler().FindById(
            review_detail_common_pb2.FindByIdReviewDetailRequest(id=0), context
        )
    assert excinfo.value.code is grpc.StatusCode.INVALID_ARGUMENT
    assert excinfo.value.message == "invalid ID"
    assert context.metadata


async def test_create_success() -> None:
    response = await _command_handler().Create(
        review_detail_command_pb2.CreateReviewDetailRequest(
            review_id=5, type="photo", url="/img/a.png", caption="cap"
        ),
        FakeContext(),
    )
    assert response.message == "Successfully created review detail"
    assert response.data.id == 1
    assert response.data.review_id == 5
    assert response.data.type == "photo"


async def test_update_rejects_zero_id() -> None:
    context = FakeContext()
    with pytest.raises(FakeAbort) as excinfo:
        await _command_handler().Update(
            review_detail_command_pb2.UpdateReviewDetailRequest(
                review_detail_id=0, type="photo", url="/a.png", caption="cap"
            ),
            context,
        )
    assert excinfo.value.code is grpc.StatusCode.INVALID_ARGUMENT
    assert excinfo.value.message == "invalid ID"
    assert context.metadata


async def test_update_success() -> None:
    response = await _command_handler().Update(
        review_detail_command_pb2.UpdateReviewDetailRequest(
            review_detail_id=1, type="photo", url="/a.png", caption="cap"
        ),
        FakeContext(),
    )
    assert response.message == "Successfully updated review detail"
    assert response.data.id == 1


async def test_trashed_rejects_zero_id() -> None:
    context = FakeContext()
    with pytest.raises(FakeAbort) as excinfo:
        await _command_handler().TrashedReviewDetail(
            review_detail_common_pb2.FindByIdReviewDetailRequest(id=0), context
        )
    assert excinfo.value.code is grpc.StatusCode.INVALID_ARGUMENT
    assert excinfo.value.message == "invalid ID"


async def test_trashed_returns_delete_at_shape() -> None:
    response = await _command_handler().TrashedReviewDetail(
        review_detail_common_pb2.FindByIdReviewDetailRequest(id=1), FakeContext()
    )
    assert response.message == "Successfully trashed review detail"
    assert response.data.id == 1
    assert response.data.deleted_at.value == "2026-02-03"


async def test_restore_success() -> None:
    response = await _command_handler().RestoreReviewDetail(
        review_detail_common_pb2.FindByIdReviewDetailRequest(id=1), FakeContext()
    )
    assert response.message == "Successfully restored review detail"
    assert response.data.HasField("deleted_at") is False


async def test_delete_permanent_rejects_zero_id() -> None:
    context = FakeContext()
    with pytest.raises(FakeAbort) as excinfo:
        await _command_handler().DeleteReviewDetailPermanent(
            review_detail_common_pb2.FindByIdReviewDetailRequest(id=0), context
        )
    assert excinfo.value.code is grpc.StatusCode.INVALID_ARGUMENT
    assert excinfo.value.message == "invalid ID"


async def test_delete_permanent_success() -> None:
    response = await _command_handler().DeleteReviewDetailPermanent(
        review_detail_common_pb2.FindByIdReviewDetailRequest(id=1), FakeContext()
    )
    assert response.message == "Successfully deleted review detail permanently"


async def test_restore_all() -> None:
    response = await _command_handler().RestoreAllReviewDetail(
        empty_pb2.Empty(), FakeContext()
    )
    assert response.message == "Successfully restored all review details"


async def test_delete_all_permanent() -> None:
    response = await _command_handler().DeleteAllReviewDetailPermanent(
        empty_pb2.Empty(), FakeContext()
    )
    assert response.message == "Successfully deleted all review details permanently"


__all__ = []

"""Unit tests for the review gRPC handlers."""

from __future__ import annotations

from datetime import datetime
from typing import Any

import grpc
import pytest

from pb.review import review_command_pb2, review_common_pb2, review_query_pb2
from pkg.database.schema.review import (
    GetReviewByIDRow,
    GetReviewByProductIdRow,
    GetReviewsActiveRow,
    GetReviewsRow,
    Review,
    ReviewRow,
)
from pkg.logger.logger import Logger
from service.review.handler.review_command import ReviewCommandHandler
from service.review.handler.review_query import ReviewQueryHandler
from shared.errors.review_errors import (
    err_grpc_invalid_id,
    err_grpc_validate_update_review,
)

CREATED = datetime(2026, 1, 2, 3, 4, 5)
UPDATED = datetime(2026, 1, 3, 4, 5, 6)
TRASHED = datetime(2026, 2, 1, 6, 7, 8)


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


def _logger() -> Logger:
    return Logger("test", "error")


# ---- query handler ----


def _list_row(review_id: int = 1, total: int = 11) -> GetReviewsRow:
    return GetReviewsRow(
        review_id=review_id,
        user_id=5,
        product_id=10,
        name="John",
        comment="Produk bagus!",
        rating=5,
        created_at=CREATED,
        updated_at=UPDATED,
        total_count=total,
    )


def _active_row(review_id: int = 1, deleted_at: datetime | None = None) -> GetReviewsActiveRow:
    return GetReviewsActiveRow(
        review_id=review_id,
        user_id=5,
        product_id=10,
        name="John",
        comment="Produk bagus!",
        rating=5,
        created_at=CREATED,
        updated_at=UPDATED,
        deleted_at=deleted_at,
        total_count=11,
    )


def _detail_row(review_id: int = 1) -> GetReviewByProductIdRow:
    return GetReviewByProductIdRow(
        review_id=review_id,
        user_id=5,
        product_id=10,
        name="John",
        comment="Produk bagus!",
        rating=5,
        created_at=CREATED,
        updated_at=UPDATED,
        deleted_at=None,
        total_count=11,
        review_details=[
            {
                "detail_id": 9,
                "type": "photo",
                "url": "/img/a.png",
                "caption": "cap",
                "created_at": "2026-01-02T03:04:05Z",
            }
        ],
    )


class FakeQueryService:
    def __init__(self) -> None:
        self.last: Any = None

    async def find_all(self, request):
        self.last = request
        return [_list_row()], 11

    async def find_by_product(self, request):
        self.last = request
        return [_detail_row()], 11

    async def find_by_merchant(self, request):
        self.last = request
        return [_detail_row()], 11

    async def find_active(self, request):
        self.last = request
        return [_active_row()], 11

    async def find_trashed(self, request):
        self.last = request
        return [_active_row(deleted_at=TRASHED)], 11

    async def find_by_id(self, review_id: int) -> GetReviewByIDRow:
        self.last = review_id
        return GetReviewByIDRow(
            review_id=review_id,
            user_id=5,
            product_id=10,
            name="John",
            comment="Produk bagus!",
            rating=5,
            created_at=CREATED,
            updated_at=UPDATED,
        )


def _query_handler(service: FakeQueryService | None = None) -> ReviewQueryHandler:
    return ReviewQueryHandler(service or FakeQueryService(), _logger())


async def test_query_find_all_date_only_and_clamps() -> None:
    response = await _query_handler().FindAll(
        review_query_pb2.FindAllReviewRequest(page=0, page_size=0), FakeContext()
    )
    assert response.message == "Successfully fetched reviews"
    assert response.pagination.current_page == 1
    assert response.pagination.page_size == 10
    assert response.pagination.total_records == 11
    assert response.data[0].id == 1
    assert response.data[0].created_at == "2026-01-02"
    assert response.data[0].updated_at == "2026-01-03"


async def test_query_find_by_product_detail_format_and_nested_detail() -> None:
    service = FakeQueryService()
    response = await _query_handler(service).FindByProduct(
        review_query_pb2.FindAllReviewProductRequest(
            product_id=10, page=2, page_size=5, search="john"
        ),
        FakeContext(),
    )
    assert response.message == "Successfully fetched product reviews"
    assert service.last.product_id == 10
    assert service.last.rating == 0  # proto never supplies a rating
    assert service.last.page == 2 and service.last.page_size == 5
    assert response.data[0].created_at == "2026-01-02 03:04:05.000"
    assert response.data[0].review_detail.id == 9
    assert response.data[0].review_detail.caption == "cap"


async def test_query_find_by_merchant_forwards_merchant() -> None:
    service = FakeQueryService()
    response = await _query_handler(service).FindByMerchant(
        review_query_pb2.FindAllReviewMerchantRequest(merchant_id=3), FakeContext()
    )
    assert response.message == "Successfully fetched merchant reviews"
    assert service.last.merchant_id == 3
    assert service.last.rating == 0


async def test_query_find_by_active_always_sets_deleted_at_wrapper() -> None:
    response = await _query_handler().FindByActive(
        review_query_pb2.FindAllReviewRequest(), FakeContext()
    )
    assert response.message == "Successfully fetched active reviews"
    assert response.data[0].HasField("deleted_at")
    assert response.data[0].deleted_at.value == ""


async def test_query_find_by_trashed_sets_deleted_at_date() -> None:
    response = await _query_handler().FindByTrashed(
        review_query_pb2.FindAllReviewRequest(), FakeContext()
    )
    assert response.message == "Successfully fetched trashed reviews"
    assert response.data[0].deleted_at.value == "2026-02-01"


# ---- command handler ----


def _created_row(review_id: int = 9) -> ReviewRow:
    return ReviewRow(
        review_id=review_id,
        user_id=5,
        product_id=10,
        name="",
        comment="Produk bagus!",
        rating=5,
        created_at=CREATED,
        updated_at=UPDATED,
    )


def _review(deleted_at: datetime | None) -> Review:
    return Review(
        review_id=7,
        user_id=5,
        product_id=10,
        name="John",
        comment="Produk bagus!",
        rating=5,
        created_at=CREATED,
        updated_at=UPDATED,
        deleted_at=deleted_at,
    )


class FakeCommandService:
    def __init__(self) -> None:
        self.last_create: Any = None
        self.last_update: Any = None
        self.calls: list[str] = []

    async def create(self, request):
        self.last_create = request
        return _created_row()

    async def update(self, request):
        self.last_update = request
        return _created_row(review_id=request.review_id or 0)

    async def trash(self, review_id):
        self.calls.append(f"trash:{review_id}")
        return _review(TRASHED)

    async def restore(self, review_id):
        self.calls.append(f"restore:{review_id}")
        return _review(None)

    async def delete_permanent(self, review_id):
        self.calls.append(f"delete:{review_id}")
        return True

    async def restore_all(self):
        self.calls.append("restore_all")
        return True

    async def delete_all(self):
        self.calls.append("delete_all")
        return True


def _command_handler(
    service: FakeCommandService | None = None,
) -> ReviewCommandHandler:
    return ReviewCommandHandler(service or FakeCommandService(), _logger())


async def test_command_create_ignores_proto_name() -> None:
    service = FakeCommandService()
    response = await _command_handler(service).Create(
        review_command_pb2.CreateReviewRequest(
            user_id=5, product_id=10, name="ignored", comment="Produk bagus!", rating=5
        ),
        FakeContext(),
    )
    assert response.message == "Successfully created review"
    assert response.data.id == 9
    assert service.last_create.user_id == 5
    assert service.last_create.product_id == 10
    assert service.last_create.rating == 5


async def test_command_update_success_and_invalid_id() -> None:
    service = FakeCommandService()
    response = await _command_handler(service).Update(
        review_command_pb2.UpdateReviewRequest(
            review_id=7, comment="updated", rating=4
        ),
        FakeContext(),
    )
    assert response.message == "Successfully updated review"
    assert service.last_update.review_id == 7
    assert service.last_update.rating == 4

    context = FakeContext()
    with pytest.raises(FakeAbort) as excinfo:
        await _command_handler().Update(
            review_command_pb2.UpdateReviewRequest(review_id=0, comment="c", rating=4),
            context,
        )
    assert excinfo.value.code is grpc.StatusCode.INVALID_ARGUMENT
    assert excinfo.value.message == err_grpc_invalid_id.message


async def test_command_update_validation_failure() -> None:
    context = FakeContext()
    with pytest.raises(FakeAbort) as excinfo:
        await _command_handler().Update(
            review_command_pb2.UpdateReviewRequest(review_id=7, comment="", rating=0),
            context,
        )
    assert excinfo.value.code is grpc.StatusCode.INVALID_ARGUMENT
    assert excinfo.value.message == err_grpc_validate_update_review.message


async def test_command_trash_and_restore_set_deleted_at() -> None:
    service = FakeCommandService()
    trashed = await _command_handler(service).TrashedReview(
        review_common_pb2.FindByIdReviewRequest(id=7), FakeContext()
    )
    assert trashed.message == "Successfully trashed review"
    assert trashed.data.deleted_at.value == "2026-02-01"

    restored = await _command_handler(service).RestoreReview(
        review_common_pb2.FindByIdReviewRequest(id=7), FakeContext()
    )
    assert restored.message == "Successfully restored review"
    assert restored.data.deleted_at.value == ""


async def test_command_single_row_guards_invalid_id() -> None:
    for rpc, request in [
        (
            "TrashedReview",
            review_common_pb2.FindByIdReviewRequest(id=0),
        ),
        (
            "RestoreReview",
            review_common_pb2.FindByIdReviewRequest(id=0),
        ),
        (
            "DeleteReviewPermanent",
            review_common_pb2.FindByIdReviewRequest(id=0),
        ),
    ]:
        with pytest.raises(FakeAbort) as excinfo:
            await getattr(_command_handler(), rpc)(request, FakeContext())
        assert excinfo.value.code is grpc.StatusCode.INVALID_ARGUMENT
        assert excinfo.value.message == err_grpc_invalid_id.message


async def test_command_delete_permanent_and_bulk() -> None:
    service = FakeCommandService()
    handler = _command_handler(service)

    deleted = await handler.DeleteReviewPermanent(
        review_common_pb2.FindByIdReviewRequest(id=7), FakeContext()
    )
    assert deleted.message == "Successfully deleted review permanently"
    assert service.calls[-1] == "delete:7"

    restored_all = await handler.RestoreAllReview(
        review_common_pb2.FindByIdReviewRequest(), FakeContext()
    )
    assert restored_all.message == "Successfully restored all reviews"

    deleted_all = await handler.DeleteAllReviewPermanent(
        review_common_pb2.FindByIdReviewRequest(), FakeContext()
    )
    assert deleted_all.message == "Successfully deleted all reviews permanently"
    assert service.calls[-2:] == ["restore_all", "delete_all"]


__all__ = []

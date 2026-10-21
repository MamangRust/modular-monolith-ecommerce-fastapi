"""Unit tests for the gateway review transport handler. `normalize_pagination` Matches the expected gateway clamp. `create` rejects a missing/non-positive JWT subject with 401 `Unauthorized` (`user_id` context check); the query methods do NOT require a subject (review query routes never read it). keeps no gateway-level cache."""

from __future__ import annotations

from typing import Any

import grpc
import pytest

from pb.review import (
    review_command_pb2,
    review_common_pb2,
    review_query_pb2,
)
from service.apigateway.app.client import ServiceConnections
from service.apigateway.handler.review.handler import (
    ReviewHandler,
    normalize_pagination,
)
from shared.errors import AppError


def _rpc_error(code: grpc.StatusCode, details: str) -> grpc.aio.AioRpcError:
    return grpc.aio.AioRpcError(
        code, grpc.aio.Metadata(), grpc.aio.Metadata(), details=details
    )


class FakeQuery:
    def __init__(self) -> None:
        self.last: Any = None

    async def FindAll(self, request: Any, timeout: float | None = None) -> Any:
        self.last = request
        message = review_common_pb2.ApiResponsePaginationReview(
            status="success", message="Successfully fetched reviews"
        )
        message.data.add(id=1, user_id=5, name="John")
        message.pagination.total_records = 1
        return message

    async def FindByProduct(self, request: Any, timeout: float | None = None) -> Any:
        self.last = request
        message = review_common_pb2.ApiResponsePaginationReviewDetail(
            status="success", message="Successfully fetched product reviews"
        )
        message.data.add(id=1, name="John")
        return message

    async def FindByMerchant(self, request: Any, timeout: float | None = None) -> Any:
        self.last = request
        message = review_common_pb2.ApiResponsePaginationReviewDetail(
            status="success", message="Successfully fetched merchant reviews"
        )
        message.data.add(id=1, name="John")
        return message

    async def FindByActive(self, request: Any, timeout: float | None = None) -> Any:
        self.last = request
        message = review_common_pb2.ApiResponsePaginationReviewDeleteAt(
            status="success", message="Successfully fetched active reviews"
        )
        message.data.add(id=1, name="John")
        return message

    async def FindByTrashed(self, request: Any, timeout: float | None = None) -> Any:
        self.last = request
        message = review_common_pb2.ApiResponsePaginationReviewDeleteAt(
            status="success", message="Successfully fetched trashed reviews"
        )
        message.data.add(id=1, name="John")
        return message


class FakeCommand:
    def __init__(self, fail_create: bool = False) -> None:
        self.last: Any = None
        self.fail_create = fail_create

    async def Create(self, request: Any, timeout: float | None = None) -> Any:
        self.last = request
        if self.fail_create:
            raise _rpc_error(grpc.StatusCode.NOT_FOUND, "product not found")
        message = review_common_pb2.ApiResponseReview(
            status="success", message="Successfully created review"
        )
        message.data.id = 9
        message.data.user_id = request.user_id
        return message

    async def Update(self, request: Any, timeout: float | None = None) -> Any:
        self.last = request
        message = review_common_pb2.ApiResponseReview(
            status="success", message="Successfully updated review"
        )
        message.data.id = request.review_id
        return message

    async def TrashedReview(self, request: Any, timeout: float | None = None) -> Any:
        self.last = request
        return review_common_pb2.ApiResponseReviewDeleteAt(
            status="success", message="Successfully trashed review"
        )

    async def RestoreReview(self, request: Any, timeout: float | None = None) -> Any:
        self.last = request
        return review_common_pb2.ApiResponseReviewDeleteAt(
            status="success", message="Successfully restored review"
        )

    async def DeleteReviewPermanent(
        self, request: Any, timeout: float | None = None
    ) -> Any:
        self.last = request
        return review_common_pb2.ApiResponseReviewDelete(
            status="success", message="Successfully deleted review permanently"
        )

    async def RestoreAllReview(self, request: Any, timeout: float | None = None) -> Any:
        self.last = request
        return review_common_pb2.ApiResponseReviewAll(
            status="success", message="Successfully restored all reviews"
        )

    async def DeleteAllReviewPermanent(
        self, request: Any, timeout: float | None = None
    ) -> Any:
        self.last = request
        return review_common_pb2.ApiResponseReviewAll(
            status="success", message="Successfully deleted all reviews permanently"
        )


def _handler() -> tuple[ReviewHandler, grpc.aio.Channel]:
    channel = grpc.aio.insecure_channel("127.0.0.1:1")
    connections = ServiceConnections(
        channels={"review": channel},
        addresses={"review": "127.0.0.1:1"},
    )
    return ReviewHandler(connections), channel


@pytest.mark.parametrize(
    ("page", "page_size", "expected"),
    [
        (1, 10, (1, 10)),
        (0, 0, (1, 10)),
        (-5, -1, (1, 10)),
        (3, 0, (3, 10)),
        (0, 25, (1, 25)),
    ],
)
def test_normalize_pagination(page: int, page_size: int, expected: tuple[int, int]) -> None:
    assert normalize_pagination(page, page_size) == expected


async def test_query_methods_build_requests_and_map() -> None:
    handler, channel = _handler()
    fake: Any = FakeQuery()
    handler._query = fake
    try:
        response = await handler.find_all(0, 0, "john")
        assert isinstance(fake.last, review_query_pb2.FindAllReviewRequest)
        assert fake.last.page == 1 and fake.last.page_size == 10
        assert fake.last.search == "john"
        assert response.data is not None
        assert response.data[0].id == 1

        await handler.find_by_product(10, 1, 10, "")
        assert isinstance(fake.last, review_query_pb2.FindAllReviewProductRequest)
        assert fake.last.product_id == 10

        await handler.find_by_merchant(3, 1, 10, "")
        assert isinstance(fake.last, review_query_pb2.FindAllReviewMerchantRequest)
        assert fake.last.merchant_id == 3

        await handler.find_by_active(1, 10, "")
        assert isinstance(fake.last, review_query_pb2.FindAllReviewRequest)

        await handler.find_by_trashed(1, 10, "")
        assert isinstance(fake.last, review_query_pb2.FindAllReviewRequest)
    finally:
        await channel.close()


@pytest.mark.parametrize("user_id", [None, 0, -1])
async def test_create_rejects_missing_subject(user_id: int | None) -> None:
    handler, channel = _handler()
    try:
        with pytest.raises(AppError) as excinfo:
            await handler.create(user_id, 10, 5, "c")
        assert excinfo.value.code == 401
        assert excinfo.value.message == "Unauthorized"
    finally:
        await channel.close()


async def test_create_builds_request_with_jwt_owner() -> None:
    handler, channel = _handler()
    fake: Any = FakeCommand()
    handler._command = fake
    try:
        response = await handler.create(5, 10, 5, "Produk bagus!")
        assert isinstance(fake.last, review_command_pb2.CreateReviewRequest)
        assert fake.last.user_id == 5
        assert fake.last.product_id == 10
        assert fake.last.rating == 5
        assert fake.last.comment == "Produk bagus!"
        assert response.data is not None
        assert response.data.id == 9
    finally:
        await channel.close()


async def test_create_maps_grpc_error() -> None:
    handler, channel = _handler()
    handler._command = FakeCommand(fail_create=True)
    try:
        with pytest.raises(AppError) as excinfo:
            await handler.create(5, 2_000_000_000, 5, "c")
        assert excinfo.value.code == 404
        assert excinfo.value.message == "product not found"
    finally:
        await channel.close()


async def test_command_methods_build_requests() -> None:
    handler, channel = _handler()
    fake: Any = FakeCommand()
    handler._command = fake
    try:
        await handler.update(7, 4, "updated")
        assert isinstance(fake.last, review_command_pb2.UpdateReviewRequest)
        assert fake.last.review_id == 7 and fake.last.rating == 4

        for method, message in [
            ("trash", "Successfully trashed review"),
            ("restore", "Successfully restored review"),
        ]:
            response = await getattr(handler, method)(7)
            assert isinstance(fake.last, review_common_pb2.FindByIdReviewRequest)
            assert fake.last.id == 7
            assert response.message == message

        deleted = await handler.delete_permanent(7)
        assert deleted.message == "Successfully deleted review permanently"

        restored_all = await handler.restore_all()
        assert restored_all.message == "Successfully restored all reviews"

        deleted_all = await handler.delete_all_permanent()
        assert deleted_all.message == "Successfully deleted all reviews permanently"
    finally:
        await channel.close()


__all__ = []

"""Unit tests for the gateway cart transport handler. `normalize_pagination` Matches the expected gateway clamp. Every method rejects a missing/non-positive JWT subject with 401 `Unauthorized` (`user_id` context check). The owner id is taken from the argument (route reads `state.user_id`) and never from the body. keeps no gateway-level cache."""

from __future__ import annotations

from typing import Any

import grpc
import pytest

from pb.cart import (
    cart_command_pb2,
    cart_common_pb2,
    cart_query_pb2,
)
from service.apigateway.app.client import ServiceConnections
from service.apigateway.handler.cart.handler import CartHandler, normalize_pagination
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
        message = cart_common_pb2.ApiResponsePaginationCart(
            status="success", message="Successfully fetched cart items"
        )
        message.data.add(id=1, user_id=request.user_id, name="Galaxy S24")
        message.pagination.total_records = 1
        return message


class FakeCommand:
    def __init__(self, fail_create: bool = False) -> None:
        self.last: Any = None
        self.fail_create = fail_create

    async def Create(self, request: Any, timeout: float | None = None) -> Any:
        self.last = request
        if self.fail_create:
            raise _rpc_error(grpc.StatusCode.INVALID_ARGUMENT, "Insufficient product stock")
        message = cart_common_pb2.ApiResponseCart(
            status="success", message="Successfully created cart"
        )
        message.data.id = 9
        message.data.user_id = request.user_id
        return message

    async def Delete(self, request: Any, timeout: float | None = None) -> Any:
        self.last = request
        return cart_common_pb2.ApiResponseCartDelete(
            status="success", message="Successfully deleted cart item permanently"
        )

    async def DeleteAll(self, request: Any, timeout: float | None = None) -> Any:
        self.last = request
        return cart_common_pb2.ApiResponseCartAll(
            status="success", message="Successfully deleted all cart items permanently"
        )


def _handler() -> tuple[CartHandler, grpc.aio.Channel]:
    channel = grpc.aio.insecure_channel("127.0.0.1:1")
    connections = ServiceConnections(
        channels={"cart": channel},
        addresses={"cart": "127.0.0.1:1"},
    )
    return CartHandler(connections), channel


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
def test_normalize_pagination(
    page: int, page_size: int, expected: tuple[int, int]
) -> None:
    assert normalize_pagination(page, page_size) == expected


@pytest.mark.parametrize("user_id", [None, 0, -1])
async def test_find_all_rejects_missing_subject(user_id: int | None) -> None:
    handler, channel = _handler()
    try:
        with pytest.raises(AppError) as excinfo:
            await handler.find_all(user_id, 1, 10, "")
        assert excinfo.value.code == 401
        assert excinfo.value.message == "Unauthorized"
    finally:
        await channel.close()


async def test_find_all_builds_request_and_maps() -> None:
    handler, channel = _handler()
    fake: Any = FakeQuery()
    handler._query = fake
    try:
        response = await handler.find_all(5, 0, 0, "galaxy")
        assert isinstance(fake.last, cart_query_pb2.FindAllCartRequest)
        assert fake.last.user_id == 5
        assert fake.last.page == 1 and fake.last.page_size == 10
        assert fake.last.search == "galaxy"
        assert response.data is not None
        assert response.data[0].id == 1
    finally:
        await channel.close()


@pytest.mark.parametrize("user_id", [None, 0])
async def test_create_rejects_missing_subject(user_id: int | None) -> None:
    handler, channel = _handler()
    try:
        with pytest.raises(AppError) as excinfo:
            await handler.create(user_id, 10, 2)
        assert excinfo.value.code == 401
    finally:
        await channel.close()


async def test_create_builds_request_with_jwt_owner() -> None:
    handler, channel = _handler()
    fake: Any = FakeCommand()
    handler._command = fake
    try:
        response = await handler.create(5, 10, 2)
        assert isinstance(fake.last, cart_command_pb2.CreateCartRequest)
        assert fake.last.user_id == 5
        assert fake.last.product_id == 10
        assert fake.last.quantity == 2
        assert response.data is not None
        assert response.data.id == 9
    finally:
        await channel.close()


async def test_create_maps_grpc_error() -> None:
    handler, channel = _handler()
    handler._command = FakeCommand(fail_create=True)
    try:
        with pytest.raises(AppError) as excinfo:
            await handler.create(5, 10, 999)
        assert excinfo.value.code == 400
        assert excinfo.value.message == "Insufficient product stock"
    finally:
        await channel.close()


async def test_delete_rejects_missing_subject_and_builds_request() -> None:
    handler, channel = _handler()
    fake: Any = FakeCommand()
    handler._command = fake
    try:
        with pytest.raises(AppError) as excinfo:
            await handler.delete(None, 3)
        assert excinfo.value.code == 401

        response = await handler.delete(5, 3)
        assert isinstance(fake.last, cart_command_pb2.DeleteCartRequest)
        assert fake.last.user_id == 5 and fake.last.cart_id == 3
        assert response.message == "Successfully deleted cart item permanently"
    finally:
        await channel.close()


async def test_delete_all_builds_request() -> None:
    handler, channel = _handler()
    fake: Any = FakeCommand()
    handler._command = fake
    try:
        with pytest.raises(AppError) as excinfo:
            await handler.delete_all(0, [1])
        assert excinfo.value.code == 401

        response = await handler.delete_all(5, [3, 4])
        assert isinstance(fake.last, cart_command_pb2.DeleteAllCartRequest)
        assert fake.last.user_id == 5
        assert list(fake.last.cart_ids) == [3, 4]
        assert response.message == "Successfully deleted all cart items permanently"
    finally:
        await channel.close()


__all__ = []

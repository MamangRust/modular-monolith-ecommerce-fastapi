"""Unit tests for the cart gRPC handlers."""

from __future__ import annotations

from datetime import datetime
from typing import Any

import grpc
import pytest

from pb.cart import cart_command_pb2, cart_query_pb2
from pkg.database.schema.cart import Cart, GetCartsRow
from pkg.logger.logger import Logger
from service.cart.handler.cart_command import CartCommandHandler
from service.cart.handler.cart_query import CartQueryHandler
from shared.errors.cart_errors import (
    err_grpc_validate_create_cart,
    err_grpc_validate_delete_all_cart,
    err_grpc_validate_delete_cart,
)

CREATED = datetime(2026, 1, 2, 3, 4, 5)
UPDATED = datetime(2026, 1, 3, 4, 5, 6)


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


def _list_row(cart_id: int = 1, total: int = 11) -> GetCartsRow:
    return GetCartsRow(
        cart_id=cart_id,
        user_id=5,
        product_id=10,
        name="Galaxy S24",
        price=1200,
        image="galaxy-s24.jpg",
        quantity=2,
        weight=200,
        created_at=CREATED,
        updated_at=UPDATED,
        total_count=total,
    )


class FakeQueryService:
    def __init__(self) -> None:
        self.last_request: Any = None

    async def find_all(self, request):
        self.last_request = request
        return [_list_row()], 11


def _query_handler(service: FakeQueryService | None = None) -> CartQueryHandler:
    return CartQueryHandler(service or FakeQueryService(), _logger())


async def test_query_find_all_formats_date_only_and_clamps_paging() -> None:
    response = await _query_handler().FindAll(
        cart_query_pb2.FindAllCartRequest(user_id=5, page=0, page_size=0),
        FakeContext(),
    )
    assert response.message == "Successfully fetched cart items"
    assert response.pagination.current_page == 1
    assert response.pagination.page_size == 10
    assert response.pagination.total_records == 11
    assert response.data[0].id == 1
    assert response.data[0].user_id == 5
    assert response.data[0].created_at == "2026-01-02"
    assert response.data[0].updated_at == "2026-01-03"


async def test_query_find_all_forwards_user_and_search() -> None:
    service = FakeQueryService()
    await _query_handler(service).FindAll(
        cart_query_pb2.FindAllCartRequest(
            user_id=7, page=2, page_size=5, search="galaxy"
        ),
        FakeContext(),
    )
    assert service.last_request.user_id == 7
    assert service.last_request.page == 2
    assert service.last_request.page_size == 5
    assert service.last_request.search == "galaxy"


# ---- command handler ----


class FakeCommandService:
    def __init__(self) -> None:
        self.last_create: Any = None
        self.last_delete: Any = None
        self.last_delete_all: Any = None

    async def create(self, request):
        self.last_create = request
        return Cart(
            cart_id=9,
            user_id=request.user_id,
            product_id=request.product_id,
            name="Galaxy S24",
            price=1200,
            image="galaxy-s24.jpg",
            quantity=request.quantity,
            weight=200,
            created_at=CREATED,
            updated_at=UPDATED,
        )

    async def delete_permanent(self, request):
        self.last_delete = request
        return True

    async def delete_all(self, request):
        self.last_delete_all = request
        return True


def _command_handler(
    service: FakeCommandService | None = None,
) -> CartCommandHandler:
    return CartCommandHandler(service or FakeCommandService(), _logger())


async def test_command_create_success() -> None:
    service = FakeCommandService()
    response = await _command_handler(service).Create(
        cart_command_pb2.CreateCartRequest(product_id=10, user_id=5, quantity=2),
        FakeContext(),
    )
    assert response.message == "Successfully created cart"
    assert response.data.id == 9
    assert response.data.product_id == 10
    assert response.data.quantity == 2
    assert response.data.created_at == "2026-01-02"
    assert service.last_create.user_id == 5


async def test_command_create_validation_failure() -> None:
    context = FakeContext()
    with pytest.raises(FakeAbort) as excinfo:
        await _command_handler().Create(
            cart_command_pb2.CreateCartRequest(product_id=10, user_id=5, quantity=0),
            context,
        )
    assert excinfo.value.code is grpc.StatusCode.INVALID_ARGUMENT
    assert excinfo.value.message == err_grpc_validate_create_cart.message


async def test_command_delete_success() -> None:
    service = FakeCommandService()
    response = await _command_handler(service).Delete(
        cart_command_pb2.DeleteCartRequest(cart_id=3, user_id=5),
        FakeContext(),
    )
    assert response.message == "Successfully deleted cart item permanently"
    assert service.last_delete.cart_id == 3
    assert service.last_delete.user_id == 5


async def test_command_delete_validation_failure() -> None:
    context = FakeContext()
    with pytest.raises(FakeAbort) as excinfo:
        await _command_handler().Delete(
            cart_command_pb2.DeleteCartRequest(cart_id=0, user_id=5), context
        )
    assert excinfo.value.code is grpc.StatusCode.INVALID_ARGUMENT
    assert excinfo.value.message == err_grpc_validate_delete_cart.message


async def test_command_delete_all_success() -> None:
    service = FakeCommandService()
    response = await _command_handler(service).DeleteAll(
        cart_command_pb2.DeleteAllCartRequest(user_id=5, cart_ids=[3, 4]),
        FakeContext(),
    )
    assert response.message == "Successfully deleted all cart items permanently"
    assert list(service.last_delete_all.cart_ids) == [3, 4]
    assert service.last_delete_all.user_id == 5


async def test_command_delete_all_validation_failure() -> None:
    context = FakeContext()
    with pytest.raises(FakeAbort) as excinfo:
        await _command_handler().DeleteAll(
            cart_command_pb2.DeleteAllCartRequest(user_id=5, cart_ids=[]), context
        )
    assert excinfo.value.code is grpc.StatusCode.INVALID_ARGUMENT
    assert excinfo.value.message == err_grpc_validate_delete_all_cart.message


__all__ = []

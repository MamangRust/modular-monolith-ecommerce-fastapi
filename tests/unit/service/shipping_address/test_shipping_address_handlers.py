"""Unit tests for shipping address gRPC handlers (in-process, no server/DB). The handler has no request validator (unlike order_item), so `CreateShipping`/ `UpdateShipping` only fail at the repository. The id-guarded operations raise the bare `ErrGrpcInvalidID`. Timestamps are date-only (`%Y-%m-%d`), matching category; `shipping_cost` is truncated to an int on the wire."""

from __future__ import annotations

from datetime import datetime
from typing import Any

import grpc
import pytest

from pb.shipping_address import (
    shipping_address_command_pb2,
    shipping_address_common_pb2,
    shipping_address_query_pb2,
)
from pkg.database.schema.shipping_address import (
    CreateShippingAddressRow,
    GetShippingAddressActiveRow,
    GetShippingAddressByOrderIDRow,
    GetShippingAddressRow,
    GetShippingByIDRow,
    ShippingAddress,
    UpdateShippingAddressRow,
)
from pkg.logger.logger import Logger
from service.shipping_address.handler.command import ShippingCommandHandler
from service.shipping_address.handler.query import ShippingQueryHandler

CREATED = datetime(2026, 1, 2, 3, 4, 5)
UPDATED = datetime(2026, 1, 3, 4, 5, 6)
DELETED = datetime(2026, 2, 3, 11, 22, 33)


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


def _row(shipping_address_id: int = 1, total: int = 11) -> GetShippingAddressRow:
    return GetShippingAddressRow(
        shipping_address_id=shipping_address_id,
        order_id=10,
        alamat="Jl. Merdeka 1",
        provinsi="DKI Jakarta",
        negara="Indonesia",
        kota="Jakarta",
        courier="JNE",
        shipping_method="REG",
        shipping_cost=12.75,
        created_at=CREATED,
        updated_at=UPDATED,
        total_count=total,
    )


def _active_row(deleted_at: datetime | None = None) -> GetShippingAddressActiveRow:
    return GetShippingAddressActiveRow(
        shipping_address_id=1,
        order_id=10,
        alamat="Jl. Merdeka 1",
        provinsi="DKI Jakarta",
        negara="Indonesia",
        kota="Jakarta",
        courier="JNE",
        shipping_method="REG",
        shipping_cost=12.75,
        created_at=CREATED,
        updated_at=UPDATED,
        deleted_at=deleted_at,
        total_count=1,
    )


def _by_id_row() -> GetShippingByIDRow:
    return GetShippingByIDRow(
        shipping_address_id=1,
        order_id=10,
        alamat="Jl. Merdeka 1",
        provinsi="DKI Jakarta",
        negara="Indonesia",
        kota="Jakarta",
        courier="JNE",
        shipping_method="REG",
        shipping_cost=12.75,
        created_at=CREATED,
        updated_at=UPDATED,
    )


def _by_order_row() -> GetShippingAddressByOrderIDRow:
    return GetShippingAddressByOrderIDRow(
        shipping_address_id=1,
        order_id=10,
        alamat="Jl. Merdeka 1",
        provinsi="DKI Jakarta",
        negara="Indonesia",
        kota="Jakarta",
        courier="JNE",
        shipping_method="REG",
        shipping_cost=12.75,
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

    async def find_by_id(self, shipping_id):
        return _by_id_row()

    async def find_by_order(self, order_id):
        return _by_order_row()


class FakeCommandService:
    async def create(self, request):
        return CreateShippingAddressRow(
            shipping_address_id=1,
            order_id=request.order_id,
            alamat=request.alamat,
            provinsi=request.provinsi,
            negara=request.negara,
            kota=request.kota,
            courier=request.courier,
            shipping_method=request.shipping_method,
            shipping_cost=request.shipping_cost,
            created_at=CREATED,
            updated_at=UPDATED,
        )

    async def update(self, request):
        return UpdateShippingAddressRow(
            shipping_address_id=request.shipping_id,
            order_id=request.order_id,
            alamat=request.alamat,
            provinsi=request.provinsi,
            negara=request.negara,
            kota=request.kota,
            courier=request.courier,
            shipping_method=request.shipping_method,
            shipping_cost=request.shipping_cost,
            created_at=CREATED,
            updated_at=UPDATED,
        )

    async def trash(self, shipping_id):
        return ShippingAddress(
            shipping_address_id=shipping_id,
            order_id=10,
            alamat="Jl. Merdeka 1",
            provinsi="DKI Jakarta",
            negara="Indonesia",
            kota="Jakarta",
            courier="JNE",
            shipping_method="REG",
            shipping_cost=12.75,
            created_at=CREATED,
            updated_at=UPDATED,
            deleted_at=DELETED,
        )

    async def restore(self, shipping_id):
        return ShippingAddress(
            shipping_address_id=shipping_id,
            order_id=10,
            alamat="Jl. Merdeka 1",
            provinsi="DKI Jakarta",
            negara="Indonesia",
            kota="Jakarta",
            courier="JNE",
            shipping_method="REG",
            shipping_cost=12.75,
            created_at=CREATED,
            updated_at=UPDATED,
            deleted_at=None,
        )

    async def delete_permanent(self, shipping_id):
        return True

    async def delete_by_order_id_permanent(self, order_id):
        return True

    async def restore_all(self):
        return True

    async def delete_all(self):
        return True


def _logger() -> Logger:
    return Logger("test", "error")


def _query_handler() -> ShippingQueryHandler:
    return ShippingQueryHandler(FakeQueryService(), _logger())


def _command_handler() -> ShippingCommandHandler:
    return ShippingCommandHandler(FakeCommandService(), _logger())


async def test_find_all_normalizes_and_formats_date_only() -> None:
    request = shipping_address_query_pb2.FindAllShippingRequest(
        page=0, page_size=0, search=""
    )
    response = await _query_handler().FindAll(request, FakeContext())

    assert response.status == "success"
    assert response.message == "Successfully fetched shipping addresses"
    assert response.pagination.current_page == 1
    assert response.pagination.page_size == 10
    assert response.pagination.total_pages == 2
    assert response.pagination.total_records == 11
    # Date-only layout, like category (not banner/order_item's millisecond one).
    assert response.data[0].created_at == "2026-01-02"
    assert response.data[0].updated_at == "2026-01-03"
    # shipping_cost is truncated to on the wire.
    assert response.data[0].shippingCost == 12
    assert response.data[0].shippingMethod == "REG"
    assert response.data[0].courier == "JNE"


async def test_find_by_active_omits_deleted_at_wrapper_when_null() -> None:
    response = await _query_handler().FindByActive(
        shipping_address_query_pb2.FindAllShippingRequest(page=1, page_size=10),
        FakeContext(),
    )
    assert response.message == "Successfully fetched active shipping addresses"
    assert response.data[0].HasField("deleted_at") is False


async def test_find_by_trashed_includes_deleted_at() -> None:
    response = await _query_handler().FindByTrashed(
        shipping_address_query_pb2.FindAllShippingRequest(page=1, page_size=10),
        FakeContext(),
    )
    assert response.message == "Successfully fetched trashed shipping addresses"
    assert response.data[0].HasField("deleted_at") is True
    assert response.data[0].deleted_at.value == "2026-02-03"


async def test_find_by_id_success() -> None:
    response = await _query_handler().FindById(
        shipping_address_common_pb2.FindByIdShippingRequest(id=1), FakeContext()
    )
    assert response.message == "Successfully fetched shipping address"
    assert response.data.id == 1


async def test_find_by_id_rejects_zero_id() -> None:
    context = FakeContext()
    with pytest.raises(FakeAbort) as excinfo:
        await _query_handler().FindById(
            shipping_address_common_pb2.FindByIdShippingRequest(id=0), context
        )
    assert excinfo.value.code is grpc.StatusCode.INVALID_ARGUMENT
    assert excinfo.value.message == "invalid ID"
    assert context.metadata


async def test_find_by_order_success() -> None:
    response = await _query_handler().FindByOrder(
        shipping_address_common_pb2.FindByIdShippingRequest(id=10), FakeContext()
    )
    assert response.message == "Successfully fetched shipping address by order ID"
    assert response.data.order_id == 10


async def test_find_by_order_rejects_zero_id() -> None:
    context = FakeContext()
    with pytest.raises(FakeAbort) as excinfo:
        await _query_handler().FindByOrder(
            shipping_address_common_pb2.FindByIdShippingRequest(id=0), context
        )
    assert excinfo.value.code is grpc.StatusCode.INVALID_ARGUMENT
    assert excinfo.value.message == "invalid ID"


async def test_create_shipping_success() -> None:
    response = await _command_handler().CreateShipping(
        shipping_address_command_pb2.CreateShippingAddressRequest(
            order_id=10,
            alamat="Jl. Merdeka 1",
            provinsi="DKI Jakarta",
            kota="Jakarta",
            courier="JNE",
            shipping_method="REG",
            shipping_cost=12000,
            negara="Indonesia",
        ),
        FakeContext(),
    )
    assert response.message == "Successfully created shipping address"
    assert response.data.order_id == 10
    assert response.data.shippingCost == 12000


async def test_update_shipping_success() -> None:
    response = await _command_handler().UpdateShipping(
        shipping_address_command_pb2.UpdateShippingAddressRequest(
            shipping_id=1, order_id=10, kota="Bandung", shipping_cost=9000
        ),
        FakeContext(),
    )
    assert response.message == "Successfully updated shipping address"
    assert response.data.id == 1


async def test_trashed_shipping_rejects_zero_id() -> None:
    context = FakeContext()
    with pytest.raises(FakeAbort) as excinfo:
        await _command_handler().TrashedShipping(
            shipping_address_common_pb2.FindByIdShippingRequest(id=0), context
        )
    assert excinfo.value.code is grpc.StatusCode.INVALID_ARGUMENT
    assert excinfo.value.message == "invalid ID"


async def test_trashed_shipping_returns_delete_at_shape() -> None:
    response = await _command_handler().TrashedShipping(
        shipping_address_common_pb2.FindByIdShippingRequest(id=1), FakeContext()
    )
    assert response.message == "Successfully trashed shipping address"
    assert response.data.id == 1
    assert response.data.deleted_at.value == "2026-02-03"


async def test_restore_shipping_success() -> None:
    response = await _command_handler().RestoreShipping(
        shipping_address_common_pb2.FindByIdShippingRequest(id=1), FakeContext()
    )
    assert response.message == "Successfully restored shipping address"
    # Restored row has no deleted_at, so the wrapper stays unset.
    assert response.data.HasField("deleted_at") is False


async def test_delete_shipping_permanent() -> None:
    response = await _command_handler().DeleteShippingPermanent(
        shipping_address_common_pb2.FindByIdShippingRequest(id=1), FakeContext()
    )
    assert response.message == "Successfully deleted shipping address permanently"


async def test_restore_all_shipping() -> None:
    from google.protobuf import empty_pb2

    response = await _command_handler().RestoreAllShipping(
        empty_pb2.Empty(), FakeContext()
    )
    assert response.message == "Successfully restored all shipping addresses"


async def test_delete_all_shipping_permanent() -> None:
    from google.protobuf import empty_pb2

    response = await _command_handler().DeleteAllShippingPermanent(
        empty_pb2.Empty(), FakeContext()
    )
    assert response.message == "Successfully deleted all shipping addresses permanently"


async def test_delete_shipping_by_order_permanent() -> None:
    response = await _command_handler().DeleteShippingByOrderPermanent(
        shipping_address_common_pb2.FindByIdShippingRequest(id=7), FakeContext()
    )
    assert (
        response.message
        == "Successfully deleted shipping addresses by order permanently"
    )


async def test_delete_shipping_by_order_permanent_rejects_zero_id() -> None:
    context = FakeContext()
    with pytest.raises(FakeAbort) as excinfo:
        await _command_handler().DeleteShippingByOrderPermanent(
            shipping_address_common_pb2.FindByIdShippingRequest(id=0), context
        )
    assert excinfo.value.code is grpc.StatusCode.INVALID_ARGUMENT
    assert excinfo.value.message == "invalid ID"

"""Unit tests for the gateway merchant_business transport handler. `normalize_pagination` Matches the expected gateway clamp (no `page_size` cap). `require_positive_id` guards every path-id route with 400 `Invalid ID` — including the query `find_by_id` (matching, unlike merchant_detail whose query route uses `id is required`). The three list RPCs are built from the shared `FindAllMerchantRequest` (from `pb.merchant`). The `DeletePermanent`/`RestoreAll`/`DeleteAllPermanent` responses reuse the merchant envelope (`ApiResponse[None]`)."""

from __future__ import annotations

from typing import Any

import grpc
import pytest

from pb.merchant import merchant_common_pb2, merchant_query_pb2
from pb.merchant_business import merchant_business_common_pb2
from service.apigateway.app.client import ServiceConnections
from service.apigateway.handler.merchant_business.handler import (
    MerchantBusinessHandler,
    normalize_pagination,
    require_positive_id,
)
from shared.errors import AppError


class FakeQuery:
    def __init__(self) -> None:
        self.last: Any = None
        self.last_method = ""

    async def FindAll(self, request: Any, timeout: float | None = None) -> Any:
        self.last, self.last_method = request, "FindAll"
        message = (
            merchant_business_common_pb2.ApiResponsePaginationMerchantBusiness(
                status="success", message="Successfully fetched merchant"
            )
        )
        message.data.add(id=1, merchant_id=10, business_type="Toko Elektronik")
        message.pagination.total_records = 1
        return message

    async def FindById(self, request: Any, timeout: float | None = None) -> Any:
        self.last, self.last_method = request, "FindById"
        message = merchant_business_common_pb2.ApiResponseMerchantBusiness(
            status="success", message="Successfully fetched merchant"
        )
        message.data.id = request.id
        message.data.business_type = "Toko Elektronik"
        return message

    async def FindByActive(self, request: Any, timeout: float | None = None) -> Any:
        self.last, self.last_method = request, "FindByActive"
        message = (
            merchant_business_common_pb2.ApiResponsePaginationMerchantBusinessDeleteAt(
                status="success", message="Successfully fetched active merchant"
            )
        )
        message.data.add(id=1, merchant_id=10, business_type="Toko Elektronik")
        return message

    async def FindByTrashed(self, request: Any, timeout: float | None = None) -> Any:
        self.last, self.last_method = request, "FindByTrashed"
        message = (
            merchant_business_common_pb2.ApiResponsePaginationMerchantBusinessDeleteAt(
                status="success", message="Successfully fetched trashed merchant"
            )
        )
        message.data.add(id=1, merchant_id=10, business_type="Toko Elektronik")
        message.data[0].deleted_at.value = "2026-02-01 05:06:07.000"
        return message


class FakeCommand:
    def __init__(self) -> None:
        self.last: Any = None
        self.last_method = ""

    async def Create(self, request: Any, timeout: float | None = None) -> Any:
        self.last, self.last_method = request, "Create"
        message = merchant_business_common_pb2.ApiResponseMerchantBusiness(
            status="success", message="Successfully created merchant business"
        )
        message.data.id = 9
        message.data.merchant_id = request.merchant_id
        return message

    async def Update(self, request: Any, timeout: float | None = None) -> Any:
        self.last, self.last_method = request, "Update"
        message = merchant_business_common_pb2.ApiResponseMerchantBusiness(
            status="success", message="Successfully updated merchant business"
        )
        message.data.id = request.merchant_business_info_id
        return message

    async def TrashedMerchantBusiness(
        self, request: Any, timeout: float | None = None
    ) -> Any:
        self.last, self.last_method = request, "TrashedMerchantBusiness"
        message = merchant_business_common_pb2.ApiResponseMerchantBusinessDeleteAt(
            status="success", message="Successfully trashed merchant business"
        )
        message.data.id = request.id
        message.data.deleted_at.value = "2026-02-01 05:06:07.000"
        return message

    async def RestoreMerchantBusiness(
        self, request: Any, timeout: float | None = None
    ) -> Any:
        self.last, self.last_method = request, "RestoreMerchantBusiness"
        message = merchant_business_common_pb2.ApiResponseMerchantBusinessDeleteAt(
            status="success", message="Successfully restored merchant business"
        )
        message.data.id = request.id
        return message

    async def DeleteMerchantBusinessPermanent(
        self, request: Any, timeout: float | None = None
    ) -> Any:
        self.last, self.last_method = request, "DeleteMerchantBusinessPermanent"
        return merchant_common_pb2.ApiResponseMerchantDelete(
            status="success",
            message="Successfully deleted merchant business permanently",
        )

    async def RestoreAllMerchantBusiness(
        self, request: Any, timeout: float | None = None
    ) -> Any:
        self.last, self.last_method = request, "RestoreAllMerchantBusiness"
        return merchant_common_pb2.ApiResponseMerchantAll(
            status="success",
            message="Successfully restored all trashed merchant businesses",
        )

    async def DeleteAllMerchantBusinessPermanent(
        self, request: Any, timeout: float | None = None
    ) -> Any:
        self.last, self.last_method = request, "DeleteAllMerchantBusinessPermanent"
        return merchant_common_pb2.ApiResponseMerchantAll(
            status="success",
            message="Successfully deleted all merchant businesses permanently",
        )


@pytest.mark.parametrize(
    ("page", "page_size", "expected"),
    [
        (1, 10, (1, 10)),
        (0, 0, (1, 10)),
        (-5, -1, (1, 10)),
        (3, 0, (3, 10)),
        (0, 25, (1, 25)),
        # No page_size cap in the gateway (unlike the request DTO validator).
        (1, 500, (1, 500)),
    ],
)
def test_normalize_pagination(
    page: int, page_size: int, expected: tuple[int, int]
) -> None:
    assert normalize_pagination(page, page_size) == expected


@pytest.mark.parametrize("value", [0, -1, -2_000_000_000])
def test_require_positive_id_rejects_non_positive(value: int) -> None:
    with pytest.raises(AppError) as excinfo:
        require_positive_id(value)
    assert excinfo.value.code == 400
    assert excinfo.value.type == "BAD_REQUEST"
    assert excinfo.value.message == "Invalid ID"


@pytest.mark.parametrize("value", [1, 42])
def test_require_positive_id_accepts_positive(value: int) -> None:
    require_positive_id(value)


def _handler() -> tuple[MerchantBusinessHandler, grpc.aio.Channel]:
    channel = grpc.aio.insecure_channel("127.0.0.1:1")
    connections = ServiceConnections(
        channels={"merchant_business": channel},
        addresses={"merchant_business": "127.0.0.1:1"},
    )
    return MerchantBusinessHandler(connections), channel


async def test_handler_builds_query_and_command_stubs() -> None:
    handler, channel = _handler()
    try:
        assert handler._query is not None
        assert handler._command is not None
    finally:
        await channel.close()


async def test_query_list_uses_shared_find_all_request() -> None:
    handler, channel = _handler()
    fake: Any = FakeQuery()
    handler._query = fake
    try:
        await handler.find_all(1, 10, "toko")
        assert isinstance(fake.last, merchant_query_pb2.FindAllMerchantRequest)
        assert fake.last.search == "toko"

        await handler.find_by_active(1, 10, "")
        assert fake.last_method == "FindByActive"
        assert isinstance(fake.last, merchant_query_pb2.FindAllMerchantRequest)

        await handler.find_by_trashed(1, 10, "")
        assert fake.last_method == "FindByTrashed"
        assert isinstance(fake.last, merchant_query_pb2.FindAllMerchantRequest)
    finally:
        await channel.close()


async def test_query_find_by_id_rejects_non_positive() -> None:
    handler, channel = _handler()
    try:
        with pytest.raises(AppError) as excinfo:
            await handler.find_by_id(0)
        # Unlike merchant_detail, the merchant_business query route also guards
        # with `Invalid ID`.
        assert excinfo.value.code == 400
        assert excinfo.value.message == "Invalid ID"
    finally:
        await channel.close()


async def test_query_find_by_id_success_maps_response() -> None:
    handler, channel = _handler()
    fake: Any = FakeQuery()
    handler._query = fake
    try:
        response = await handler.find_by_id(7)
        assert response.status == "success"
        assert response.data.id == 7
        assert fake.last.id == 7
    finally:
        await channel.close()


async def test_command_create_success_maps_response() -> None:
    handler, channel = _handler()
    fake: Any = FakeCommand()
    handler._command = fake
    try:
        response = await handler.create(
            5, "Toko Elektronik", "01.234", 2010, 15, "https://technostore.com"
        )
        assert response.status == "success"
        assert response.data.id == 9
        assert response.data.merchant_id == 5
        assert fake.last.merchant_id == 5
        assert fake.last.established_year == 2010
    finally:
        await channel.close()


async def test_command_update_success_maps_response() -> None:
    handler, channel = _handler()
    handler._command = FakeCommand()
    try:
        response = await handler.update(
            7, "Retail Gadget", "04.567", 2018, 8, "https://gadgethub.com"
        )
        assert response.data.id == 7
    finally:
        await channel.close()


async def test_command_trash_restore_map_delete_at() -> None:
    handler, channel = _handler()
    handler._command = FakeCommand()
    try:
        trashed = await handler.trash(3)
        assert trashed.data.id == 3
        assert trashed.data.deleted_at == "2026-02-01 05:06:07.000"

        restored = await handler.restore(3)
        assert restored.data.id == 3
        # No wrapper attached -> "" (takes the address of a zero string).
        assert restored.data.deleted_at == ""
    finally:
        await channel.close()


@pytest.mark.parametrize(
    "invoke",
    [
        lambda handler: handler.update(0, "Toko", "t", 2010, 15, ""),
        lambda handler: handler.trash(0),
        lambda handler: handler.restore(0),
        lambda handler: handler.delete_permanent(0),
    ],
)
async def test_command_id_routes_reject_non_positive(invoke) -> None:
    handler, channel = _handler()
    try:
        with pytest.raises(AppError) as excinfo:
            await invoke(handler)
        assert excinfo.value.code == 400
        assert excinfo.value.message == "Invalid ID"
    finally:
        await channel.close()


async def test_command_delete_and_bulk_use_merchant_envelope() -> None:
    handler, channel = _handler()
    handler._command = FakeCommand()
    try:
        deleted = await handler.delete_permanent(3)
        assert deleted.message == "Successfully deleted merchant business permanently"

        restored_all = await handler.restore_all()
        assert (
            restored_all.message
            == "Successfully restored all trashed merchant businesses"
        )

        deleted_all = await handler.delete_all_permanent()
        assert (
            deleted_all.message
            == "Successfully deleted all merchant businesses permanently"
        )
    finally:
        await channel.close()


__all__ = []

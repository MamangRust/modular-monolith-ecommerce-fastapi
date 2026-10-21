"""Unit tests for the gateway product transport handler. `normalize_pagination` Matches the expected gateway clamp. `create`/`update` resolve the uploaded image to `image_product` ("" when no file) and clean the stored file up when the RPC fails. keeps no gateway-level cache."""

from __future__ import annotations

from typing import Any

import grpc
import pytest

from pb.product import (
    product_common_pb2,
    product_query_pb2,
)
from service.apigateway.app.client import ServiceConnections
from service.apigateway.handler.product.handler import (
    ProductHandler,
    normalize_pagination,
)
from shared.errors import AppError


def _rpc_error(code: grpc.StatusCode, details: str) -> grpc.aio.AioRpcError:
    return grpc.aio.AioRpcError(
        code, grpc.aio.Metadata(), grpc.aio.Metadata(), details=details
    )


class FakeUpload:
    def __init__(self, path: str = "uploads/products/pic.jpg") -> None:
        self.path = path
        self.cleaned: list[str] = []
        self.last_dir = ""
        self.last_file: Any = None

    async def process_image_upload(self, upload_dir, file, required):
        self.last_dir = upload_dir
        self.last_file = file
        return self.path

    def cleanup_image_on_failure(self, image_path: str) -> None:
        self.cleaned.append(image_path)


class FakeQuery:
    def __init__(self) -> None:
        self.last: Any = None
        self.last_method = ""

    async def FindAll(self, request: Any, timeout: float | None = None) -> Any:
        self.last, self.last_method = request, "FindAll"
        message = product_common_pb2.ApiResponsePaginationProduct(
            status="success", message="Successfully fetched products"
        )
        message.data.add(id=1, merchant_id=10, name="Galaxy S24")
        message.pagination.total_records = 1
        return message

    async def FindById(self, request: Any, timeout: float | None = None) -> Any:
        self.last, self.last_method = request, "FindById"
        message = product_common_pb2.ApiResponseProduct(
            status="success", message="Successfully fetched product"
        )
        message.data.id = request.id
        message.data.name = "Galaxy S24"
        return message

    async def FindByMerchant(self, request: Any, timeout: float | None = None) -> Any:
        self.last, self.last_method = request, "FindByMerchant"
        message = product_common_pb2.ApiResponsePaginationProduct(
            status="success", message="Successfully fetched merchant products"
        )
        message.data.add(id=1, merchant_id=request.merchant_id)
        return message

    async def FindByCategory(self, request: Any, timeout: float | None = None) -> Any:
        self.last, self.last_method = request, "FindByCategory"
        message = product_common_pb2.ApiResponsePaginationProduct(
            status="success", message="Successfully fetched category products"
        )
        message.data.add(id=1, category_id=3)
        return message

    async def FindByActive(self, request: Any, timeout: float | None = None) -> Any:
        self.last, self.last_method = request, "FindByActive"
        message = product_common_pb2.ApiResponsePaginationProductDeleteAt(
            status="success", message="Successfully fetched active products"
        )
        message.data.add(id=1, merchant_id=10)
        return message

    async def FindByTrashed(self, request: Any, timeout: float | None = None) -> Any:
        self.last, self.last_method = request, "FindByTrashed"
        message = product_common_pb2.ApiResponsePaginationProductDeleteAt(
            status="success", message="Successfully fetched trashed products"
        )
        message.data.add(id=1, merchant_id=10)
        message.data[0].deleted_at.value = "2026-02-01 05:06:07.000"
        return message


class FakeCommand:
    def __init__(self, fail_create: bool = False, fail_update: bool = False) -> None:
        self.last: Any = None
        self.last_method = ""
        self.fail_create = fail_create
        self.fail_update = fail_update

    async def Create(self, request: Any, timeout: float | None = None) -> Any:
        self.last, self.last_method = request, "Create"
        if self.fail_create:
            raise _rpc_error(
                grpc.StatusCode.INVALID_ARGUMENT,
                "validation failed: invalid create product request",
            )
        message = product_common_pb2.ApiResponseProduct(
            status="success", message="Successfully created product"
        )
        message.data.id = 9
        message.data.merchant_id = request.merchant_id
        return message

    async def Update(self, request: Any, timeout: float | None = None) -> Any:
        self.last, self.last_method = request, "Update"
        if self.fail_update:
            raise _rpc_error(grpc.StatusCode.NOT_FOUND, "product not found")
        message = product_common_pb2.ApiResponseProduct(
            status="success", message="Successfully updated product"
        )
        message.data.id = request.product_id
        return message

    async def TrashedProduct(self, request: Any, timeout: float | None = None) -> Any:
        self.last, self.last_method = request, "TrashedProduct"
        message = product_common_pb2.ApiResponseProductDeleteAt(
            status="success", message="Successfully trashed product"
        )
        message.data.id = request.id
        message.data.deleted_at.value = "2026-02-01 05:06:07.000"
        return message

    async def RestoreProduct(self, request: Any, timeout: float | None = None) -> Any:
        self.last, self.last_method = request, "RestoreProduct"
        message = product_common_pb2.ApiResponseProductDeleteAt(
            status="success", message="Successfully restored product"
        )
        message.data.id = request.id
        return message

    async def DeleteProductPermanent(
        self, request: Any, timeout: float | None = None
    ) -> Any:
        self.last, self.last_method = request, "DeleteProductPermanent"
        return product_common_pb2.ApiResponseProductDelete(
            status="success", message="Successfully deleted product permanently"
        )

    async def RestoreAllProduct(self, request: Any, timeout: float | None = None) -> Any:
        self.last, self.last_method = request, "RestoreAllProduct"
        return product_common_pb2.ApiResponseProductAll(
            status="success", message="Successfully restored all products"
        )

    async def DeleteAllProductPermanent(
        self, request: Any, timeout: float | None = None
    ) -> Any:
        self.last, self.last_method = request, "DeleteAllProductPermanent"
        return product_common_pb2.ApiResponseProductAll(
            status="success", message="Successfully deleted all products permanently"
        )


def _handler() -> tuple[ProductHandler, grpc.aio.Channel, FakeUpload]:
    channel = grpc.aio.insecure_channel("127.0.0.1:1")
    connections = ServiceConnections(
        channels={"product": channel},
        addresses={"product": "127.0.0.1:1"},
    )
    upload = FakeUpload()
    return ProductHandler(connections, upload), channel, upload  # type: ignore[arg-type]


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


async def test_query_find_all_builds_request_and_maps() -> None:
    handler, channel, _ = _handler()
    fake: Any = FakeQuery()
    handler._query = fake
    try:
        response = await handler.find_all(0, 0, "galaxy")
        assert isinstance(fake.last, product_query_pb2.FindAllProductRequest)
        assert fake.last.page == 1 and fake.last.page_size == 10
        assert fake.last.search == "galaxy"
        assert response.message == "Successfully fetched products"
        assert response.data is not None
        assert response.data[0].id == 1
    finally:
        await channel.close()


async def test_query_find_by_id_rejects_non_positive() -> None:
    handler, channel, _ = _handler()
    try:
        with pytest.raises(AppError) as excinfo:
            await handler.find_by_id(0)
        assert excinfo.value.code == 400
        assert excinfo.value.message == "Invalid Product ID"
    finally:
        await channel.close()


async def test_query_find_by_id_success() -> None:
    handler, channel, _ = _handler()
    fake: Any = FakeQuery()
    handler._query = fake
    try:
        response = await handler.find_by_id(7)
        assert fake.last.id == 7
        assert response.data is not None
        assert response.data.id == 7
    finally:
        await channel.close()


async def test_query_find_by_merchant_rejects_non_positive() -> None:
    handler, channel, _ = _handler()
    try:
        with pytest.raises(AppError) as excinfo:
            await handler.find_by_merchant(0, 1, 10, "")
        assert excinfo.value.code == 400
        assert excinfo.value.message == "Invalid Merchant ID"
    finally:
        await channel.close()


async def test_query_find_by_merchant_builds_request() -> None:
    handler, channel, _ = _handler()
    fake: Any = FakeQuery()
    handler._query = fake
    try:
        await handler.find_by_merchant(5, 0, 0, "galaxy")
        assert isinstance(fake.last, product_query_pb2.FindAllProductMerchantRequest)
        assert fake.last.merchant_id == 5
        assert fake.last.page == 1 and fake.last.page_size == 10
        # does not forward the price filters on this route.
        assert fake.last.min_price == 0 and fake.last.max_price == 0
    finally:
        await channel.close()


async def test_query_find_by_category_requires_name() -> None:
    handler, channel, _ = _handler()
    try:
        with pytest.raises(AppError) as excinfo:
            await handler.find_by_category("", 1, 10, "")
        assert excinfo.value.code == 400
        assert excinfo.value.message == "Category Name is required"
    finally:
        await channel.close()


async def test_query_find_by_category_builds_request() -> None:
    handler, channel, _ = _handler()
    fake: Any = FakeQuery()
    handler._query = fake
    try:
        await handler.find_by_category("Electronics", 1, 10, "galaxy")
        assert isinstance(fake.last, product_query_pb2.FindAllProductCategoryRequest)
        assert fake.last.category_name == "Electronics"
    finally:
        await channel.close()


async def test_query_active_and_trashed_map_delete_at() -> None:
    handler, channel, _ = _handler()
    fake: Any = FakeQuery()
    handler._query = fake
    try:
        active = await handler.find_by_active(1, 10, "")
        assert fake.last_method == "FindByActive"
        assert active.data is not None
        assert active.data[0].deleted_at == ""

        trashed = await handler.find_by_trashed(1, 10, "")
        assert fake.last_method == "FindByTrashed"
        assert trashed.data is not None
        assert trashed.data[0].deleted_at == "2026-02-01 05:06:07.000"
    finally:
        await channel.close()


async def test_command_create_uploads_image_and_maps() -> None:
    handler, channel, upload = _handler()
    fake: Any = FakeCommand()
    handler._command = fake
    try:
        response = await handler.create(
            5, 3, "Galaxy S24", "desc", 1200, 5, "Samsung", 200, 5, "galaxy-s24", object()
        )
        assert upload.last_dir == "uploads/products"
        assert fake.last.image_product == "uploads/products/pic.jpg"
        assert fake.last.merchant_id == 5
        assert response.data is not None
        assert response.data.id == 9
    finally:
        await channel.close()


async def test_command_create_without_image_sends_empty_path() -> None:
    handler, channel, _ = _handler()
    fake: Any = FakeCommand()
    handler._command = fake
    try:
        await handler.create(
            5, 3, "Galaxy S24", "desc", 1200, 5, "Samsung", 200, 5, "galaxy-s24", None
        )
        assert fake.last.image_product == ""
    finally:
        await channel.close()


async def test_command_create_cleans_image_on_rpc_failure() -> None:
    handler, channel, upload = _handler()
    handler._command = FakeCommand(fail_create=True)
    try:
        with pytest.raises(AppError) as excinfo:
            await handler.create(
                5,
                3,
                "Galaxy S24",
                "desc",
                1200,
                5,
                "Samsung",
                200,
                5,
                "galaxy-s24",
                object(),
            )
        assert excinfo.value.code == 400
        assert upload.cleaned == ["uploads/products/pic.jpg"]
    finally:
        await channel.close()


async def test_command_update_rejects_non_positive_id() -> None:
    handler, channel, _ = _handler()
    try:
        with pytest.raises(AppError) as excinfo:
            await handler.update(
                0, 5, 3, "n", "d", 1, 1, "b", 1, 5, "s", None
            )
        assert excinfo.value.code == 400
        assert excinfo.value.message == "Invalid ID"
    finally:
        await channel.close()


async def test_command_update_cleans_image_on_rpc_failure() -> None:
    handler, channel, upload = _handler()
    handler._command = FakeCommand(fail_update=True)
    try:
        with pytest.raises(AppError) as excinfo:
            await handler.update(
                7, 5, 3, "n", "d", 1, 1, "b", 1, 5, "s", object()
            )
        assert excinfo.value.code == 404
        assert upload.cleaned == ["uploads/products/pic.jpg"]
    finally:
        await channel.close()


async def test_command_update_success_maps() -> None:
    handler, channel, _ = _handler()
    handler._command = FakeCommand()
    try:
        response = await handler.update(
            7, 5, 3, "n", "d", 1, 1, "b", 1, 5, "s", None
        )
        assert response.data is not None
        assert response.data.id == 7
    finally:
        await channel.close()


@pytest.mark.parametrize(
    "invoke",
    [
        lambda handler: handler.trash(0),
        lambda handler: handler.restore(0),
        lambda handler: handler.delete_permanent(0),
    ],
)
async def test_command_id_routes_reject_non_positive(invoke) -> None:
    handler, channel, _ = _handler()
    try:
        with pytest.raises(AppError) as excinfo:
            await invoke(handler)
        assert excinfo.value.code == 400
        assert excinfo.value.message == "Invalid ID"
    finally:
        await channel.close()


async def test_command_trash_restore_map_delete_at() -> None:
    handler, channel, _ = _handler()
    handler._command = FakeCommand()
    try:
        trashed = await handler.trash(3)
        assert trashed.data is not None
        assert trashed.data.id == 3
        assert trashed.data.deleted_at == "2026-02-01 05:06:07.000"

        restored = await handler.restore(3)
        assert restored.data is not None
        assert restored.data.id == 3
        assert restored.data.deleted_at == ""
    finally:
        await channel.close()


async def test_command_permanent_and_bulk_envelopes() -> None:
    handler, channel, _ = _handler()
    handler._command = FakeCommand()
    try:
        deleted = await handler.delete_permanent(3)
        assert deleted.message == "Successfully deleted product permanently"

        restored_all = await handler.restore_all()
        assert restored_all.message == "Successfully restored all products"

        deleted_all = await handler.delete_all_permanent()
        assert deleted_all.message == "Successfully deleted all products permanently"
    finally:
        await channel.close()


__all__ = []

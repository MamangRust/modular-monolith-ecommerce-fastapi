"""Unit tests for the product gRPC handlers."""

from __future__ import annotations

from datetime import datetime
from typing import Any

import grpc
import pytest
from google.protobuf import empty_pb2

from pb.product import (
    product_command_pb2,
    product_common_pb2,
    product_query_pb2,
)
from pkg.database.schema.product import (
    AdjustProductStockRow,
    GetProductsActiveRow,
    GetProductsRow,
    ProductRow,
)
from pkg.logger.logger import Logger
from service.product.handler.product_command import ProductCommandHandler
from service.product.handler.product_query import ProductQueryHandler
from shared.errors.product_errors import (
    err_grpc_validate_create_product,
    err_grpc_validate_update_product,
)

CREATED = datetime(2026, 1, 2, 3, 4, 5)
UPDATED = datetime(2026, 1, 3, 4, 5, 6)
DELETED = datetime(2026, 2, 1, 5, 6, 7)


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


def _list_row(product_id: int = 1, total: int = 11) -> GetProductsRow:
    return GetProductsRow(
        product_id=product_id,
        merchant_id=10,
        category_id=3,
        name="Galaxy S24",
        description="desc",
        price=1200,
        count_in_stock=5,
        brand="Samsung",
        weight=200,
        rating=4.5,
        slug_product="galaxy-s24",
        image_product="uploads/products/galaxy-s24.jpg",
        created_at=CREATED,
        updated_at=UPDATED,
        total_count=total,
    )


def _active_row(deleted_at: datetime | None = None) -> GetProductsActiveRow:
    return GetProductsActiveRow(
        product_id=1,
        merchant_id=10,
        category_id=3,
        name="Galaxy S24",
        description="desc",
        price=1200,
        count_in_stock=5,
        brand="Samsung",
        weight=200,
        rating=4.5,
        slug_product="galaxy-s24",
        image_product="uploads/products/galaxy-s24.jpg",
        created_at=CREATED,
        updated_at=UPDATED,
        deleted_at=deleted_at,
        total_count=1,
    )


def _by_id_row() -> ProductRow:
    return ProductRow(
        product_id=1,
        merchant_id=10,
        category_id=3,
        name="Galaxy S24",
        description="desc",
        price=1200,
        count_in_stock=5,
        brand="Samsung",
        weight=200,
        rating=4.5,
        slug_product="galaxy-s24",
        image_product="uploads/products/galaxy-s24.jpg",
        created_at=CREATED,
        updated_at=UPDATED,
    )


class FakeQueryService:
    def __init__(self) -> None:
        self.last_by_merchant: tuple[Any, ...] | None = None
        self.last_by_category: tuple[Any, ...] | None = None
        self.last_by_id: int | None = None

    async def find_all(self, search, page, page_size):
        return [_list_row()], 11

    async def find_active(self, search, page, page_size):
        return [_active_row()], 1

    async def find_trashed(self, search, page, page_size):
        return [_active_row(deleted_at=DELETED)], 1

    async def find_by_merchant(
        self, merchant_id, category_id, search, min_price, max_price, page, page_size
    ):
        self.last_by_merchant = (
            merchant_id,
            category_id,
            search,
            min_price,
            max_price,
            page,
            page_size,
        )
        return [_list_row()], 11

    async def find_by_category(
        self, category_name, search, min_price, max_price, page, page_size
    ):
        self.last_by_category = (
            category_name,
            search,
            min_price,
            max_price,
            page,
            page_size,
        )
        return [_list_row()], 11

    async def find_by_id(self, product_id):
        self.last_by_id = product_id
        return _by_id_row()


def _query_handler(service: FakeQueryService | None = None) -> ProductQueryHandler:
    return ProductQueryHandler(service or FakeQueryService(), _logger())


async def test_query_find_all_formats_timestamps_and_clamps_paging() -> None:
    response = await _query_handler().FindAll(
        product_query_pb2.FindAllProductRequest(page=0, page_size=0),
        FakeContext(),
    )
    assert response.message == "Successfully fetched products"
    assert response.pagination.current_page == 1
    assert response.pagination.page_size == 10
    assert response.pagination.total_records == 11
    assert response.data[0].id == 1
    assert response.data[0].created_at == "2026-01-02 03:04:05.000"
    assert response.data[0].updated_at == "2026-01-03 04:05:06.000"
    assert response.data[0].rating == 4.5


async def test_query_find_by_active_omits_deleted_at_wrapper_when_null() -> None:
    response = await _query_handler().FindByActive(
        product_query_pb2.FindAllProductRequest(page=1, page_size=10),
        FakeContext(),
    )
    assert response.message == "Successfully fetched active products"
    assert response.data[0].HasField("deleted_at") is False


async def test_query_find_by_trashed_includes_deleted_at() -> None:
    response = await _query_handler().FindByTrashed(
        product_query_pb2.FindAllProductRequest(page=1, page_size=10),
        FakeContext(),
    )
    assert response.data[0].HasField("deleted_at") is True
    assert response.data[0].deleted_at.value == "2026-02-01 05:06:07.000"


async def test_query_find_by_merchant_forwards_price_filters() -> None:
    service = FakeQueryService()
    response = await _query_handler(service).FindByMerchant(
        product_query_pb2.FindAllProductMerchantRequest(
            merchant_id=10,
            category_id=3,
            search="galaxy",
            min_price=100,
            max_price=2000,
            page=1,
            page_size=10,
        ),
        FakeContext(),
    )
    assert response.message == "Successfully fetched merchant products"
    assert service.last_by_merchant == (10, 3, "galaxy", 100, 2000, 1, 10)


async def test_query_find_by_category_forwards_price_filters() -> None:
    service = FakeQueryService()
    response = await _query_handler(service).FindByCategory(
        product_query_pb2.FindAllProductCategoryRequest(
            category_name="Electronics",
            search="galaxy",
            min_price=100,
            max_price=2000,
            page=1,
            page_size=10,
        ),
        FakeContext(),
    )
    assert response.message == "Successfully fetched category products"
    assert service.last_by_category == ("Electronics", "galaxy", 100, 2000, 1, 10)


async def test_query_find_by_id_success() -> None:
    response = await _query_handler().FindById(
        product_common_pb2.FindByIdProductRequest(id=1),
        FakeContext(),
    )
    assert response.message == "Successfully fetched product"
    assert response.data.id == 1
    assert response.data.name == "Galaxy S24"


async def test_query_find_by_id_zero_is_not_guarded() -> None:
    # the query handler has no `id == 0` guard.
    service = FakeQueryService()
    response = await _query_handler(service).FindById(
        product_common_pb2.FindByIdProductRequest(id=0),
        FakeContext(),
    )
    assert service.last_by_id == 0
    assert response.message == "Successfully fetched product"


# ---- command handler ----


class FakeCommandService:
    def __init__(self) -> None:
        self.last_create: Any = None
        self.last_update: Any = None
        self.last_count_stock: tuple[int, int] | None = None
        self.last_adjust: tuple[int, int, str] | None = None

    async def create(self, request):
        self.last_create = request
        return _by_id_row()

    async def update(self, request):
        self.last_update = request
        return _by_id_row()

    async def update_product_count_stock(self, product_id, stock):
        self.last_count_stock = (product_id, stock)
        return AdjustProductStockRow(product_id=product_id, count_in_stock=stock)

    async def adjust_product_stock(self, product_id, delta, operation_id):
        self.last_adjust = (product_id, delta, operation_id)
        return AdjustProductStockRow(product_id=product_id, count_in_stock=7)

    async def trash(self, product_id):
        return _by_id_row()

    async def restore(self, product_id):
        return _by_id_row()

    async def delete_permanent(self, product_id):
        return True

    async def restore_all(self):
        return True

    async def delete_all(self):
        return True


def _command_handler(
    service: FakeCommandService | None = None,
) -> ProductCommandHandler:
    return ProductCommandHandler(service or FakeCommandService(), _logger())


def _create_pb(**overrides: Any) -> Any:
    values = {
        "merchant_id": 10,
        "category_id": 3,
        "name": "Galaxy S24",
        "description": "desc",
        "price": 1200,
        "count_in_stock": 5,
        "brand": "Samsung",
        "weight": 200,
        "rating": 5,
        "slug_product": "galaxy-s24",
        "image_product": "uploads/products/galaxy-s24.jpg",
    }
    values.update(overrides)
    return product_command_pb2.CreateProductRequest(**values)


def _update_pb(**overrides: Any) -> Any:
    values = {
        "product_id": 4,
        "merchant_id": 10,
        "category_id": 3,
        "name": "Galaxy S24",
        "description": "desc",
        "price": 1200,
        "count_in_stock": 5,
        "brand": "Samsung",
        "weight": 200,
        "rating": 5,
        "slug_product": "galaxy-s24",
        "image_product": "uploads/products/galaxy-s24.jpg",
    }
    values.update(overrides)
    return product_command_pb2.UpdateProductRequest(**values)


async def test_command_create_success() -> None:
    response = await _command_handler().Create(_create_pb(), FakeContext())
    assert response.message == "Successfully created product"
    assert response.data.id == 1
    assert response.data.created_at == "2026-01-02 03:04:05.000"


async def test_command_create_validation_failure() -> None:
    context = FakeContext()
    with pytest.raises(FakeAbort) as excinfo:
        await _command_handler().Create(_create_pb(name=""), context)
    assert excinfo.value.code is grpc.StatusCode.INVALID_ARGUMENT
    assert excinfo.value.message == err_grpc_validate_create_product.message


async def test_command_update_rejects_zero_id() -> None:
    context = FakeContext()
    with pytest.raises(FakeAbort) as excinfo:
        await _command_handler().Update(_update_pb(product_id=0), context)
    assert excinfo.value.code is grpc.StatusCode.INVALID_ARGUMENT
    assert excinfo.value.message == "invalid ID"


async def test_command_update_success() -> None:
    service = FakeCommandService()
    response = await _command_handler(service).Update(_update_pb(), FakeContext())
    assert service.last_update.product_id == 4
    assert response.message == "Successfully updated product"


async def test_command_update_validation_failure() -> None:
    context = FakeContext()
    with pytest.raises(FakeAbort) as excinfo:
        await _command_handler().Update(_update_pb(price=0), context)
    assert excinfo.value.code is grpc.StatusCode.INVALID_ARGUMENT
    assert excinfo.value.message == err_grpc_validate_update_product.message


async def test_command_count_stock_row_emits_only_id_and_stock() -> None:
    service = FakeCommandService()
    response = await _command_handler(service).UpdateProductCountStock(
        product_command_pb2.UpdateProductCountStockRequest(product_id=4, stock=9),
        FakeContext(),
    )
    assert service.last_count_stock == (4, 9)
    assert response.message == "Successfully updated product count stock"
    assert response.data.id == 4
    assert response.data.count_in_stock == 9
    # The stock projection carries no other columns.
    assert response.data.merchant_id == 0
    assert response.data.name == ""
    assert response.data.created_at == ""


async def test_command_adjust_stock_row_emits_only_id_and_stock() -> None:
    service = FakeCommandService()
    response = await _command_handler(service).AdjustProductStock(
        product_command_pb2.AdjustProductStockRequest(
            product_id=4, delta=-2, operation_id="op-1"
        ),
        FakeContext(),
    )
    assert service.last_adjust == (4, -2, "op-1")
    assert response.message == "Successfully adjusted product stock"
    assert response.data.id == 4
    assert response.data.count_in_stock == 7
    assert response.data.category_id == 0


@pytest.mark.parametrize(
    "method_name",
    ["TrashedProduct", "RestoreProduct", "DeleteProductPermanent"],
)
async def test_command_single_row_guards_reject_zero(method_name: str) -> None:
    context = FakeContext()
    handler = _command_handler()
    with pytest.raises(FakeAbort) as excinfo:
        await getattr(handler, method_name)(
            product_common_pb2.FindByIdProductRequest(id=0), context
        )
    assert excinfo.value.code is grpc.StatusCode.INVALID_ARGUMENT
    assert excinfo.value.message == "invalid ID"


async def test_command_trash_restore_return_delete_at_shape() -> None:
    trashed = await _command_handler().TrashedProduct(
        product_common_pb2.FindByIdProductRequest(id=1), FakeContext()
    )
    restored = await _command_handler().RestoreProduct(
        product_common_pb2.FindByIdProductRequest(id=1), FakeContext()
    )
    assert trashed.message == "Successfully trashed product"
    assert restored.message == "Successfully restored product"
    # Single-row trash/restore rows omit `deleted_at`.
    assert trashed.data.HasField("deleted_at") is False
    assert restored.data.HasField("deleted_at") is False


async def test_command_permanent_and_bulk_envelopes() -> None:
    handler = _command_handler()
    deleted = await handler.DeleteProductPermanent(
        product_common_pb2.FindByIdProductRequest(id=1), FakeContext()
    )
    restored_all = await handler.RestoreAllProduct(empty_pb2.Empty(), FakeContext())
    deleted_all = await handler.DeleteAllProductPermanent(
        empty_pb2.Empty(), FakeContext()
    )
    assert isinstance(deleted, product_common_pb2.ApiResponseProductDelete)
    assert isinstance(restored_all, product_common_pb2.ApiResponseProductAll)
    assert isinstance(deleted_all, product_common_pb2.ApiResponseProductAll)
    assert deleted.message == "Successfully deleted product permanently"
    assert restored_all.message == "Successfully restored all products"
    assert deleted_all.message == "Successfully deleted all products permanently"


__all__ = []

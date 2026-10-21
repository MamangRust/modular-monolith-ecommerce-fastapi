"""Unit tests for category gRPC handlers (in-process, no server/DB)."""

from __future__ import annotations

from datetime import datetime
from typing import Any

import grpc
import pytest

from pb.category import (
    category_command_pb2,
    category_common_pb2,
    category_query_pb2,
)
from pkg.database.schema.category import (
    Category,
    CreateCategoryRow,
    GetCategoriesActiveRow,
    GetCategoriesRow,
    GetCategoryByIDRow,
    GetMonthlyCategoryRow,
    GetMonthlyTotalPriceRow,
    GetYearlyCategoryRow,
    GetYearlyTotalPriceRow,
)
from pkg.logger.logger import Logger
from service.category.handler.command import CategoryCommandHandler
from service.category.handler.query import CategoryQueryHandler
from service.category.handler.stats import CategoryStatsHandler
from service.category.handler.stats_by_id import CategoryStatsByIdHandler
from service.category.handler.stats_by_merchant import CategoryStatsByMerchantHandler

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


def _row() -> GetCategoriesRow:
    return GetCategoriesRow(
        category_id=1,
        name="Elektronik",
        description="desc",
        slug_category="elektronik",
        image_category="elektronik.png",
        created_at=CREATED,
        updated_at=UPDATED,
        total_count=11,
    )


def _active_row(deleted_at: datetime | None = None) -> GetCategoriesActiveRow:
    return GetCategoriesActiveRow(
        category_id=1,
        name="Elektronik",
        description="desc",
        slug_category="elektronik",
        image_category="elektronik.png",
        created_at=CREATED,
        updated_at=UPDATED,
        deleted_at=deleted_at,
        total_count=1,
    )


class FakeQueryService:
    async def find_all(self, search, page, page_size):
        return [_row()], 11

    async def find_by_id(self, category_id):
        return GetCategoryByIDRow(
            category_id=category_id,
            name="Elektronik",
            description="desc",
            slug_category="elektronik",
            image_category="elektronik.png",
            created_at=CREATED,
            updated_at=UPDATED,
        )

    async def find_active(self, search, page, page_size):
        return [_active_row()], 1

    async def find_trashed(self, search, page, page_size):
        return [_active_row(deleted_at=DELETED)], 1


class FakeCommandService:
    async def create(self, request):
        return CreateCategoryRow(
            category_id=1,
            name=request.name,
            description=request.description,
            slug_category=request.slug_category,
            image_category=request.image_category,
            created_at=CREATED,
            updated_at=UPDATED,
        )

    async def update(self, request):
        return GetCategoryByIDRow(
            category_id=request.category_id or 0,
            name=request.name,
            description=request.description,
            slug_category=request.slug_category,
            image_category=request.image_category,
            created_at=CREATED,
            updated_at=UPDATED,
        )

    async def trash(self, category_id):
        return Category(
            category_id=category_id,
            name="Elektronik",
            description="desc",
            slug_category="elektronik",
            image_category="elektronik.png",
            created_at=CREATED,
            updated_at=UPDATED,
            deleted_at=DELETED,
        )

    async def restore(self, category_id):
        return Category(
            category_id=category_id,
            name="Elektronik",
            description="desc",
            slug_category="elektronik",
            image_category="elektronik.png",
            created_at=CREATED,
            updated_at=UPDATED,
            deleted_at=None,
        )

    async def delete_permanent(self, category_id):
        return True

    async def restore_all(self):
        return True

    async def delete_all(self):
        return True


class FakeStatsService:
    async def find_monthly_total_price(self, year, month):
        return [GetMonthlyTotalPriceRow(year="2026", month="01", total_revenue=1000)]

    async def find_yearly_total_price(self, year):
        return [GetYearlyTotalPriceRow(year="2026", total_revenue=5000)]

    async def find_month_price(self, year):
        return [
            GetMonthlyCategoryRow(
                month="01",
                category_id=1,
                category_name="Elektronik",
                order_count=2,
                items_sold=3,
                total_revenue=1000,
            )
        ]

    async def find_year_price(self, year):
        return [
            GetYearlyCategoryRow(
                year="2026",
                category_id=1,
                category_name="Elektronik",
                order_count=2,
                items_sold=3,
                total_revenue=1000,
                unique_products_sold=1,
            )
        ]


class FakeStatsByIdService(FakeStatsService):
    async def find_monthly_total_price_by_id(self, year, month, category_id):
        return await FakeStatsService.find_monthly_total_price(self, year, month)

    async def find_yearly_total_price_by_id(self, year, category_id):
        return await FakeStatsService.find_yearly_total_price(self, year)

    async def find_month_price_by_id(self, year, category_id):
        return await FakeStatsService.find_month_price(self, year)

    async def find_year_price_by_id(self, year, category_id):
        return await FakeStatsService.find_year_price(self, year)


class FakeStatsByMerchantService(FakeStatsByIdService):
    async def find_monthly_total_price_by_merchant(self, year, month, merchant_id):
        return await FakeStatsService.find_monthly_total_price(self, year, month)

    async def find_yearly_total_price_by_merchant(self, year, merchant_id):
        return await FakeStatsService.find_yearly_total_price(self, year)

    async def find_month_price_by_merchant(self, year, merchant_id):
        return await FakeStatsService.find_month_price(self, year)

    async def find_year_price_by_merchant(self, year, merchant_id):
        return await FakeStatsService.find_year_price(self, year)


def _logger() -> Logger:
    return Logger("test", "error")


def _query_handler() -> CategoryQueryHandler:
    return CategoryQueryHandler(FakeQueryService(), _logger())


def _command_handler() -> CategoryCommandHandler:
    return CategoryCommandHandler(FakeCommandService(), _logger())


async def test_find_all_normalizes_and_computes_total_pages() -> None:
    request = category_query_pb2.FindAllCategoryRequest(page=0, page_size=0, search="")
    response = await _query_handler().FindAll(request, FakeContext())

    assert response.status == "success"
    assert response.message == "Successfully fetched categories"
    assert response.pagination.current_page == 1
    assert response.pagination.page_size == 10
    assert response.pagination.total_pages == 2
    assert response.pagination.total_records == 11
    assert response.data[0].created_at == "2026-01-02"


async def test_find_by_id_rejects_zero_id() -> None:
    context = FakeContext()
    with pytest.raises(FakeAbort) as excinfo:
        await _query_handler().FindById(
            category_common_pb2.FindByIdCategoryRequest(id=0), context
        )
    assert excinfo.value.code is grpc.StatusCode.INVALID_ARGUMENT
    assert excinfo.value.message == "Invalid category ID"
    assert context.metadata  # ErrorResponse detail attached


async def test_find_by_id_returns_category() -> None:
    response = await _query_handler().FindById(
        category_common_pb2.FindByIdCategoryRequest(id=1), FakeContext()
    )
    assert response.data.id == 1
    assert response.message == "Successfully fetched category"
    assert response.data.updated_at == "2026-01-03"


async def test_find_by_active_always_attaches_deleted_at_wrapper() -> None:
    response = await _query_handler().FindByActive(
        category_query_pb2.FindAllCategoryRequest(page=1, page_size=10), FakeContext()
    )
    assert response.data[0].HasField("deleted_at") is True
    assert response.data[0].deleted_at.value == ""


async def test_find_by_trashed_includes_deleted_at() -> None:
    response = await _query_handler().FindByTrashed(
        category_query_pb2.FindAllCategoryRequest(page=1, page_size=10), FakeContext()
    )
    assert response.data[0].deleted_at.value == "2026-02-03"


async def test_create_rejects_missing_required_field() -> None:
    context = FakeContext()
    with pytest.raises(FakeAbort) as excinfo:
        await _command_handler().Create(
            category_command_pb2.CreateCategoryRequest(
                name="Elektronik",
                description="",
                slug_category="elektronik",
                image_category="elektronik.png",
            ),
            context,
        )
    assert excinfo.value.code is grpc.StatusCode.INVALID_ARGUMENT
    assert (
        excinfo.value.message == "Validation failed: invalid create category request"
    )


async def test_create_returns_envelope() -> None:
    response = await _command_handler().Create(
        category_command_pb2.CreateCategoryRequest(
            name="Elektronik",
            description="desc",
            slug_category="elektronik",
            image_category="elektronik.png",
        ),
        FakeContext(),
    )
    assert response.status == "success"
    assert response.message == "Successfully created category"
    assert response.data.name == "Elektronik"


async def test_update_rejects_zero_id() -> None:
    with pytest.raises(FakeAbort):
        await _command_handler().Update(
            category_command_pb2.UpdateCategoryRequest(
                category_id=0,
                name="X",
                description="d",
                slug_category="x",
                image_category="x.png",
            ),
            FakeContext(),
        )


async def test_update_returns_envelope() -> None:
    response = await _command_handler().Update(
        category_command_pb2.UpdateCategoryRequest(
            category_id=3,
            name="Updated",
            description="d",
            slug_category="updated",
            image_category="u.png",
        ),
        FakeContext(),
    )
    assert response.message == "Successfully updated category"
    assert response.data.id == 3
    assert response.data.name == "Updated"


async def test_trash_and_restore_report_delete_at_envelope() -> None:
    handler = _command_handler()
    trashed = await handler.TrashedCategory(
        category_common_pb2.FindByIdCategoryRequest(id=3), FakeContext()
    )
    assert trashed.message == "Successfully trashed category"
    assert trashed.data.id == 3
    assert trashed.data.deleted_at.value == "2026-02-03"

    restored = await handler.RestoreCategory(
        category_common_pb2.FindByIdCategoryRequest(id=3), FakeContext()
    )
    assert restored.message == "Successfully restored category"
    assert restored.data.id == 3


async def test_delete_permanent_has_no_data() -> None:
    response = await _command_handler().DeleteCategoryPermanent(
        category_common_pb2.FindByIdCategoryRequest(id=3), FakeContext()
    )
    assert response.message == "Successfully deleted category permanently"


async def test_bulk_commands_report_go_messages() -> None:
    handler = _command_handler()
    restore = await handler.RestoreAllCategory(None, FakeContext())
    delete = await handler.DeleteAllCategoryPermanent(None, FakeContext())
    assert restore.message == "Successfully restored all categories"
    assert delete.message == "Successfully deleted all categories permanently"


async def test_stats_handlers_report_go_messages_and_values() -> None:
    stats = CategoryStatsHandler(FakeStatsService(), _logger())

    monthly = await stats.FindMonthlyTotalPrices(
        category_common_pb2.FindYearMonthTotalPrices(year=2026, month=1), FakeContext()
    )
    assert monthly.message == "Monthly sales retrieved successfully"
    assert monthly.data[0].year == "2026"
    assert monthly.data[0].month == "01"
    assert monthly.data[0].total_revenue == 1000

    yearly = await stats.FindYearlyTotalPrices(
        category_common_pb2.FindYearTotalPrices(year=2026), FakeContext()
    )
    assert yearly.message == "Yearly payment methods retrieved successfully"

    month_price = await stats.FindMonthPrice(
        category_common_pb2.FindYearCategory(year=2026), FakeContext()
    )
    assert month_price.message == "Monthly payment methods retrieved successfully"
    assert month_price.data[0].category_name == "Elektronik"
    assert month_price.data[0].order_count == 2

    year_price = await stats.FindYearPrice(
        category_common_pb2.FindYearCategory(year=2026), FakeContext()
    )
    assert year_price.message == "Yearly payment methods retrieved successfully"
    assert year_price.data[0].unique_products_sold == 1


async def test_stats_handlers_validate_year_and_month() -> None:
    stats = CategoryStatsHandler(FakeStatsService(), _logger())
    with pytest.raises(FakeAbort) as year_err:
        await stats.FindMonthlyTotalPrices(
            category_common_pb2.FindYearMonthTotalPrices(year=0, month=1), FakeContext()
        )
    assert year_err.value.message == "Invalid year"

    with pytest.raises(FakeAbort) as month_err:
        await stats.FindMonthlyTotalPrices(
            category_common_pb2.FindYearMonthTotalPrices(year=2026, month=13),
            FakeContext(),
        )
    assert month_err.value.message == "Invalid month"


async def test_stats_by_id_and_by_merchant_messages() -> None:
    by_id = CategoryStatsByIdHandler(FakeStatsByIdService(), _logger())
    month_by_id = await by_id.FindMonthPriceById(
        category_common_pb2.FindYearCategoryById(year=2026, category_id=1),
        FakeContext(),
    )
    assert month_by_id.message == "Category monthly payment methods retrieved successfully"

    year_by_id = await by_id.FindYearPriceById(
        category_common_pb2.FindYearCategoryById(year=2026, category_id=1),
        FakeContext(),
    )
    assert year_by_id.message == "Category yearly payment methods retrieved successfully"

    by_merchant = CategoryStatsByMerchantHandler(
        FakeStatsByMerchantService(), _logger()
    )
    month_by_merchant = await by_merchant.FindMonthPriceByMerchant(
        category_common_pb2.FindYearCategoryByMerchant(
            year=2026, merchant_id=1
        ),
        FakeContext(),
    )
    assert (
        month_by_merchant.message
        == "Merchant monthly payment methods retrieved successfully"
    )

    year_by_merchant = await by_merchant.FindYearPriceByMerchant(
        category_common_pb2.FindYearCategoryByMerchant(
            year=2026, merchant_id=1
        ),
        FakeContext(),
    )
    assert (
        year_by_merchant.message
        == "Merchant yearly payment methods retrieved successfully"
    )


async def test_stats_by_id_rejects_invalid_id() -> None:
    by_id = CategoryStatsByIdHandler(FakeStatsByIdService(), _logger())
    with pytest.raises(FakeAbort) as err:
        await by_id.FindMonthPriceById(
            category_common_pb2.FindYearCategoryById(year=2026, category_id=0),
            FakeContext(),
        )
    assert err.value.message == "Invalid category ID"

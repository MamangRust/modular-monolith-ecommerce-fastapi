"""Category gRPC integration tests: real grpc.aio server, generated clients.

Marked `integration`. Verifies the wire contract (the `%Y-%m-%d` date layout,
the always-present `deleted_at` wrapper, the stats envelopes) and that the
`ErrorResponse` detail survives the hop so a 404 stays a 404.

The stats RPCs are skipped until `orders`/`order_items`/`products` exist.
"""

from __future__ import annotations

import uuid

import grpc
import pytest

from pb.category import (
    category_command_pb2,
    category_command_pb2_grpc,
    category_common_pb2,
    category_query_pb2,
    category_query_pb2_grpc,
)
from pb.category.stats import (
    category_stats_byid_pb2_grpc,
    category_stats_bymerchant_pb2_grpc,
    category_stats_pb2_grpc,
)
from pkg.database.database import Database
from shared.errors import parse_grpc_error

pytestmark = pytest.mark.integration


def _create_request(name: str, slug: str) -> category_command_pb2.CreateCategoryRequest:
    return category_command_pb2.CreateCategoryRequest(
        name=name,
        description="integration test category",
        slug_category=slug,
        image_category="test.png",
    )


async def test_category_grpc_lifecycle_and_error_mapping(
    db: Database, category_grpc_server: str
) -> None:
    channel = grpc.aio.insecure_channel(category_grpc_server)
    query = category_query_pb2_grpc.CategoryQueryServiceStub(channel)
    command = category_command_pb2_grpc.CategoryCommandServiceStub(channel)
    name = f"TEST_GRPC_{uuid.uuid4().hex[:10]}"
    slug = f"test-grpc-{uuid.uuid4().hex[:12]}"

    try:
        created = await command.Create(_create_request(name, slug), timeout=5)
        assert created.status == "success"
        assert created.message == "Successfully created category"
        assert created.data.name == name
        assert created.data.created_at  # `%Y-%m-%d`, non-empty
        category_id = created.data.id

        found = await query.FindById(
            category_common_pb2.FindByIdCategoryRequest(id=category_id), timeout=5
        )
        assert found.data.id == category_id

        listed = await query.FindAll(
            category_query_pb2.FindAllCategoryRequest(page=1, page_size=10, search=name),
            timeout=5,
        )
        assert listed.pagination.total_records >= 1

        trashed = await command.TrashedCategory(
            category_common_pb2.FindByIdCategoryRequest(id=category_id), timeout=5
        )
        assert trashed.message == "Successfully trashed category"
        assert trashed.data.deleted_at.value  # non-empty after trash

        # Category FindAll filters `deleted_at IS NULL`, so the trashed row is
        # no longer listed (unlike banner).
        listed_after_trash = await query.FindAll(
            category_query_pb2.FindAllCategoryRequest(page=1, page_size=10, search=name),
            timeout=5,
        )
        assert all(row.id != category_id for row in listed_after_trash.data)

        restored = await command.RestoreCategory(
            category_common_pb2.FindByIdCategoryRequest(id=category_id), timeout=5
        )
        assert restored.message == "Successfully restored category"

        with pytest.raises(grpc.aio.AioRpcError) as invalid:
            await query.FindById(
                category_common_pb2.FindByIdCategoryRequest(id=0), timeout=5
            )
        assert invalid.value.code() is grpc.StatusCode.INVALID_ARGUMENT
        parsed_invalid = parse_grpc_error(invalid.value)
        assert parsed_invalid.code == 400
        assert parsed_invalid.message == "Invalid category ID"

        with pytest.raises(grpc.aio.AioRpcError) as missing:
            await query.FindById(
                category_common_pb2.FindByIdCategoryRequest(id=2_000_000_000),
                timeout=5,
            )
        assert missing.value.code() is grpc.StatusCode.NOT_FOUND
        assert parse_grpc_error(missing.value).code == 404

        with pytest.raises(grpc.aio.AioRpcError) as invalid_body:
            await command.Create(
                category_command_pb2.CreateCategoryRequest(
                    name="bad",
                    description="",
                    slug_category="bad",
                    image_category="bad.png",
                ),
                timeout=5,
            )
        assert invalid_body.value.code() is grpc.StatusCode.INVALID_ARGUMENT
        assert (
            parse_grpc_error(invalid_body.value).message
            == "Validation failed: invalid create category request"
        )
    finally:
        await channel.close()
        await db.execute(
            "DELETE FROM categories WHERE name LIKE :pattern",
            {"pattern": "TEST_GRPC%"},
        )


async def test_delete_permanent_removes_trashed_row(
    db: Database, category_grpc_server: str
) -> None:
    channel = grpc.aio.insecure_channel(category_grpc_server)
    query = category_query_pb2_grpc.CategoryQueryServiceStub(channel)
    command = category_command_pb2_grpc.CategoryCommandServiceStub(channel)
    name = f"TEST_GRPC_{uuid.uuid4().hex[:10]}"
    slug = f"test-grpc-{uuid.uuid4().hex[:12]}"
    try:
        created = await command.Create(_create_request(name, slug), timeout=5)
        category_id = created.data.id
        await command.TrashedCategory(
            category_common_pb2.FindByIdCategoryRequest(id=category_id), timeout=5
        )
        deleted = await command.DeleteCategoryPermanent(
            category_common_pb2.FindByIdCategoryRequest(id=category_id), timeout=5
        )
        assert deleted.message == "Successfully deleted category permanently"

        trashed = await query.FindByTrashed(
            category_query_pb2.FindAllCategoryRequest(page=1, page_size=10, search=name),
            timeout=5,
        )
        assert all(row.id != category_id for row in trashed.data)
    finally:
        await channel.close()
        await db.execute(
            "DELETE FROM categories WHERE name LIKE :pattern",
            {"pattern": "TEST_GRPC%"},
        )


async def _tables_exist(db: Database, *tables: str) -> bool:
    for table in tables:
        row = await db.scalar("SELECT to_regclass(:name) AS reg", {"name": table})
        if row is None or row["reg"] is None:
            return False
    return True


async def test_stats_rpcs_respond(
    db: Database, category_grpc_server: str
) -> None:
    if not await _tables_exist(db, "orders", "order_items", "products"):
        pytest.skip("orders/order_items/products tables not migrated yet")

    channel = grpc.aio.insecure_channel(category_grpc_server)
    stats = category_stats_pb2_grpc.CategoryStatsServiceStub(channel)
    by_id = category_stats_byid_pb2_grpc.CategoryStatsByIdServiceStub(channel)
    by_merchant = (
        category_stats_bymerchant_pb2_grpc.CategoryStatsByMerchantServiceStub(channel)
    )
    try:
        monthly = await stats.FindMonthlyTotalPrices(
            category_common_pb2.FindYearMonthTotalPrices(year=2026, month=1), timeout=5
        )
        assert monthly.message == "Monthly sales retrieved successfully"

        yearly = await stats.FindYearlyTotalPrices(
            category_common_pb2.FindYearTotalPrices(year=2026), timeout=5
        )
        assert yearly.message == "Yearly payment methods retrieved successfully"

        month_by_id = await by_id.FindMonthPriceById(
            category_common_pb2.FindYearCategoryById(year=2026, category_id=1), timeout=5
        )
        assert (
            month_by_id.message
            == "Category monthly payment methods retrieved successfully"
        )

        year_by_merchant = await by_merchant.FindYearPriceByMerchant(
            category_common_pb2.FindYearCategoryByMerchant(year=2026, merchant_id=1),
            timeout=5,
        )
        assert (
            year_by_merchant.message
            == "Merchant yearly payment methods retrieved successfully"
        )
    finally:
        await channel.close()

"""order gRPC integration tests. Marked `integration`. Runs the four real order servicers behind an ephemeral port; the `order_grpc_server` fixture points the product/order_item/shipping adapters at their real servers (each spun up by its own fixture), so the create saga reserves stock, writes order items and creates the shipping address for real. The merchant/transaction channels are dead wiring (unused). Verifies: - the create saga computes `total = sum(quantity * product.price) + shipping_cost` and the millisecond timestamps; - the query RPCs (`FindAll`/`FindById`/`FindByActive`/`FindByTrashed`) and the conditional `deleted_at` wrapper (unset on active rows, set on trashed ones); - the update saga moves stock by the quantity delta; - trash/restore/permanent delete and the `id == 0` guard; - the eight stats RPCs (global + by-merchant) and their verbatim guard inconsistencies."""

from __future__ import annotations

from datetime import datetime

import grpc
import pytest

from pb.order import (
    order_command_pb2,
    order_command_pb2_grpc,
    order_common_pb2,
    order_query_pb2,
    order_query_pb2_grpc,
)
from pb.order.stats import (
    order_stats_pb2,
    order_stats_pb2_grpc,
    order_statsbymerchant_pb2,
    order_statsbymerchant_pb2_grpc,
)
from pb.shipping_address import shipping_address_command_pb2
from pkg.database.database import Database
from shared.errors import parse_grpc_error

pytestmark = pytest.mark.integration


def _shipping(**overrides):
    base = {
        "alamat": "Jalan Panjang No 1",
        "provinsi": "DKI Jakarta",
        "kota": "Jakarta",
        "courier": "jne",
        "shipping_method": "reg",
        "shipping_cost": 15000,
        "negara": "Indonesia",
    }
    base.update(overrides)
    return shipping_address_command_pb2.CreateShippingAddressRequest(**base)


def _create_request(parents, *, quantity: int = 2, shipping=None):
    return order_command_pb2.CreateOrderRequest(
        merchant_id=parents.merchant_id,
        user_id=parents.user_id,
        total_price=1,  # non-zero to pass validation; the saga recomputes it
        items=[
            order_command_pb2.CreateOrderItemRequest(
                product_id=parents.product_id, quantity=quantity, price=5000
            )
        ],
        shipping=shipping if shipping is not None else _shipping(),
    )


async def test_order_grpc_lifecycle(db: Database, order_parents, order_grpc_server) -> None:
    channel = grpc.aio.insecure_channel(order_grpc_server)
    query = order_query_pb2_grpc.OrderQueryServiceStub(channel)
    command = order_command_pb2_grpc.OrderCommandServiceStub(channel)
    try:
        created = await command.Create(_create_request(order_parents), timeout=10)
        assert created.message == "Successfully created order"
        assert created.data.user_id == order_parents.user_id
        assert created.data.merchant_id == order_parents.merchant_id
        # 2 * 5000 (product price) + 15000 shipping.
        assert created.data.total_price == 25000
        assert len(created.data.created_at) == 23  # .mmm layout
        order_id = created.data.id

        # The saga persisted the order item and the reservation ledger.
        item = await db.scalar(
            """
            SELECT order_item_id FROM order_items
            WHERE order_id = :order_id AND deleted_at IS NULL
            """,
            {"order_id": order_id},
        )
        assert item is not None
        order_item_id = int(item["order_item_id"])
        reservation = await db.scalar(
            """
            SELECT status, quantity FROM order_stock_reservations
            WHERE order_id = :order_id
            """,
            {"order_id": order_id},
        )
        assert reservation is not None
        assert reservation["status"] == "reserved"
        assert int(reservation["quantity"]) == 2

        listed = await query.FindAll(
            order_query_pb2.FindAllOrderRequest(page=1, page_size=10, search=str(order_id)),
            timeout=5,
        )
        assert listed.message == "Successfully fetched order"
        assert listed.pagination.total_records >= 1
        assert any(r.id == order_id for r in listed.data)

        by_id = await query.FindById(
            order_common_pb2.FindByIdOrderRequest(id=order_id), timeout=5
        )
        assert by_id.data.id == order_id
        assert by_id.data.total_price == 25000

        # Update: raise the quantity to 3; the saga reserves one more unit.
        updated = await command.Update(
            order_command_pb2.UpdateOrderRequest(
                order_id=order_id,
                user_id=order_parents.user_id,
                total_price=1,  # overwritten by the saga
                items=[
                    order_command_pb2.UpdateOrderItemRequest(
                        order_item_id=order_item_id,
                        product_id=order_parents.product_id,
                        quantity=3,
                        price=5000,
                    )
                ],
            ),
            timeout=10,
        )
        assert updated.message == "Successfully updated order"
        assert updated.data.total_price == 3 * 5000 + 15000

        reservation_after = await db.scalar(
            """
            SELECT quantity FROM order_stock_reservations
            WHERE order_id = :order_id
            """,
            {"order_id": order_id},
        )
        assert reservation_after is not None
        assert int(reservation_after["quantity"]) == 3

        # Active rows leave the deleted_at wrapper unset (guards on non-empty).
        active = await query.FindByActive(
            order_query_pb2.FindAllOrderRequest(page=1, page_size=100, search=""),
            timeout=5,
        )
        assert active.message == "Successfully fetched active order"
        active_row = next(r for r in active.data if r.id == order_id)
        assert not active_row.HasField("deleted_at")

        trashed = await command.TrashedOrder(
            order_common_pb2.FindByIdOrderRequest(id=order_id), timeout=10
        )
        assert trashed.message == "Successfully trashed order"
        assert trashed.data.deleted_at.value

        trashed_rows = await query.FindByTrashed(
            order_query_pb2.FindAllOrderRequest(page=1, page_size=100, search=""),
            timeout=5,
        )
        assert trashed_rows.message == "Successfully fetched trashed order"
        trashed_row = next(r for r in trashed_rows.data if r.id == order_id)
        assert trashed_row.HasField("deleted_at")

        restored = await command.RestoreOrder(
            order_common_pb2.FindByIdOrderRequest(id=order_id), timeout=10
        )
        assert restored.message == "Successfully restored order"

        await command.TrashedOrder(
            order_common_pb2.FindByIdOrderRequest(id=order_id), timeout=10
        )
        deleted = await command.DeleteOrderPermanent(
            order_common_pb2.FindByIdOrderRequest(id=order_id), timeout=10
        )
        assert deleted.message == "Successfully deleted order permanently"
    finally:
        await channel.close()


async def test_order_grpc_error_mapping(order_parents, order_grpc_server) -> None:
    channel = grpc.aio.insecure_channel(order_grpc_server)
    query = order_query_pb2_grpc.OrderQueryServiceStub(channel)
    command = order_command_pb2_grpc.OrderCommandServiceStub(channel)
    try:
        # Empty shipping -> nested validation failure.
        with pytest.raises(grpc.aio.AioRpcError) as bad_create:
            await command.Create(
                order_command_pb2.CreateOrderRequest(
                    merchant_id=order_parents.merchant_id,
                    user_id=order_parents.user_id,
                    total_price=1,
                    items=[
                        order_command_pb2.CreateOrderItemRequest(
                            product_id=order_parents.product_id, quantity=1, price=5000
                        )
                    ],
                ),
                timeout=10,
            )
        assert bad_create.value.code() is grpc.StatusCode.INVALID_ARGUMENT
        assert parse_grpc_error(bad_create.value).message == (
            "validation failed: invalid create order request"
        )

        # Update body with a zero user_id -> update validation failure.
        with pytest.raises(grpc.aio.AioRpcError) as bad_update:
            await command.Update(
                order_command_pb2.UpdateOrderRequest(
                    order_id=1,
                    user_id=0,
                    total_price=0,
                    items=[
                        order_command_pb2.UpdateOrderItemRequest(
                            order_item_id=0, product_id=1, quantity=1, price=1
                        )
                    ],
                ),
                timeout=10,
            )
        assert bad_update.value.code() is grpc.StatusCode.INVALID_ARGUMENT
        assert parse_grpc_error(bad_update.value).message == (
            "validation failed: invalid update order request"
        )

        # FindById / single-row mutations guard id == 0.
        with pytest.raises(grpc.aio.AioRpcError) as invalid_id:
            await query.FindById(
                order_common_pb2.FindByIdOrderRequest(id=0), timeout=5
            )
        assert invalid_id.value.code() is grpc.StatusCode.INVALID_ARGUMENT
        assert parse_grpc_error(invalid_id.value).message == "Invalid ID"

        with pytest.raises(grpc.aio.AioRpcError) as invalid_trash:
            await command.TrashedOrder(
                order_common_pb2.FindByIdOrderRequest(id=0), timeout=5
            )
        assert parse_grpc_error(invalid_trash.value).message == "Invalid ID"

        # A quantity above the fixture stock (1000) loses the guarded UPDATE.
        with pytest.raises(grpc.aio.AioRpcError) as no_stock:
            await command.Create(_create_request(order_parents, quantity=100_000), timeout=15)
        assert no_stock.value.code() is grpc.StatusCode.INVALID_ARGUMENT
        assert parse_grpc_error(no_stock.value).message == "Insufficient product stock"
    finally:
        await channel.close()


async def test_order_stats_grpc(
    db: Database, order_parents, order_grpc_server
) -> None:
    channel = grpc.aio.insecure_channel(order_grpc_server)
    stats = order_stats_pb2_grpc.OrderStatsServiceStub(channel)
    by_merchant = order_statsbymerchant_pb2_grpc.OrderStatsByMerchantServiceStub(channel)
    merchant_id = order_parents.merchant_id
    try:
        # Seed an order in March 2001 (deterministic window, far from the seeder).
        order = await db.execute(
            """
            INSERT INTO orders (user_id, merchant_id, total_price, created_at)
            VALUES (:user_id, :merchant_id, 7000, :created_at)
            RETURNING order_id
            """,
            {
                "user_id": order_parents.user_id,
                "merchant_id": merchant_id,
                "created_at": datetime(2001, 3, 10, 9, 0),
            },
        )
        assert order is not None
        order_id = int(order["order_id"])
        await db.execute(
            """
            INSERT INTO order_items (order_id, product_id, quantity, price)
            VALUES (:order_id, :product_id, 2, 3500)
            """,
            {"order_id": order_id, "product_id": order_parents.product_id},
        )

        monthly = await stats.FindMonthlyTotalRevenue(
            order_stats_pb2.FindYearMonthTotalRevenue(year=2001, month=3), timeout=5
        )
        assert monthly.message == "Monthly sales retrieved successfully"
        march = next(r for r in monthly.data if r.month == "March")
        assert march.total_revenue == 7000

        yearly = await stats.FindYearlyTotalRevenue(
            order_stats_pb2.FindYearTotalRevenue(year=2001), timeout=5
        )
        assert yearly.message == "Yearly payment methods retrieved successfully"
        current = next(r for r in yearly.data if r.year == "2001")
        assert current.total_revenue == 7000

        monthly_revenue = await stats.FindMonthlyRevenue(
            order_stats_pb2.FindYearOrder(year=2001), timeout=5
        )
        assert monthly_revenue.message == "Monthly revenue data retrieved"
        mar = next(r for r in monthly_revenue.data if r.month == "Mar")
        assert mar.order_count == 1
        assert mar.total_items_sold == 2

        yearly_revenue = await stats.FindYearlyRevenue(
            order_stats_pb2.FindYearOrder(year=2001), timeout=5
        )
        assert yearly_revenue.message == "Yearly revenue data retrieved"
        y2001 = next(r for r in yearly_revenue.data if r.year == "2001")
        assert y2001.order_count == 1
        assert y2001.unique_products_sold == 1

        # By-merchant siblings.
        bm_monthly = await by_merchant.FindMonthlyTotalRevenueByMerchant(
            order_statsbymerchant_pb2.FindYearMonthTotalRevenueByMerchant(
                year=2001, month=3, merchant_id=merchant_id
            ),
            timeout=5,
        )
        assert bm_monthly.message == "Monthly sales retrieved successfully"
        assert next(r for r in bm_monthly.data if r.month == "March").total_revenue == 7000

        bm_yearly = await by_merchant.FindYearlyTotalRevenueByMerchant(
            order_statsbymerchant_pb2.FindYearTotalRevenueByMerchant(
                year=2001, merchant_id=merchant_id
            ),
            timeout=5,
        )
        assert bm_yearly.message == "Yearly payment methods retrieved successfully"

        bm_monthly_revenue = await by_merchant.FindMonthlyRevenueByMerchant(
            order_statsbymerchant_pb2.FindYearOrderByMerchant(
                year=2001, merchant_id=merchant_id
            ),
            timeout=5,
        )
        assert bm_monthly_revenue.message == "Monthly revenue by merchant data retrieved"

        bm_yearly_revenue = await by_merchant.FindYearlyRevenueByMerchant(
            order_statsbymerchant_pb2.FindYearOrderByMerchant(
                year=2001, merchant_id=merchant_id
            ),
            timeout=5,
        )
        assert bm_yearly_revenue.message == "Yearly revenue by merchant data retrieved"
    finally:
        await channel.close()


async def test_order_stats_grpc_guards(order_grpc_server) -> None:
    channel = grpc.aio.insecure_channel(order_grpc_server)
    stats = order_stats_pb2_grpc.OrderStatsServiceStub(channel)
    by_merchant = order_statsbymerchant_pb2_grpc.OrderStatsByMerchantServiceStub(channel)
    try:
        with pytest.raises(grpc.aio.AioRpcError) as bad_year:
            await stats.FindMonthlyTotalRevenue(
                order_stats_pb2.FindYearMonthTotalRevenue(year=0, month=3), timeout=5
            )
        assert parse_grpc_error(bad_year.value).message == "Invalid year"

        with pytest.raises(grpc.aio.AioRpcError) as bad_month:
            await stats.FindMonthlyTotalRevenue(
                order_stats_pb2.FindYearMonthTotalRevenue(year=2001, month=13), timeout=5
            )
        assert parse_grpc_error(bad_month.value).message == "Invalid month"

        # with the generic invalid-id sentinel.
        with pytest.raises(grpc.aio.AioRpcError) as summary_year:
            await stats.FindMonthlyRevenue(
                order_stats_pb2.FindYearOrder(year=0), timeout=5
            )
        assert parse_grpc_error(summary_year.value).message == "Invalid ID"

        with pytest.raises(grpc.aio.AioRpcError) as merchant_monthly:
            await by_merchant.FindMonthlyRevenueByMerchant(
                order_statsbymerchant_pb2.FindYearOrderByMerchant(
                    year=2001, merchant_id=0
                ),
                timeout=5,
            )
        assert parse_grpc_error(merchant_monthly.value).message == "Invalid merchant ID"

        # generic invalid-id sentinel for a bad merchant.
        with pytest.raises(grpc.aio.AioRpcError) as merchant_yearly:
            await by_merchant.FindYearlyRevenueByMerchant(
                order_statsbymerchant_pb2.FindYearOrderByMerchant(
                    year=2001, merchant_id=0
                ),
                timeout=5,
            )
        assert parse_grpc_error(merchant_yearly.value).message == "Invalid ID"
    finally:
        await channel.close()


__all__ = []

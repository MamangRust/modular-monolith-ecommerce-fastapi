"""order repository integration tests against a real PostgreSQL. The stats repositories join `orders` + `order_items`, so the stats tests insert orders with an explicit `created_at` in **2001** — far from the seeder's current-year rows — to keep the revenue windows deterministic. Covers the read repository (`find_all`/`find_active`/`find_trashed`/ `find_by_merchant`/`find_by_id`), the write repository (create/update/trash/ restore/permanent delete incl. the child-purge CTE and the bulk operations), the four stats queries (global + by-merchant), and the stock reservation ledger (upsert/release/reserve/update_quantity and the conditional `NoRowsError` transitions)."""

from __future__ import annotations

from datetime import datetime

import grpc
import pytest

from pkg.database.database import Database
from pkg.database.errors import NoRowsError
from service.order.repository import GuardOptions, new_repositories
from service.order.repository.stock_reservation_repository import (
    StockReservationRepositoryImpl,
)
from shared.domain.requests.order import (
    CreateOrderRecordRequest,
    FindAllOrder,
    FindAllOrderByMerchant,
    MonthOrderMerchant,
    MonthTotalRevenue,
    MonthTotalRevenueMerchant,
    UpdateOrderRecordRequest,
    YearOrderMerchant,
    YearTotalRevenueMerchant,
)
from shared.errors import AppError

pytestmark = pytest.mark.integration


@pytest.fixture
async def repos(db):
    """order repositories with unused dependency channels."""
    channels = [grpc.aio.insecure_channel("127.0.0.1:1") for _ in range(6)]
    try:
        yield new_repositories(
            db,
            user_channel=channels[0],
            merchant_channel=channels[1],
            product_channel=channels[2],
            order_item_channel=channels[3],
            shipping_channel=channels[4],
            transaction_channel=channels[5],
            guards=GuardOptions(),
        )
    finally:
        for channel in channels:
            await channel.close()


async def _seed_order(
    db: Database,
    parents,
    *,
    total_price: int = 0,
    created_at: datetime | None = None,
) -> int:
    if created_at is None:
        row = await db.execute(
            """
            INSERT INTO orders (user_id, merchant_id, total_price)
            VALUES (:user_id, :merchant_id, :total_price)
            RETURNING order_id
            """,
            {
                "user_id": parents.user_id,
                "merchant_id": parents.merchant_id,
                "total_price": total_price,
            },
        )
    else:
        row = await db.execute(
            """
            INSERT INTO orders (user_id, merchant_id, total_price, created_at)
            VALUES (:user_id, :merchant_id, :total_price, :created_at)
            RETURNING order_id
            """,
            {
                "user_id": parents.user_id,
                "merchant_id": parents.merchant_id,
                "total_price": total_price,
                "created_at": created_at,
            },
        )
    assert row is not None
    return int(row["order_id"])


async def _seed_item(
    db: Database,
    order_id: int,
    product_id: int,
    *,
    quantity: int = 2,
    price: int = 5000,
) -> int:
    row = await db.execute(
        """
        INSERT INTO order_items (order_id, product_id, quantity, price)
        VALUES (:order_id, :product_id, :quantity, :price)
        RETURNING order_item_id
        """,
        {
            "order_id": order_id,
            "product_id": product_id,
            "quantity": quantity,
            "price": price,
        },
    )
    assert row is not None
    return int(row["order_item_id"])


# --------------------------------------------------------------- read + write


async def test_create_and_query_repository(db, order_parents, repos) -> None:
    created = await repos.order_command.create(
        CreateOrderRecordRequest(
            merchant_id=order_parents.merchant_id,
            user_id=order_parents.user_id,
            total_price=0,
        )
    )
    assert created.order_id > 0
    assert created.user_id == order_parents.user_id
    assert created.merchant_id == order_parents.merchant_id
    assert created.total_price == 0

    rows = await repos.order_query.find_all(
        FindAllOrder(search=str(created.order_id), page=1, page_size=10)
    )
    assert any(row.order_id == created.order_id for row in rows)
    assert rows[0].total_count >= 1

    by_id = await repos.order_query.find_by_id(created.order_id)
    assert by_id.order_id == created.order_id

    by_merchant = await repos.order_query.find_by_merchant(
        FindAllOrderByMerchant(
            merchant_id=order_parents.merchant_id, search="", page=1, page_size=100
        )
    )
    assert any(row.order_id == created.order_id for row in by_merchant)


async def test_update_trash_restore_and_active_trashed(db, order_parents, repos) -> None:
    order_id = await _seed_order(db, order_parents)
    updated = await repos.order_command.update(
        UpdateOrderRecordRequest(
            order_id=order_id,
            merchant_id=order_parents.merchant_id,
            user_id=order_parents.user_id,
            total_price=12345,
        )
    )
    assert updated.total_price == 12345

    trashed = await repos.order_command.trash(order_id)
    assert trashed.deleted_at is not None

    active = await repos.order_query.find_active(
        FindAllOrder(search="", page=1, page_size=100)
    )
    assert all(row.order_id != order_id for row in active)

    trashed_rows = await repos.order_query.find_trashed(
        FindAllOrder(search="", page=1, page_size=100)
    )
    assert any(row.order_id == order_id for row in trashed_rows)

    # `find_trashed_by_id` reads the trashed row directly.
    fetched = await repos.order_command.find_trashed_by_id(order_id)
    assert fetched.order_id == order_id

    restored = await repos.order_command.restore(order_id)
    assert restored.deleted_at is None


async def test_delete_permanent_requires_trashed(db, order_parents, repos) -> None:
    order_id = await _seed_order(db, order_parents)
    # `:exec` in -> always reports success even when nothing matched.
    assert await repos.order_command.delete_permanent(order_id) is True
    still_active = await repos.order_query.find_by_id(order_id)
    assert still_active.order_id == order_id

    await repos.order_command.trash(order_id)
    assert await repos.order_command.delete_permanent(order_id) is True
    with pytest.raises(AppError) as missing:
        await repos.order_query.find_by_id(order_id)
    assert missing.value.code == 404


async def test_delete_permanent_with_children_purges_children(
    db, order_parents, repos
) -> None:
    order_id = await _seed_order(db, order_parents)
    product_id = order_parents.product_id
    await _seed_item(db, order_id, product_id)
    await repos.stock_reservation.upsert(order_id, product_id, 2)
    await db.execute(
        """
        INSERT INTO shipping_addresses (order_id, alamat, provinsi, kota, courier,
            shipping_method, shipping_cost, negara)
        VALUES (:order_id, 'alamat', 'prov', 'kota', 'jne', 'reg', 1000, 'ID')
        """,
        {"order_id": order_id},
    )
    await db.execute(
        """
        INSERT INTO transactions (order_id, merchant_id, payment_method, amount)
        VALUES (:order_id, :merchant_id, 'transfer', 1000)
        """,
        {"order_id": order_id, "merchant_id": order_parents.merchant_id},
    )

    await repos.order_command.trash(order_id)
    assert await repos.order_command.delete_permanent_with_children(order_id) is True

    assert await repos.stock_reservation.get_by_order(order_id) == []
    assert await db.select(
        "SELECT 1 FROM order_items WHERE order_id = :order_id", {"order_id": order_id}
    ) == []
    assert await db.select(
        "SELECT 1 FROM shipping_addresses WHERE order_id = :order_id",
        {"order_id": order_id},
    ) == []
    assert await db.select(
        "SELECT 1 FROM transactions WHERE order_id = :order_id", {"order_id": order_id}
    ) == []


async def test_delete_permanent_with_children_requires_trashed(
    db, order_parents, repos
) -> None:
    order_id = await _seed_order(db, order_parents)
    with pytest.raises(AppError) as excinfo:
        await repos.order_command.delete_permanent_with_children(order_id)
    assert excinfo.value.code == 404
    assert excinfo.value.message == "order not found"


async def test_bulk_restore_and_delete_all(db, order_parents, repos) -> None:
    first = await _seed_order(db, order_parents)
    second = await _seed_order(db, order_parents)
    await repos.order_command.trash(first)
    await repos.order_command.trash(second)

    trashed = await repos.order_command.find_trashed()
    assert {first, second}.issubset({int(row.order_id) for row in trashed})

    assert await repos.order_command.restore_all() is True
    active = await repos.order_query.find_active(
        FindAllOrder(search=str(first), page=1, page_size=10)
    )
    assert any(row.order_id == first for row in active)

    await repos.order_command.trash(first)
    assert await repos.order_command.delete_all() is True
    with pytest.raises(AppError):
        await repos.order_query.find_by_id(first)


async def test_missing_order_maps_to_not_found(db, repos) -> None:
    with pytest.raises(AppError) as excinfo:
        await repos.order_query.find_by_id(2_000_000_000)
    assert excinfo.value.code == 404
    assert excinfo.value.message == "order not found"


# -------------------------------------------------------------------- stats


async def test_global_stats_revenue_and_orders(db, order_parents, repos) -> None:
    order_id = await _seed_order(
        db, order_parents, total_price=10000, created_at=datetime(2001, 6, 15, 10, 0)
    )
    await _seed_item(db, order_id, order_parents.product_id, quantity=3, price=10000)

    monthly = await repos.order_stats.get_monthly_total_revenue(
        MonthTotalRevenue(year=2001, month=6)
    )
    june = next(row for row in monthly if row.month == "June")
    assert int(june.total_revenue) == 10000

    yearly = await repos.order_stats.get_yearly_total_revenue(2001)
    current = next(row for row in yearly if row.year == "2001")
    assert int(current.total_revenue) == 10000

    monthly_order = await repos.order_stats.get_monthly_order(2001)
    june_order = next(row for row in monthly_order if row.month == "Jun")
    assert int(june_order.order_count) == 1
    assert int(june_order.total_revenue) == 10000
    assert int(june_order.total_items_sold) == 3

    yearly_order = await repos.order_stats.get_yearly_order(2001)
    y2001 = next(row for row in yearly_order if row.year == "2001")
    assert int(y2001.order_count) == 1
    assert int(y2001.unique_products_sold) == 1


async def test_by_merchant_stats_revenue_and_orders(db, order_parents, repos) -> None:
    order_id = await _seed_order(
        db, order_parents, total_price=20000, created_at=datetime(2001, 6, 15, 10, 0)
    )
    await _seed_item(db, order_id, order_parents.product_id, quantity=4, price=5000)
    merchant_id = order_parents.merchant_id

    monthly = await repos.order_stats_by_merchant.get_monthly_total_revenue_by_merchant(
        MonthTotalRevenueMerchant(merchant_id=merchant_id, year=2001, month=6)
    )
    june = next(row for row in monthly if row.month == "June")
    assert int(june.total_revenue) == 20000

    yearly = (
        await repos.order_stats_by_merchant.get_yearly_total_revenue_by_merchant(
            YearTotalRevenueMerchant(merchant_id=merchant_id, year=2001)
        )
    )
    current = next(row for row in yearly if row.year == "2001")
    assert int(current.total_revenue) == 20000

    monthly_order = (
        await repos.order_stats_by_merchant.get_monthly_order_by_merchant(
            MonthOrderMerchant(merchant_id=merchant_id, year=2001)
        )
    )
    june_order = next(row for row in monthly_order if row.month == "Jun")
    assert int(june_order.order_count) == 1
    assert int(june_order.total_items_sold) == 4

    yearly_order = (
        await repos.order_stats_by_merchant.get_yearly_order_by_merchant(
            YearOrderMerchant(merchant_id=merchant_id, year=2001)
        )
    )
    y2001 = next(row for row in yearly_order if row.year == "2001")
    assert int(y2001.total_revenue) == 20000


async def test_by_merchant_stats_isolate_other_merchants(
    db, order_parents, repos
) -> None:
    order_id = await _seed_order(
        db, order_parents, total_price=5000, created_at=datetime(2001, 6, 15, 10, 0)
    )
    await _seed_item(db, order_id, order_parents.product_id, quantity=1, price=5000)

    other = await repos.order_stats_by_merchant.get_monthly_total_revenue_by_merchant(
        MonthTotalRevenueMerchant(merchant_id=999_999_999, year=2001, month=6)
    )
    assert all(int(row.total_revenue) == 0 for row in other)


# ------------------------------------------------------- stock reservations


async def test_stock_reservation_ledger_lifecycle(db, order_parents) -> None:
    stock = StockReservationRepositoryImpl(db)
    order_id = await _seed_order(db, order_parents)
    product_id = order_parents.product_id

    reservation = await stock.upsert(order_id, product_id, 2)
    assert reservation.status == "reserved"
    assert reservation.quantity == 2

    # A second upsert adds to the quantity (ON CONFLICT DO UPDATE).
    reservation = await stock.upsert(order_id, product_id, 3)
    assert reservation.quantity == 5

    updated = await stock.update_quantity(order_id, product_id, 7)
    assert updated.quantity == 7

    released = await stock.release(order_id, product_id)
    assert released.status == "released"
    # Releasing again finds no `reserved` row -> pgx.ErrNoRows equivalent.
    with pytest.raises(NoRowsError):
        await stock.release(order_id, product_id)

    re_reserved = await stock.reserve(order_id, product_id)
    assert re_reserved.status == "reserved"
    with pytest.raises(NoRowsError):
        await stock.reserve(order_id, product_id)

    assert len(await stock.get_by_order(order_id)) == 1
    await stock.delete_by_order_product(order_id, product_id)
    assert await stock.get_by_order(order_id) == []


async def test_reconcile_queries_split_by_order_state(db, order_parents) -> None:
    stock = StockReservationRepositoryImpl(db)
    active = await _seed_order(db, order_parents)
    trashed = await _seed_order(db, order_parents)
    product_id = order_parents.product_id

    await stock.upsert(active, product_id, 2)
    await stock.release(active, product_id)  # released on an ACTIVE order
    await stock.upsert(trashed, product_id, 3)  # reserved on a TRASHED order
    await db.execute(
        "UPDATE orders SET deleted_at = CURRENT_TIMESTAMP WHERE order_id = :order_id",
        {"order_id": trashed},
    )

    released_active = await stock.get_released_for_active_orders()
    assert any(int(row.order_id) == active for row in released_active)
    reserved_trashed = await stock.get_reserved_for_trashed_orders()
    assert any(int(row.order_id) == trashed for row in reserved_trashed)


async def test_cleanup_removes_old_released_reservations(db, order_parents) -> None:
    stock = StockReservationRepositoryImpl(db)
    order_id = await _seed_order(db, order_parents)
    product_id = order_parents.product_id
    await stock.upsert(order_id, product_id, 2)
    await stock.release(order_id, product_id)
    await db.execute(
        "UPDATE orders SET deleted_at = CURRENT_TIMESTAMP WHERE order_id = :order_id",
        {"order_id": order_id},
    )
    # Age the released row past the retention cutoff.
    await db.execute(
        """
        UPDATE order_stock_reservations SET updated_at = :old
        WHERE order_id = :order_id
        """,
        {"old": datetime(2000, 1, 1), "order_id": order_id},
    )

    removed = await stock.delete_old_released_reservations(datetime(2020, 1, 1))
    assert removed >= 1
    assert await stock.get_by_order(order_id) == []


__all__ = []

"""Order item repository integration tests against a real PostgreSQL.

Marked `integration` (excluded from `make test`). `order_items` has foreign keys
to `orders` (which references `users` and `merchants`) and to `products`, so each
test uses the `order_parents` fixture (a real user + merchant + category +
product) and seeds its own order. The fixture also removes every row it owns.
The product id doubles as the search key (the SQL matches `order_id::TEXT` /
`product_id::TEXT`).
"""

from __future__ import annotations

import pytest

from pkg.database.database import Database
from service.order_item.repository import new_repositories
from shared.domain.requests.order_item import (
    CreateOrderItemRecordRequest,
    UpdateOrderItemRecordRequest,
)
from shared.errors import AppError

pytestmark = pytest.mark.integration


async def _seed_order(db: Database, parents) -> int:
    order = await db.execute(
        """
        INSERT INTO orders (user_id, merchant_id, total_price)
        VALUES (:user_id, :merchant_id, 0)
        RETURNING order_id
        """,
        {"user_id": parents.user_id, "merchant_id": parents.merchant_id},
    )
    assert order is not None
    return int(order["order_id"])


def _create(order_id: int, product_id: int, quantity: int = 2, price: int = 5000):
    return CreateOrderItemRecordRequest(
        order_id=order_id,
        product_id=product_id,
        quantity=quantity,
        price=price,
    )


async def test_create_and_find_by_order(db: Database, order_parents) -> None:
    repos = new_repositories(db)
    order_id = await _seed_order(db, order_parents)
    product_id = order_parents.product_id
    created = await repos.command.create(_create(order_id, product_id))
    assert created.order_item_id > 0
    assert created.order_id == order_id
    assert created.product_id == product_id
    assert created.quantity == 2
    assert created.price == 5000

    found = await repos.query.find_order_item_by_order(order_id)
    assert any(row.order_item_id == created.order_item_id for row in found)

    listed = await repos.query.find_all(str(product_id), 1, 10)
    assert any(row.order_item_id == created.order_item_id for row in listed)


async def test_calculate_total_price_sums_active_items(
    db: Database, order_parents
) -> None:
    repos = new_repositories(db)
    order_id = await _seed_order(db, order_parents)
    product_id = order_parents.product_id
    await repos.command.create(_create(order_id, product_id, quantity=2, price=5000))
    await repos.command.create(_create(order_id, product_id, quantity=3, price=1000))
    # An item trashed before the sum must not count.
    trashed = await repos.command.create(
        _create(order_id, product_id, quantity=9, price=999)
    )
    await repos.command.trash(trashed.order_item_id)

    total = await repos.command.calculate_total_price(order_id)
    assert total == 2 * 5000 + 3 * 1000


async def test_missing_order_item_maps_to_not_found(db: Database) -> None:
    repos = new_repositories(db)
    with pytest.raises(AppError) as excinfo:
        await repos.command.trash(2_000_000_000)
    assert excinfo.value.code == 404
    assert excinfo.value.message == "order item not found"


async def test_soft_delete_lifecycle(db: Database, order_parents) -> None:
    repos = new_repositories(db)
    order_id = await _seed_order(db, order_parents)
    product_id = order_parents.product_id
    created = await repos.command.create(_create(order_id, product_id))

    trashed = await repos.command.trash(created.order_item_id)
    assert trashed.deleted_at is not None

    # FindAll / FindActive filter `deleted_at IS NULL`.
    listed = await repos.query.find_all(str(product_id), 1, 10)
    assert all(row.order_item_id != created.order_item_id for row in listed)

    active = await repos.query.find_active(str(product_id), 1, 10)
    assert all(row.order_item_id != created.order_item_id for row in active)

    trashed_rows = await repos.query.find_trashed(str(product_id), 1, 10)
    assert any(row.order_item_id == created.order_item_id for row in trashed_rows)

    # The by-order read also excludes trashed rows.
    by_order = await repos.query.find_order_item_by_order(order_id)
    assert all(row.order_item_id != created.order_item_id for row in by_order)

    restored = await repos.command.restore(created.order_item_id)
    assert restored.deleted_at is None

    active_after = await repos.query.find_active(str(product_id), 1, 10)
    assert any(row.order_item_id == created.order_item_id for row in active_after)


async def test_update_then_delete_permanent(db: Database, order_parents) -> None:
    repos = new_repositories(db)
    order_id = await _seed_order(db, order_parents)
    product_id = order_parents.product_id
    created = await repos.command.create(_create(order_id, product_id))

    updated = await repos.command.update(
        UpdateOrderItemRecordRequest(
            order_item_id=created.order_item_id, quantity=7, price=1234
        )
    )
    assert updated.quantity == 7
    assert updated.price == 1234

    await repos.command.trash(created.order_item_id)
    await repos.command.delete_permanent(created.order_item_id)

    trashed_rows = await repos.query.find_trashed(str(product_id), 1, 10)
    assert all(row.order_item_id != created.order_item_id for row in trashed_rows)


async def test_pagination_reports_total_count(db: Database, order_parents) -> None:
    repos = new_repositories(db)
    order_id = await _seed_order(db, order_parents)
    for _ in range(3):
        await repos.command.create(_create(order_id, order_parents.product_id))
    rows = await repos.query.find_all(str(order_id), 1, 2)
    assert len(rows) == 2
    assert rows[0].total_count >= 3


async def test_delete_by_order_permanent_purges_all_items(
    db: Database, order_parents
) -> None:
    repos = new_repositories(db)
    order_id = await _seed_order(db, order_parents)
    await repos.command.create(_create(order_id, order_parents.product_id))
    await repos.command.create(_create(order_id, order_parents.product_id))

    await repos.command.delete_order_item_by_order_permanent(order_id)
    assert await repos.query.find_order_item_by_order(order_id) == []


async def test_delete_all_clears_items_of_trashed_parent_order(
    db: Database, order_parents
) -> None:
    """`DeleteAll` also purges items whose parent order is trashed."""
    repos = new_repositories(db)
    order_id = await _seed_order(db, order_parents)
    product_id = order_parents.product_id
    created = await repos.command.create(_create(order_id, product_id))
    await db.execute(
        "UPDATE orders SET deleted_at = CURRENT_TIMESTAMP WHERE order_id = :order_id",
        {"order_id": order_id},
    )

    await repos.command.delete_all()

    # The item row is gone even though the item itself was never trashed.
    rows = await repos.query.find_trashed(str(product_id), 1, 10)
    assert all(row.order_item_id != created.order_item_id for row in rows)


async def test_update_missing_order_item_maps_to_not_found(db: Database) -> None:
    repos = new_repositories(db)
    with pytest.raises(AppError) as excinfo:
        await repos.command.update(
            UpdateOrderItemRecordRequest(
                order_item_id=2_000_000_000, quantity=1, price=1
            )
        )
    assert excinfo.value.code == 404

"""Shipping address repository integration tests against a real PostgreSQL.

Marked `integration` (excluded from `make test`). `shipping_addresses` has a
foreign key to `orders` (which now references `users` **and** `merchants`), so
each test uses the `order_parents` fixture (a real user + merchant) and seeds its
own order. A unique `alamat` token is used both as the search key (the SQL
matches `alamat ILIKE`) and to isolate rows. The fixture removes every row it
owns.
"""

from __future__ import annotations

import uuid

import pytest

from pkg.database.database import Database
from service.shipping_address.repository import new_repositories
from shared.domain.requests.shipping_address import (
    CreateShippingAddressRequest,
    UpdateShippingAddressRequest,
)
from shared.errors import AppError

pytestmark = pytest.mark.integration


def _token() -> str:
    return f"Jalan Uji {uuid.uuid4().hex[:10]}"


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


def _create(order_id: int, alamat: str, cost: int = 12000):
    return CreateShippingAddressRequest(
        order_id=order_id,
        alamat=alamat,
        provinsi="DKI Jakarta",
        negara="Indonesia",
        kota="Jakarta",
        courier="JNE",
        shipping_method="REG",
        shipping_cost=cost,
    )


async def test_create_and_find(db: Database, order_parents) -> None:
    repos = new_repositories(db)
    order_id = await _seed_order(db, order_parents)
    alamat = _token()
    created = await repos.command.create(_create(order_id, alamat))
    assert created.shipping_address_id > 0
    assert created.order_id == order_id
    assert created.alamat == alamat
    assert float(created.shipping_cost) == pytest.approx(12000)

    by_id = await repos.query.find_by_id(created.shipping_address_id)
    assert by_id.shipping_address_id == created.shipping_address_id

    by_order = await repos.query.find_by_order(order_id)
    assert by_order.order_id == order_id

    listed = await repos.query.find_all(alamat, 1, 10)
    assert any(
        row.shipping_address_id == created.shipping_address_id for row in listed
    )


async def test_soft_delete_lifecycle(db: Database, order_parents) -> None:
    repos = new_repositories(db)
    order_id = await _seed_order(db, order_parents)
    alamat = _token()
    created = await repos.command.create(_create(order_id, alamat))

    trashed = await repos.command.trash(created.shipping_address_id)
    assert trashed.deleted_at is not None

    # FindAll / FindActive filter `deleted_at IS NULL`.
    listed = await repos.query.find_all(alamat, 1, 10)
    assert all(
        row.shipping_address_id != created.shipping_address_id for row in listed
    )

    active = await repos.query.find_active(alamat, 1, 10)
    assert all(
        row.shipping_address_id != created.shipping_address_id for row in active
    )

    trashed_rows = await repos.query.find_trashed(alamat, 1, 10)
    assert any(
        row.shipping_address_id == created.shipping_address_id
        for row in trashed_rows
    )

    # The by-id / by-order reads also exclude trashed rows.
    with pytest.raises(AppError) as missing:
        await repos.query.find_by_id(created.shipping_address_id)
    assert missing.value.code == 404

    restored = await repos.command.restore(created.shipping_address_id)
    assert restored.deleted_at is None

    active_after = await repos.query.find_active(alamat, 1, 10)
    assert any(
        row.shipping_address_id == created.shipping_address_id
        for row in active_after
    )


async def test_update_then_delete_permanent(db: Database, order_parents) -> None:
    repos = new_repositories(db)
    order_id = await _seed_order(db, order_parents)
    alamat = _token()
    created = await repos.command.create(_create(order_id, alamat))

    updated = await repos.command.update(
        UpdateShippingAddressRequest(
            shipping_id=created.shipping_address_id,
            order_id=order_id,
            alamat=alamat,
            provinsi="Jawa Barat",
            negara="Indonesia",
            kota="Bandung",
            courier="SICEPAT",
            shipping_method="EXP",
            shipping_cost=20000,
        )
    )
    assert updated.kota == "Bandung"
    assert float(updated.shipping_cost) == pytest.approx(20000)

    await repos.command.trash(created.shipping_address_id)
    await repos.command.delete_permanent(created.shipping_address_id)

    trashed_rows = await repos.query.find_trashed(alamat, 1, 10)
    assert all(
        row.shipping_address_id != created.shipping_address_id
        for row in trashed_rows
    )


async def test_pagination_reports_total_count(db: Database, order_parents) -> None:
    repos = new_repositories(db)
    order_id = await _seed_order(db, order_parents)
    prefix = f"Jalan Uji {uuid.uuid4().hex[:10]}"
    for i in range(3):
        await repos.command.create(_create(order_id, f"{prefix} {i}"))
    rows = await repos.query.find_all(prefix, 1, 2)
    assert len(rows) == 2
    assert rows[0].total_count >= 3


async def test_delete_by_order_permanent_purges_all(
    db: Database, order_parents
) -> None:
    repos = new_repositories(db)
    order_id = await _seed_order(db, order_parents)
    await repos.command.create(_create(order_id, _token()))
    await repos.command.create(_create(order_id, _token()))

    await repos.command.delete_by_order_id_permanent(order_id)

    with pytest.raises(AppError):
        await repos.query.find_by_order(order_id)


async def test_delete_all_clears_addresses_of_trashed_parent_order(
    db: Database, order_parents
) -> None:
    """`DeleteAll` also purges addresses whose parent order is trashed."""
    repos = new_repositories(db)
    order_id = await _seed_order(db, order_parents)
    alamat = _token()
    created = await repos.command.create(_create(order_id, alamat))
    await db.execute(
        "UPDATE orders SET deleted_at = CURRENT_TIMESTAMP WHERE order_id = :order_id",
        {"order_id": order_id},
    )

    await repos.command.delete_all()

    # The row is gone even though the address itself was never trashed.
    rows = await repos.query.find_trashed(alamat, 1, 10)
    assert all(
        row.shipping_address_id != created.shipping_address_id for row in rows
    )


async def test_restore_all_restores_trashed_addresses(
    db: Database, order_parents
) -> None:
    repos = new_repositories(db)
    order_id = await _seed_order(db, order_parents)
    alamat = _token()
    created = await repos.command.create(_create(order_id, alamat))
    await repos.command.trash(created.shipping_address_id)

    await repos.command.restore_all()

    active = await repos.query.find_active(alamat, 1, 10)
    assert any(
        row.shipping_address_id == created.shipping_address_id for row in active
    )


async def test_missing_shipping_address_maps_to_not_found(db: Database) -> None:
    repos = new_repositories(db)
    with pytest.raises(AppError) as excinfo:
        await repos.command.trash(2_000_000_000)
    assert excinfo.value.code == 404
    assert excinfo.value.message == "shipping address not found"


async def test_update_missing_shipping_address_maps_to_not_found(db: Database) -> None:
    repos = new_repositories(db)
    with pytest.raises(AppError) as excinfo:
        await repos.command.update(
            UpdateShippingAddressRequest(shipping_id=2_000_000_000, kota="X")
        )
    assert excinfo.value.code == 404

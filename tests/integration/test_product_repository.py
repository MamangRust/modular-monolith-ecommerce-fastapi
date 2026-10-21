"""product repository integration tests. Marked `integration` (excluded from `make test`). `products.merchant_id` and `products.category_id` both have `ON DELETE CASCADE` FKs, so each test seeds its own user + merchant + category and removes them afterwards.: - `create`/`update` persist `rating` (port normalisation; drops it); - `find_all`/`find_active` require `deleted_at IS NULL`; `find_trashed` requires `deleted_at IS NOT NULL`; - `find_by_id` adds `AND deleted_at IS NULL` and maps a missing row to 404; - `update_product_count_stock` only updates when `stock >= 0`, so a negative value yields no row -> 404; - `adjust_product_stock` is idempotent per `(operation_id, product_id, delta)` and refuses to drive the stock negative; - `delete_permanent` only affects trashed rows."""

from __future__ import annotations

import uuid

import grpc
import pytest

from service.product.repository import GuardOptions, new_repositories
from shared.domain.requests.product import (
    CreateProductRequest,
    UpdateProductRequest,
)
from shared.errors import AppError

pytestmark = pytest.mark.integration


@pytest.fixture
async def repos(db):
    """product repositories with unused category/merchant channels."""
    category_channel = grpc.aio.insecure_channel("127.0.0.1:1")
    merchant_channel = grpc.aio.insecure_channel("127.0.0.1:1")
    try:
        yield new_repositories(
            db,
            category_channel=category_channel,
            merchant_channel=merchant_channel,
            guards=GuardOptions(),
        )
    finally:
        await category_channel.close()
        await merchant_channel.close()


async def _seed(db) -> tuple[int, int, int, str, str]:
    email = f"test_product_{uuid.uuid4().hex[:10]}@example.com"
    merchant_name = f"Merchant {uuid.uuid4().hex[:10]}"
    category_name = f"Category {uuid.uuid4().hex[:10]}"
    user = await db.execute(
        """
        INSERT INTO users (firstname, lastname, email, password, verification_code)
        VALUES ('T', 'U', :email, 'x', 'v')
        RETURNING user_id
        """,
        {"email": email},
    )
    assert user is not None
    user_id = int(user["user_id"])
    merchant = await db.execute(
        """
        INSERT INTO merchants (
            user_id, name, description, address, contact_email, contact_phone, status
        )
        VALUES (:user_id, :name, 'd', 'a', 'e@f.com', '0812', 'active')
        RETURNING merchant_id
        """,
        {"user_id": user_id, "name": merchant_name},
    )
    assert merchant is not None
    merchant_id = int(merchant["merchant_id"])
    category = await db.execute(
        """
        INSERT INTO categories (name, description, slug_category, image_category)
        VALUES (:name, 'd', :slug, 'img.jpg')
        RETURNING category_id
        """,
        {"name": category_name, "slug": uuid.uuid4().hex[:10]},
    )
    assert category is not None
    category_id = int(category["category_id"])
    return user_id, merchant_id, category_id, merchant_name, category_name


async def _cleanup(db, user_id: int, merchant_id: int, category_id: int) -> None:
    await db.execute(
        "DELETE FROM products WHERE merchant_id = :mid", {"mid": merchant_id}
    )
    await db.execute(
        "DELETE FROM categories WHERE category_id = :cid", {"cid": category_id}
    )
    await db.execute(
        "DELETE FROM merchants WHERE merchant_id = :mid", {"mid": merchant_id}
    )
    await db.execute("DELETE FROM users WHERE user_id = :uid", {"uid": user_id})


def _create(merchant_id: int, category_id: int, **overrides) -> CreateProductRequest:
    values = {
        "merchant_id": merchant_id,
        "category_id": category_id,
        "name": f"Galaxy S24 {uuid.uuid4().hex[:6]}",
        "description": "desc",
        "price": 1200,
        "count_in_stock": 5,
        "brand": "Samsung",
        "weight": 200,
        "rating": 4,
        "slug_product": f"galaxy-{uuid.uuid4().hex[:8]}",
        "image_product": "uploads/products/galaxy.jpg",
    }
    values.update(overrides)
    return CreateProductRequest(**values)


async def test_create_persists_rating_and_find(db, repos) -> None:
    user_id, merchant_id, category_id, _, category_name = await _seed(db)
    try:
        created = await repos.product_command.create(
            _create(merchant_id, category_id, rating=4)
        )
        assert created.product_id > 0
        # Port normalisation: rating is persisted (drops it).
        assert created.rating == 4.0

        by_id = await repos.product_query.find_by_id(created.product_id)
        assert by_id.product_id == created.product_id
        assert by_id.description == "desc"

        listed = await repos.product_query.find_all(created.name, 1, 10)
        assert any(row.product_id == created.product_id for row in listed)
        assert listed[0].total_count >= 1

        by_category = await repos.product_query.find_by_category(
            category_name, "", 0, 0, 1, 10
        )
        assert any(row.product_id == created.product_id for row in by_category)
        assert by_category[0].category_name == category_name
    finally:
        await _cleanup(db, user_id, merchant_id, category_id)


async def test_update_changes_fields(db, repos) -> None:
    user_id, merchant_id, category_id, _, _ = await _seed(db)
    try:
        created = await repos.product_command.create(_create(merchant_id, category_id))
        updated = await repos.product_command.update(
            UpdateProductRequest(
                product_id=created.product_id,
                merchant_id=merchant_id,
                category_id=category_id,
                name="Galaxy S25 Ultra",
                description="updated",
                price=1500,
                count_in_stock=8,
                brand="Samsung",
                weight=210,
                rating=5,
                slug_product=created.slug_product,
                image_product=created.image_product,
            )
        )
        assert updated.name == "Galaxy S25 Ultra"
        assert updated.price == 1500
        assert updated.rating == 5.0
    finally:
        await _cleanup(db, user_id, merchant_id, category_id)


async def test_soft_delete_lifecycle(db, repos) -> None:
    user_id, merchant_id, category_id, _, _ = await _seed(db)
    try:
        created = await repos.product_command.create(_create(merchant_id, category_id))
        product_id = created.product_id

        # The single-row trash/restore projection omits `deleted_at` (
        # with `TrashProductRow`/`RestoreProductRow`), so the soft-delete
        # state is asserted through the list queries instead.
        trashed = await repos.product_command.trash(product_id)
        assert trashed.product_id == product_id

        listed = await repos.product_query.find_all(created.name, 1, 10)
        assert all(row.product_id != product_id for row in listed)
        trashed_rows = await repos.product_query.find_trashed(created.name, 1, 10)
        assert any(row.product_id == product_id for row in trashed_rows)

        with pytest.raises(AppError) as missing:
            await repos.product_query.find_by_id(product_id)
        assert missing.value.code == 404

        restored = await repos.product_command.restore(product_id)
        assert restored.product_id == product_id
        active = await repos.product_query.find_active(created.name, 1, 10)
        assert any(row.product_id == product_id for row in active)
    finally:
        await _cleanup(db, user_id, merchant_id, category_id)


async def test_find_by_merchant_filters(db, repos) -> None:
    user_id, merchant_id, category_id, _, _ = await _seed(db)
    try:
        cheap = await repos.product_command.create(
            _create(merchant_id, category_id, name="Cheap Item", price=50)
        )
        pricey = await repos.product_command.create(
            _create(merchant_id, category_id, name="Pricey Item", price=5000)
        )

        all_rows = await repos.product_query.find_by_merchant(
            merchant_id, 0, "", 0, 0, 1, 10
        )
        ids = {row.product_id for row in all_rows}
        assert {cheap.product_id, pricey.product_id} <= ids

        bounded = await repos.product_query.find_by_merchant(
            merchant_id, 0, "", 0, 100, 1, 10
        )
        bounded_ids = {row.product_id for row in bounded}
        assert cheap.product_id in bounded_ids
        assert pricey.product_id not in bounded_ids

        by_category = await repos.product_query.find_by_merchant(
            merchant_id, category_id, "", 0, 0, 1, 10
        )
        assert any(row.product_id == cheap.product_id for row in by_category)
    finally:
        await _cleanup(db, user_id, merchant_id, category_id)


async def test_count_stock_update_and_negative_guard(db, repos) -> None:
    user_id, merchant_id, category_id, _, _ = await _seed(db)
    try:
        created = await repos.product_command.create(_create(merchant_id, category_id))
        row = await repos.product_command.update_product_count_stock(
            created.product_id, 20
        )
        assert row.count_in_stock == 20

        # A negative target is rejected by the SQL guard (no row -> 404).
        with pytest.raises(AppError) as excinfo:
            await repos.product_command.update_product_count_stock(
                created.product_id, -1
            )
        assert excinfo.value.code == 404
    finally:
        await _cleanup(db, user_id, merchant_id, category_id)


async def test_adjust_product_stock_is_idempotent(db, repos) -> None:
    user_id, merchant_id, category_id, _, _ = await _seed(db)
    try:
        created = await repos.product_command.create(
            _create(merchant_id, category_id, count_in_stock=10)
        )
        op = uuid.uuid4().hex

        first = await repos.product_command.adjust_product_stock(
            created.product_id, -3, op
        )
        assert first.count_in_stock == 7

        # Replaying the same operation does not apply the delta again.
        replay = await repos.product_command.adjust_product_stock(
            created.product_id, -3, op
        )
        assert replay.count_in_stock == 7

        # A different operation applies normally.
        second = await repos.product_command.adjust_product_stock(
            created.product_id, 5, uuid.uuid4().hex
        )
        assert second.count_in_stock == 12

        # Driving the stock negative is refused (no row -> 404).
        with pytest.raises(AppError) as excinfo:
            await repos.product_command.adjust_product_stock(
                created.product_id, -100, uuid.uuid4().hex
            )
        assert excinfo.value.code == 404
    finally:
        await _cleanup(db, user_id, merchant_id, category_id)


async def test_delete_permanent_requires_trashed(db, repos) -> None:
    user_id, merchant_id, category_id, _, _ = await _seed(db)
    try:
        created = await repos.product_command.create(_create(merchant_id, category_id))
        product_id = created.product_id

        # A live row is not deleted (SQL guards deleted_at IS NOT NULL).
        await repos.product_command.delete_permanent(product_id)
        still_there = await repos.product_query.find_by_id(product_id)
        assert still_there.product_id == product_id

        await repos.product_command.trash(product_id)
        await repos.product_command.delete_permanent(product_id)
        trashed_rows = await repos.product_query.find_trashed(created.name, 1, 10)
        assert all(row.product_id != product_id for row in trashed_rows)
    finally:
        await _cleanup(db, user_id, merchant_id, category_id)


async def test_missing_maps_to_not_found(db, repos) -> None:
    with pytest.raises(AppError) as excinfo:
        await repos.product_query.find_by_id(2_000_000_000)
    assert excinfo.value.code == 404
    assert excinfo.value.message == "product not found"

    with pytest.raises(AppError) as trash_missing:
        await repos.product_command.trash(2_000_000_000)
    assert trash_missing.value.code == 404


async def test_pagination_reports_total_count(db, repos) -> None:
    user_id, merchant_id, category_id, _, _ = await _seed(db)
    try:
        prefix = f"Bulk {uuid.uuid4().hex[:6]}"
        for index in range(3):
            await repos.product_command.create(
                _create(merchant_id, category_id, name=f"{prefix} {index}")
            )
        rows = await repos.product_query.find_all(prefix, 1, 2)
        assert len(rows) == 2
        assert rows[0].total_count >= 3
    finally:
        await _cleanup(db, user_id, merchant_id, category_id)


async def test_restore_all_and_delete_all(db, repos) -> None:
    user_id, merchant_id, category_id, _, _ = await _seed(db)
    try:
        created = await repos.product_command.create(_create(merchant_id, category_id))
        product_id = created.product_id
        await repos.product_command.trash(product_id)

        await repos.product_command.restore_all()
        active = await repos.product_query.find_active(created.name, 1, 10)
        assert any(row.product_id == product_id for row in active)

        await repos.product_command.trash(product_id)
        await repos.product_command.delete_all()
        trashed_rows = await repos.product_query.find_trashed(created.name, 1, 10)
        assert all(row.product_id != product_id for row in trashed_rows)
    finally:
        await _cleanup(db, user_id, merchant_id, category_id)


__all__ = []

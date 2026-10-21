"""cart repository integration tests. Marked `integration` (excluded from `make test`). `carts.product_id` has `ON DELETE CASCADE` but `carts.user_id` is a plain FK, so each test seeds its own user + merchant + category + product and removes them (carts first) afterwards.: - `create` returns the base columns (no `deleted_at`) and snapshots the product; - `find_all` filters by `user_id`, requires `deleted_at IS NULL`, matches `name`/`price::TEXT` with `ILIKE`, and reports the window `total_count`; - `delete_permanent`/`delete_all_permanently` are hard deletes and always report success (`:exec` in — deleting a missing cart is not a 404)."""

from __future__ import annotations

import uuid
from dataclasses import replace
from typing import Any

import grpc
import pytest

from service.cart.repository import GuardOptions, new_repositories
from shared.domain.requests.cart import (
    CartCreateRecord,
    DeleteAllCartRequest,
    DeleteCartRequest,
    FindAllCarts,
)

pytestmark = pytest.mark.integration


@pytest.fixture
async def repos(db):
    """cart repositories with unused user/product channels."""
    user_channel = grpc.aio.insecure_channel("127.0.0.1:1")
    product_channel = grpc.aio.insecure_channel("127.0.0.1:1")
    try:
        yield new_repositories(
            db,
            user_channel=user_channel,
            product_channel=product_channel,
            guards=GuardOptions(),
        )
    finally:
        await user_channel.close()
        await product_channel.close()


async def _seed(db) -> tuple[int, int, int, int, str, int, str]:
    """Seed user + merchant + category + product; return ids and product facts."""
    email = f"test_cart_{uuid.uuid4().hex[:10]}@example.com"
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
    product = await db.execute(
        """
        INSERT INTO products (
            merchant_id, category_id, name, description, price,
            count_in_stock, brand, weight, rating, slug_product, image_product
        )
        VALUES (
            :mid, :cid, :name, 'd', 1200, 5, 'Samsung', 200, 4.5, :slug, 'galaxy-s24.jpg'
        )
        RETURNING product_id
        """,
        {
            "mid": merchant_id,
            "cid": category_id,
            "name": f"Galaxy S24 {uuid.uuid4().hex[:6]}",
            "slug": f"galaxy-{uuid.uuid4().hex[:8]}",
        },
    )
    assert product is not None
    product_id = int(product["product_id"])
    return user_id, product_id, merchant_id, category_id, "Galaxy S24", 1200, "galaxy-s24.jpg"


async def _cleanup(db, user_id: int, merchant_id: int, category_id: int) -> None:
    await db.execute("DELETE FROM carts WHERE user_id = :uid", {"uid": user_id})
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


def _record(user_id: int, product_id: int, **overrides: Any) -> CartCreateRecord:
    base = CartCreateRecord(
        product_id=product_id,
        user_id=user_id,
        name="Galaxy S24",
        price=1200,
        image_product="galaxy-s24.jpg",
        quantity=2,
        weight=200,
    )
    return replace(base, **overrides)


async def test_create_and_find_all(db, repos) -> None:
    user_id, product_id, merchant_id, category_id, name, price, image = await _seed(db)
    try:
        created = await repos.cart_command.create(_record(user_id, product_id))
        assert created.cart_id > 0
        assert created.user_id == user_id
        assert created.product_id == product_id
        assert created.name == name
        assert created.price == price
        assert created.image == image
        assert created.quantity == 2
        assert created.weight == 200

        rows = await repos.cart_query.find_all(
            FindAllCarts(user_id=user_id, page=1, page_size=10, search="")
        )
        assert any(row.cart_id == created.cart_id for row in rows)
        assert rows[0].total_count >= 1
    finally:
        await _cleanup(db, user_id, merchant_id, category_id)


async def test_find_all_filters_by_user_and_search(db, repos) -> None:
    user_id, product_id, merchant_id, category_id, _, _, _ = await _seed(db)
    try:
        await repos.cart_command.create(_record(user_id, product_id, name="Cheap Item", price=50))
        await repos.cart_command.create(_record(user_id, product_id, name="Pricey Item", price=5000))

        by_name = await repos.cart_query.find_all(
            FindAllCarts(user_id=user_id, page=1, page_size=10, search="Cheap")
        )
        assert len(by_name) == 1
        assert by_name[0].name == "Cheap Item"

        # price::TEXT is searchable too.
        by_price = await repos.cart_query.find_all(
            FindAllCarts(user_id=user_id, page=1, page_size=10, search="5000")
        )
        assert len(by_price) == 1
        assert by_price[0].name == "Pricey Item"

        # A different user sees nothing.
        other = await repos.cart_query.find_all(
            FindAllCarts(user_id=user_id + 1, page=1, page_size=10, search="")
        )
        assert other == []
    finally:
        await _cleanup(db, user_id, merchant_id, category_id)


async def test_pagination_reports_total_count(db, repos) -> None:
    user_id, product_id, merchant_id, category_id, _, _, _ = await _seed(db)
    try:
        prefix = f"Bulk {uuid.uuid4().hex[:6]}"
        for index in range(3):
            await repos.cart_command.create(
                _record(user_id, product_id, name=f"{prefix} {index}")
            )
        rows = await repos.cart_query.find_all(
            FindAllCarts(user_id=user_id, page=1, page_size=2, search=prefix)
        )
        assert len(rows) == 2
        assert rows[0].total_count >= 3
    finally:
        await _cleanup(db, user_id, merchant_id, category_id)


async def test_delete_permanent_is_hard_delete(db, repos) -> None:
    user_id, product_id, merchant_id, category_id, _, _, _ = await _seed(db)
    try:
        created = await repos.cart_command.create(_record(user_id, product_id))
        success = await repos.cart_command.delete_permanent(
            DeleteCartRequest(cart_id=created.cart_id, user_id=user_id)
        )
        assert success is True

        rows = await repos.cart_query.find_all(
            FindAllCarts(user_id=user_id, page=1, page_size=10, search="")
        )
        assert all(row.cart_id != created.cart_id for row in rows)

        again = await repos.cart_command.delete_permanent(
            DeleteCartRequest(cart_id=created.cart_id, user_id=user_id)
        )
        assert again is True
    finally:
        await _cleanup(db, user_id, merchant_id, category_id)


async def test_delete_all_permanently_only_given_ids_for_user(db, repos) -> None:
    user_id, product_id, merchant_id, category_id, _, _, _ = await _seed(db)
    try:
        first = await repos.cart_command.create(_record(user_id, product_id, name="First"))
        second = await repos.cart_command.create(_record(user_id, product_id, name="Second"))
        third = await repos.cart_command.create(_record(user_id, product_id, name="Third"))

        success = await repos.cart_command.delete_all_permanently(
            DeleteAllCartRequest(user_id=user_id, cart_ids=[first.cart_id, second.cart_id])
        )
        assert success is True

        rows = await repos.cart_query.find_all(
            FindAllCarts(user_id=user_id, page=1, page_size=10, search="")
        )
        remaining = {row.cart_id for row in rows}
        assert third.cart_id in remaining
        assert first.cart_id not in remaining
        assert second.cart_id not in remaining
    finally:
        await _cleanup(db, user_id, merchant_id, category_id)


__all__ = []

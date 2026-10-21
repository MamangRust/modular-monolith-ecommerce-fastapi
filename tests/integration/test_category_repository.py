"""Category repository integration tests against a real PostgreSQL.

Marked `integration` (excluded from `make test`). Every test uses a unique
`TEST_<PREFIX>_...` name/slug and removes only its own rows.

The stats repositories are exercised separately and skipped until the
`orders`/`order_items`/`products` tables exist (they are added by the
product/order_item/order stages) — the stats SQL joins all four tables.
"""

from __future__ import annotations

import uuid

import pytest

from pkg.database.database import Database
from service.category.repository import new_repositories
from shared.domain.requests.category import CreateCategoryRequest, UpdateCategoryRequest
from shared.errors import AppError

pytestmark = pytest.mark.integration


def _name(prefix: str) -> str:
    return f"TEST_{prefix}_{uuid.uuid4().hex[:10]}"


def _create(name: str, **overrides) -> CreateCategoryRequest:
    data = {
        "name": name,
        "description": "integration test category",
        "slug_category": f"test-{uuid.uuid4().hex[:12]}",
        "image_category": "test.png",
    }
    data.update(overrides)
    return CreateCategoryRequest(**data)


async def _cleanup(db: Database, prefix: str) -> None:
    await db.execute(
        "DELETE FROM categories WHERE name LIKE :pattern",
        {"pattern": f"TEST_{prefix}%"},
    )


async def _tables_exist(db: Database, *tables: str) -> bool:
    for table in tables:
        row = await db.scalar("SELECT to_regclass(:name) AS reg", {"name": table})
        if row is None or row["reg"] is None:
            return False
    return True


async def test_create_find_by_id(db: Database) -> None:
    repos = new_repositories(db)
    name = _name("CREATE")
    try:
        created = await repos.command.create(_create(name))
        assert created.category_id > 0
        assert created.created_at is not None

        found = await repos.query.find_by_id(created.category_id)
        assert found.name == name
        assert found.slug_category is not None
    finally:
        await _cleanup(db, "CREATE")


async def test_missing_category_maps_to_not_found(db: Database) -> None:
    repos = new_repositories(db)
    with pytest.raises(AppError) as excinfo:
        await repos.query.find_by_id(2_000_000_000)
    assert excinfo.value.code == 404
    assert excinfo.value.message == "Category not found"


async def test_find_all_excludes_trashed_rows(db: Database) -> None:
    """Unlike banner, category `FindAll` filters `deleted_at IS NULL`."""
    repos = new_repositories(db)
    name = _name("ALL")
    try:
        created = await repos.command.create(_create(name))
        await repos.command.trash(created.category_id)

        rows = await repos.query.find_all(name, 1, 10)
        assert all(row.category_id != created.category_id for row in rows)
    finally:
        await _cleanup(db, "ALL")


async def test_soft_delete_lifecycle(db: Database) -> None:
    repos = new_repositories(db)
    name = _name("SOFT")
    try:
        created = await repos.command.create(_create(name))

        trashed = await repos.command.trash(created.category_id)
        assert trashed.deleted_at is not None

        # FindByID filters `deleted_at IS NULL`, so a trashed row is gone.
        with pytest.raises(AppError):
            await repos.query.find_by_id(created.category_id)

        active = await repos.query.find_active(name, 1, 10)
        assert all(row.category_id != created.category_id for row in active)

        trashed_rows = await repos.query.find_trashed(name, 1, 10)
        assert any(row.category_id == created.category_id for row in trashed_rows)

        # FindByIDTrashed only returns the trashed row.
        found_trashed = await repos.query.find_by_id_trashed(created.category_id)
        assert found_trashed.deleted_at is not None

        restored = await repos.command.restore(created.category_id)
        assert restored.deleted_at is None

        active_after = await repos.query.find_active(name, 1, 10)
        assert any(row.category_id == created.category_id for row in active_after)
    finally:
        await _cleanup(db, "SOFT")


async def test_pagination_reports_total_count(db: Database) -> None:
    repos = new_repositories(db)
    names = [_name("PAGE") for _ in range(3)]
    try:
        for name in names:
            await repos.command.create(_create(name))
        rows = await repos.query.find_all("TEST_PAGE", 1, 2)
        assert len(rows) == 2
        assert rows[0].total_count >= 3
    finally:
        await _cleanup(db, "PAGE")


async def test_update_then_delete_permanent(db: Database) -> None:
    repos = new_repositories(db)
    name = _name("UPD")
    try:
        created = await repos.command.create(_create(name))
        updated = await repos.command.update(
            UpdateCategoryRequest(
                category_id=created.category_id,
                name=f"{name}_X",
                description="updated",
                slug_category=f"test-upd-{uuid.uuid4().hex[:12]}",
                image_category="updated.png",
            )
        )
        assert updated.name == f"{name}_X"

        await repos.command.trash(created.category_id)
        await repos.command.delete_permanent(created.category_id)

        with pytest.raises(AppError):
            await repos.query.find_by_id(created.category_id)
    finally:
        await _cleanup(db, "UPD")


async def test_update_missing_category_maps_to_not_found(db: Database) -> None:
    repos = new_repositories(db)
    with pytest.raises(AppError) as excinfo:
        await repos.command.update(
            UpdateCategoryRequest(
                category_id=2_000_000_000,
                name="X",
                description="d",
                slug_category=f"test-{uuid.uuid4().hex[:12]}",
                image_category="x.png",
            )
        )
    assert excinfo.value.code == 404


async def test_search_is_case_insensitive(db: Database) -> None:
    repos = new_repositories(db)
    name = _name("CASE")
    try:
        await repos.command.create(_create(name))
        rows = await repos.query.find_all(name.lower(), 1, 10)
        assert any(row.name == name for row in rows)
    finally:
        await _cleanup(db, "CASE")


async def test_stats_queries_run_once_dependencies_exist(db: Database) -> None:
    """Stats SQL joins orders/order_items/products; skip until they exist."""
    if not await _tables_exist(db, "orders", "order_items", "products"):
        pytest.skip("orders/order_items/products tables not migrated yet")

    repos = new_repositories(db)
    monthly = await repos.stats.get_monthly_total_price(2026, 1)
    yearly = await repos.stats.get_yearly_total_prices(2026)
    month_price = await repos.stats.get_month_price(2026)
    year_price = await repos.stats.get_year_price(2026)
    assert isinstance(monthly, list)
    assert isinstance(yearly, list)
    assert isinstance(month_price, list)
    assert isinstance(year_price, list)

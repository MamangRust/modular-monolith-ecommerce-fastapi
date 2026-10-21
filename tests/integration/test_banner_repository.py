"""Banner repository integration tests against a real PostgreSQL.

Marked `integration` (excluded from `make test`). Every test uses a unique
`TEST_<PREFIX>_...` name and removes only its own rows."""

from __future__ import annotations

import uuid

import pytest

from pkg.database.database import Database
from service.banner.repository import new_repositories
from shared.domain.requests.banner import CreateBannerRequest, UpdateBannerRequest
from shared.errors import AppError

pytestmark = pytest.mark.integration


def _name(prefix: str) -> str:
    return f"TEST_{prefix}_{uuid.uuid4().hex[:10]}"


def _create(name: str, **overrides) -> CreateBannerRequest:
    data = {
        "name": name,
        "start_date": "2023-01-01",
        "end_date": "2023-01-31",
        "start_time": "08:00:00",
        "end_time": "16:00:00",
        "is_active": True,
    }
    data.update(overrides)
    return CreateBannerRequest(**data)


async def _cleanup(db: Database, prefix: str) -> None:
    await db.execute(
        "DELETE FROM banners WHERE name LIKE :pattern", {"pattern": f"TEST_{prefix}%"}
    )


async def test_create_find_by_id(db: Database) -> None:
    repos = new_repositories(db)
    name = _name("CREATE")
    try:
        created = await repos.command.create(_create(name))
        assert created.banner_id > 0
        assert created.start_date.isoformat() == "2023-01-01"
        assert created.start_time.isoformat() == "08:00:00"

        found = await repos.query.find_by_id(created.banner_id)
        assert found.name == name
        assert found.is_active is True
    finally:
        await _cleanup(db, "CREATE")


async def test_missing_banner_maps_to_not_found(db: Database) -> None:
    repos = new_repositories(db)
    with pytest.raises(AppError) as excinfo:
        await repos.query.find_by_id(2_000_000_000)
    assert excinfo.value.code == 404
    assert excinfo.value.message == "Banner not found"


async def test_find_all_returns_trashed_rows(db: Database) -> None:
    repos = new_repositories(db)
    name = _name("ALL")
    try:
        created = await repos.command.create(_create(name))
        await repos.command.trash(created.banner_id)

        rows = await repos.query.find_all(name, 1, 10)
        assert any(row.banner_id == created.banner_id for row in rows)
    finally:
        await _cleanup(db, "ALL")


async def test_soft_delete_lifecycle(db: Database) -> None:
    repos = new_repositories(db)
    name = _name("SOFT")
    try:
        created = await repos.command.create(_create(name))

        trashed = await repos.command.trash(created.banner_id)
        assert trashed.deleted_at is not None

        # FindByID filters `deleted_at IS NULL`, so a trashed row is gone.
        with pytest.raises(AppError):
            await repos.query.find_by_id(created.banner_id)

        active = await repos.query.find_active(name, 1, 10)
        assert all(row.banner_id != created.banner_id for row in active)

        trashed_rows = await repos.query.find_trashed(name, 1, 10)
        assert any(row.banner_id == created.banner_id for row in trashed_rows)

        restored = await repos.command.restore(created.banner_id)
        assert restored.deleted_at is None

        active_after = await repos.query.find_active(name, 1, 10)
        assert any(row.banner_id == created.banner_id for row in active_after)
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
            UpdateBannerRequest(
                banner_id=created.banner_id,
                name=f"{name}_X",
                start_date="2023-02-01",
                end_date="2023-02-28",
                start_time="09:00:00",
                end_time="17:00:00",
                is_active=False,
            )
        )
        assert updated.name == f"{name}_X"
        assert updated.is_active is False

        await repos.command.trash(created.banner_id)
        await repos.command.delete_permanent(created.banner_id)

        with pytest.raises(AppError):
            await repos.query.find_by_id(created.banner_id)
    finally:
        await _cleanup(db, "UPD")


async def test_update_missing_banner_maps_to_not_found(db: Database) -> None:
    repos = new_repositories(db)
    with pytest.raises(AppError) as excinfo:
        await repos.command.update(
            UpdateBannerRequest(
                banner_id=2_000_000_000,
                name="X",
                start_date="2023-01-01",
                end_date="2023-01-31",
                start_time="08:00:00",
                end_time="16:00:00",
                is_active=True,
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

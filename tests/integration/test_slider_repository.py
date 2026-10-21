"""Slider repository integration tests against a real PostgreSQL. Marked `integration` (excluded from `make test`). The `sliders` table is standalone (no foreign keys), so each test only seeds its own rows and deletes them afterwards. A unique `name` token is used as the search key (the SQL matches `name ILIKE`)."""

from __future__ import annotations

import uuid

import pytest

from service.slider.repository import new_repositories
from shared.domain.requests.slider import CreateSliderRequest, UpdateSliderRequest
from shared.errors import AppError

pytestmark = pytest.mark.integration


def _name() -> str:
    return f"Hero {uuid.uuid4().hex[:10]}"


def _create(name: str) -> CreateSliderRequest:
    return CreateSliderRequest(name=name, image=f"/img/{uuid.uuid4().hex[:6]}.png")


async def _cleanup(db, slider_id: int) -> None:
    await db.execute(
        "DELETE FROM sliders WHERE slider_id = :slider_id", {"slider_id": slider_id}
    )


async def test_create_and_find(db) -> None:
    repos = new_repositories(db)
    name = _name()
    try:
        created = await repos.command.create(_create(name))
        assert created.slider_id > 0
        assert created.name == name

        by_id = await repos.query.find_by_id(created.slider_id)
        assert by_id.slider_id == created.slider_id

        listed = await repos.query.find_all(name, 1, 10)
        assert any(row.slider_id == created.slider_id for row in listed)
    finally:
        await _cleanup(db, created.slider_id)


async def test_soft_delete_lifecycle(db) -> None:
    repos = new_repositories(db)
    name = _name()
    created = await repos.command.create(_create(name))
    try:
        trashed = await repos.command.trash(created.slider_id)
        assert trashed.deleted_at is not None

        # FindAll / FindActive filter `deleted_at IS NULL`.
        listed = await repos.query.find_all(name, 1, 10)
        assert all(row.slider_id != created.slider_id for row in listed)

        active = await repos.query.find_active(name, 1, 10)
        assert all(row.slider_id != created.slider_id for row in active)

        trashed_rows = await repos.query.find_trashed(name, 1, 10)
        assert any(row.slider_id == created.slider_id for row in trashed_rows)

        # FindById excludes trashed rows.
        with pytest.raises(AppError) as missing:
            await repos.query.find_by_id(created.slider_id)
        assert missing.value.code == 404

        restored = await repos.command.restore(created.slider_id)
        assert restored.deleted_at is None

        active_after = await repos.query.find_active(name, 1, 10)
        assert any(row.slider_id == created.slider_id for row in active_after)
    finally:
        await _cleanup(db, created.slider_id)


async def test_update_then_delete_permanent(db) -> None:
    repos = new_repositories(db)
    name = _name()
    created = await repos.command.create(_create(name))
    try:
        updated = await repos.command.update(
            UpdateSliderRequest(
                slider_id=created.slider_id,
                name=f"{name}-v2",
                image="/img/updated.png",
            )
        )
        assert updated.name == f"{name}-v2"
        assert updated.image == "/img/updated.png"

        await repos.command.trash(created.slider_id)
        await repos.command.delete_permanent(created.slider_id)

        trashed_rows = await repos.query.find_trashed(name, 1, 10)
        assert all(row.slider_id != created.slider_id for row in trashed_rows)
    finally:
        await _cleanup(db, created.slider_id)


async def test_pagination_reports_total_count(db) -> None:
    repos = new_repositories(db)
    prefix = f"Hero {uuid.uuid4().hex[:10]}"
    ids: list[int] = []
    try:
        for i in range(3):
            row = await repos.command.create(_create(f"{prefix}-{i}"))
            ids.append(row.slider_id)
        rows = await repos.query.find_all(prefix, 1, 2)
        assert len(rows) == 2
        assert rows[0].total_count >= 3
    finally:
        for sid in ids:
            await _cleanup(db, sid)


async def test_delete_permanent_ignores_missing_row(db) -> None:
    """DeleteSliderPermanent ignores RowsAffected (no 404)."""
    repos = new_repositories(db)
    # Should not raise.
    assert await repos.command.delete_permanent(2_000_000_000) is True


async def test_restore_all_restores_trashed_sliders(db) -> None:
    repos = new_repositories(db)
    name = _name()
    created = await repos.command.create(_create(name))
    try:
        await repos.command.trash(created.slider_id)

        await repos.command.restore_all()

        active = await repos.query.find_active(name, 1, 10)
        assert any(row.slider_id == created.slider_id for row in active)
    finally:
        await _cleanup(db, created.slider_id)


async def test_delete_all_permanent_clears_trashed(db) -> None:
    repos = new_repositories(db)
    name = _name()
    created = await repos.command.create(_create(name))
    try:
        await repos.command.trash(created.slider_id)

        await repos.command.delete_all_permanent()

        rows = await repos.query.find_trashed(name, 1, 10)
        assert all(row.slider_id != created.slider_id for row in rows)
    finally:
        await _cleanup(db, created.slider_id)


async def test_missing_slider_maps_to_not_found(db) -> None:
    repos = new_repositories(db)
    with pytest.raises(AppError) as excinfo:
        await repos.command.trash(2_000_000_000)
    assert excinfo.value.code == 404
    assert excinfo.value.message == "slider not found"


async def test_update_missing_slider_maps_to_not_found(db) -> None:
    repos = new_repositories(db)
    with pytest.raises(AppError) as excinfo:
        await repos.command.update(
            UpdateSliderRequest(slider_id=2_000_000_000, name="x", image="/a.png")
        )
    assert excinfo.value.code == 404


__all__ = []

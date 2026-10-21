"""Role repository integration tests against a real PostgreSQL.

Marked `integration` (excluded from `make test`). Every test uses a unique
`TEST_<PREFIX>_...` role name and removes only its own rows.
"""

from __future__ import annotations

import uuid

import pytest

from pkg.database.database import Database
from service.role.repository import new_repositories
from shared.errors import AppError

pytestmark = pytest.mark.integration


def _name(prefix: str) -> str:
    return f"TEST_{prefix}_{uuid.uuid4().hex[:10]}"


async def _cleanup(db: Database, prefix: str) -> None:
    await db.execute("DELETE FROM roles WHERE role_name LIKE :pattern", {"pattern": f"TEST_{prefix}%"})


async def test_create_find_by_id_and_name(db: Database) -> None:
    repos = new_repositories(db)
    name = _name("CREATE")
    try:
        created = await repos.command.create(name)
        assert created.role_id > 0
        assert created.deleted_at is None

        found = await repos.query.find_by_id(created.role_id)
        assert found.role_name == name

        by_name = await repos.query.find_by_name(name)
        assert by_name.role_id == created.role_id
    finally:
        await _cleanup(db, "CREATE")


async def test_duplicate_name_maps_to_conflict(db: Database) -> None:
    repos = new_repositories(db)
    name = _name("DUP")
    try:
        await repos.command.create(name)
        with pytest.raises(AppError) as excinfo:
            await repos.command.create(name)
        assert excinfo.value.code == 409
        assert excinfo.value.message == "Role already exists"
    finally:
        await _cleanup(db, "DUP")


async def test_missing_role_maps_to_not_found(db: Database) -> None:
    repos = new_repositories(db)
    with pytest.raises(AppError) as excinfo:
        await repos.query.find_by_id(2_000_000_000)
    assert excinfo.value.code == 404


async def test_soft_delete_lifecycle(db: Database) -> None:
    repos = new_repositories(db)
    name = _name("SOFT")
    try:
        created = await repos.command.create(name)

        trashed = await repos.command.trash(created.role_id)
        assert trashed.deleted_at is not None

        assert (await repos.query.find_by_id(created.role_id)).deleted_at is not None

        active = await repos.query.find_active(name, 1, 10)
        assert all(row.role_id != created.role_id for row in active)

        trashed_rows = await repos.query.find_trashed(name, 1, 10)
        assert any(row.role_id == created.role_id for row in trashed_rows)

        restored = await repos.command.restore(created.role_id)
        assert restored.deleted_at is None

        active_after = await repos.query.find_active(name, 1, 10)
        assert any(row.role_id == created.role_id for row in active_after)
    finally:
        await _cleanup(db, "SOFT")


async def test_pagination_reports_total_count(db: Database) -> None:
    repos = new_repositories(db)
    names = [_name("PAGE") for _ in range(3)]
    try:
        for name in names:
            await repos.command.create(name)
        rows = await repos.query.find_all("TEST_PAGE", 1, 2)
        assert len(rows) == 2
        assert rows[0].total_count >= 3
    finally:
        await _cleanup(db, "PAGE")


async def test_update_then_delete_permanent(db: Database) -> None:
    repos = new_repositories(db)
    name = _name("UPD")
    try:
        created = await repos.command.create(name)
        updated = await repos.command.update(created.role_id, f"{name}_X")
        assert updated.role_name == f"{name}_X"

        await repos.command.trash(created.role_id)
        await repos.command.delete_permanent(created.role_id)

        with pytest.raises(AppError):
            await repos.query.find_by_id(created.role_id)
    finally:
        await _cleanup(db, "UPD")


async def test_update_missing_role_maps_to_not_found(db: Database) -> None:
    repos = new_repositories(db)
    with pytest.raises(AppError) as excinfo:
        await repos.command.update(2_000_000_000, "X")
    assert excinfo.value.code == 404


async def test_find_by_user_id_join(db: Database) -> None:
    repos = new_repositories(db)
    name = _name("USER")
    email = f"test_{uuid.uuid4().hex[:10]}@example.com"
    role = await repos.command.create(name)
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
    try:
        await db.execute(
            "INSERT INTO user_roles (user_id, role_id) VALUES (:user_id, :role_id)",
            {"user_id": user_id, "role_id": role.role_id},
        )
        roles = await repos.query.find_by_user_id(user_id)
        assert any(row.role_id == role.role_id for row in roles)
    finally:
        await db.execute("DELETE FROM user_roles WHERE user_id = :user_id", {"user_id": user_id})
        await db.execute("DELETE FROM users WHERE user_id = :user_id", {"user_id": user_id})
        await _cleanup(db, "USER")

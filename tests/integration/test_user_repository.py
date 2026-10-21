"""User repository integration tests against a real PostgreSQL.

Marked `integration` (excluded from `make test`). Every test uses a unique
email and removes only its own rows (plus the outbox events they queued).
"""

from __future__ import annotations

import uuid

import pytest

from pkg.database.database import Database
from service.user.repository import new_repositories
from shared.errors import AppError

pytestmark = pytest.mark.integration

EMAIL_PREFIX = "usr_"


def _email() -> str:
    return f"{EMAIL_PREFIX}{uuid.uuid4().hex[:12]}@test.example"


async def _cleanup(db: Database) -> None:
    pattern = f"{EMAIL_PREFIX}%"
    await db.execute(
        "DELETE FROM outbox_events WHERE payload->>'email' LIKE :pattern",
        {"pattern": pattern},
    )
    await db.execute("DELETE FROM users WHERE email LIKE :pattern", {"pattern": pattern})


async def test_create_find_by_id_and_email(db: Database) -> None:
    repos = new_repositories(db)
    email = _email()
    try:
        created = await repos.command.create("John", "Doe", email, "hashed")
        assert created.user_id > 0
        assert created.email == email

        found = await repos.query.find_by_id(created.user_id)
        assert found.email == email

        by_email = await repos.query.find_by_email(email)
        assert by_email.user_id == created.user_id
    finally:
        await _cleanup(db)


async def test_create_queues_auth_register_outbox_event(db: Database) -> None:
    repos = new_repositories(db)
    email = _email()
    try:
        created = await repos.command.create("John", "Doe", email, "hashed")
        rows = await db.select(
            "SELECT topic, message_key FROM outbox_events WHERE event_key = :key",
            {"key": f"auth-register:{created.user_id}"},
        )
        assert len(rows) == 1
        assert rows[0]["topic"] == "email-service-topic-auth-register"
        assert rows[0]["message_key"] == str(created.user_id)
    finally:
        await _cleanup(db)


async def test_duplicate_email_maps_to_conflict(db: Database) -> None:
    repos = new_repositories(db)
    email = _email()
    try:
        await repos.command.create("John", "Doe", email, "hashed")
        with pytest.raises(AppError) as excinfo:
            await repos.command.create("Jane", "Roe", email, "hashed")
        assert excinfo.value.code == 409
        assert excinfo.value.message == "User already exists"
    finally:
        await _cleanup(db)


async def test_missing_user_maps_to_not_found(db: Database) -> None:
    repos = new_repositories(db)
    with pytest.raises(AppError) as excinfo:
        await repos.query.find_by_id(2_000_000_000)
    assert excinfo.value.code == 404


async def test_soft_delete_lifecycle(db: Database) -> None:
    repos = new_repositories(db)
    email = _email()
    try:
        created = await repos.command.create("John", "Doe", email, "hashed")

        trashed = await repos.command.trash(created.user_id)
        assert trashed.deleted_at is not None

        active = await repos.query.find_active(email, 1, 10)
        assert all(row.user_id != created.user_id for row in active)

        trashed_rows = await repos.query.find_trashed(email, 1, 10)
        assert any(row.user_id == created.user_id for row in trashed_rows)

        restored = await repos.command.restore(created.user_id)
        assert restored.deleted_at is None

        active_after = await repos.query.find_active(email, 1, 10)
        assert any(row.user_id == created.user_id for row in active_after)
    finally:
        await _cleanup(db)


async def test_pagination_reports_total_count(db: Database) -> None:
    repos = new_repositories(db)
    marker = uuid.uuid4().hex[:10]
    emails = [f"{EMAIL_PREFIX}{marker}{i}@test.example" for i in range(3)]
    try:
        for email in emails:
            await repos.command.create("John", "Doe", email, "hashed")
        rows = await repos.query.find_all(marker, 1, 2)
        assert len(rows) == 2
        assert rows[0].total_count >= 3
    finally:
        for email in emails:
            await db.execute(
                "DELETE FROM outbox_events WHERE payload->>'email' = :email",
                {"email": email},
            )
        await db.execute(
            "DELETE FROM users WHERE email LIKE :pattern", {"pattern": f"{EMAIL_PREFIX}{marker}%"}
        )


async def test_update_then_delete_permanent(db: Database) -> None:
    repos = new_repositories(db)
    email = _email()
    try:
        created = await repos.command.create("John", "Doe", email, "hashed")
        updated = await repos.command.update(
            created.user_id, "Johnny", "Doe", email, "hashed2"
        )
        assert updated.firstname == "Johnny"
        assert updated.password == "hashed2"

        await repos.command.trash(created.user_id)
        await repos.command.delete_permanent(created.user_id)

        with pytest.raises(AppError):
            await repos.query.find_by_id(created.user_id)
    finally:
        await _cleanup(db)


async def test_update_missing_user_maps_to_not_found(db: Database) -> None:
    repos = new_repositories(db)
    with pytest.raises(AppError) as excinfo:
        await repos.command.update(2_000_000_000, "John", "Doe", "x@y.example", "hashed")
    assert excinfo.value.code == 404

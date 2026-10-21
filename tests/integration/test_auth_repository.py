"""Auth repository integration tests against a real PostgreSQL. Marked `integration` (excluded from `make test`). Every test uses the `auth_` email prefix and removes only its own rows (plus the outbox events they queued); related reset/refresh/user-role rows cascade with the user."""

from __future__ import annotations

import uuid
from collections.abc import AsyncIterator
from datetime import datetime, timedelta
from typing import Any

import grpc
import grpc.aio as grpc_aio
import pytest

from pkg.adapter.guard import default_guard
from pkg.database.database import Database
from pkg.logger.logger import get_logger
from service.auth.repository import GuardOptions, new_repositories
from shared.domain.requests.auth import (
    CreateRefreshToken,
    CreateResetTokenRequest,
    CreateUserRoleRequest,
    RegisterRequest,
    RemoveUserRoleRequest,
    UpdateRefreshToken,
)
from shared.errors import AppError


@pytest.fixture(name="make_repos")
async def make_repos(role_grpc_server: str) -> AsyncIterator[Any]:
    """Channels for the guarded cross-domain adapters (see conftest for the ephemeral downstream servers)."""
    logger = get_logger("test-repos")
    channel = grpc_aio.insecure_channel(
        role_grpc_server,
    )
    guards = GuardOptions(
        role=default_guard('role', logger), user_role=default_guard('user_role', logger),
    )

    def _make(db: Database):
        return new_repositories(db, role_channel=channel, guards=guards)

    yield _make
    await channel.close()

pytestmark = pytest.mark.integration

EMAIL_PREFIX = "auth_"
_GO_LAYOUT = "%Y-%m-%d %H:%M:%S"


def _email() -> str:
    return f"{EMAIL_PREFIX}{uuid.uuid4().hex[:12]}@test.example"


def _code() -> str:
    return f"code-{uuid.uuid4().hex[:10]}"


def _register(email: str, code: str) -> RegisterRequest:
    return RegisterRequest(
        firstname="John",
        lastname="Doe",
        email=email,
        password="hashed-secret",
        confirm_password="hashed-secret",
        verified_code=code,
        is_verified=False,
    )


async def _cleanup(db: Database) -> None:
    pattern = f"{EMAIL_PREFIX}%"
    await db.execute(
        "DELETE FROM outbox_events WHERE payload->>'email' LIKE :pattern",
        {"pattern": pattern},
    )
    await db.execute("DELETE FROM users WHERE email LIKE :pattern", {"pattern": pattern})


# ---- user repository ----


async def test_create_user_queues_auth_register_event(db: Database, make_repos) -> None:
    repos = make_repos(db)
    email = _email()
    code = _code()
    try:
        created = await repos.user.create_user(_register(email, code))

        assert created.user_id > 0
        assert created.email == email
        assert created.password == "hashed-secret"

        rows = await db.select(
            "SELECT topic, message_key, payload FROM outbox_events WHERE event_key = :key",
            {"key": f"auth-register:{created.user_id}"},
        )
        assert len(rows) == 1
        assert rows[0]["topic"] == "email-service-topic-auth-register"
        assert rows[0]["message_key"] == str(created.user_id)
        assert rows[0]["payload"]["event_type"] == "auth.register"
        assert rows[0]["payload"]["email"] == email
        assert code in rows[0]["payload"]["body"]
    finally:
        await _cleanup(db)


async def test_lookups_and_missing_rows(db: Database, make_repos) -> None:
    repos = make_repos(db)
    email = _email()
    code = _code()
    try:
        created = await repos.user.create_user(_register(email, code))

        by_email = await repos.user.find_by_email(email)
        assert by_email.user_id == created.user_id

        # Not verified yet, so the login lookup must miss.
        with pytest.raises(AppError) as unverified:
            await repos.user.find_by_email_and_verify(email)
        assert unverified.value.code == 404

        found = await repos.user.find_by_verification_code(code)
        assert found is not None
        assert found.user_id == created.user_id

        # A miss returns None (returns nil, nil) rather than raising.
        assert await repos.user.find_by_verification_code("no-such-code") is None

        with pytest.raises(AppError) as missing:
            await repos.user.find_by_email("nobody@test.example")
        assert missing.value.code == 404
    finally:
        await _cleanup(db)


async def test_find_by_id_rejects_non_positive_and_missing(db: Database, make_repos) -> None:
    repos = make_repos(db)

    with pytest.raises(AppError) as invalid:
        await repos.user.find_by_id(0)
    assert invalid.value.code == 400
    assert invalid.value.message == "user ID must be greater than zero"

    with pytest.raises(AppError) as missing:
        await repos.user.find_by_id(2_000_000_000)
    assert missing.value.code == 404


async def test_update_user_is_verified_queues_event_only_when_true(
    db: Database, make_repos,
) -> None:
    repos = make_repos(db)
    email = _email()
    try:
        created = await repos.user.create_user(_register(email, _code()))

        unverified = await repos.user.update_user_is_verified(created.user_id, False)
        assert unverified.user_id == created.user_id
        events = await db.select(
            "SELECT event_key FROM outbox_events WHERE event_key = :key",
            {"key": f"auth-verify:{created.user_id}"},
        )
        assert events == []

        verified = await repos.user.update_user_is_verified(created.user_id, True)
        assert verified.email == email
        events = await db.select(
            "SELECT topic, payload FROM outbox_events WHERE event_key = :key",
            {"key": f"auth-verify:{created.user_id}"},
        )
        assert len(events) == 1
        assert events[0]["topic"] == "email-service-topic-auth-verify-code-success"
        assert events[0]["payload"]["event_type"] == "auth.verify_code_success"

        # The login lookup now succeeds.
        login_row = await repos.user.find_by_email_and_verify(email)
        assert login_row.user_id == created.user_id
    finally:
        await _cleanup(db)


async def test_update_user_password_persists_the_new_hash(db: Database, make_repos) -> None:
    repos = make_repos(db)
    email = _email()
    try:
        created = await repos.user.create_user(_register(email, _code()))

        updated = await repos.user.update_user_password(created.user_id, "new-hash")

        assert updated.password == "new-hash"
        stored = await db.scalar(
            "SELECT password FROM users WHERE user_id = :id",
            {"id": created.user_id},
        )
        assert stored["password"] == "new-hash"
    finally:
        await _cleanup(db)


async def test_role_lookup_and_user_role_assignment(db: Database, make_repos, admin_role: int) -> None:
    repos = make_repos(db)
    email = _email()
    try:
        role = await repos.role.find_by_name("ROLE_ADMIN")
        assert role.role_id == admin_role

        created = await repos.user.create_user(_register(email, _code()))
        assigned = await repos.user_role.assign_role_to_user(
            CreateUserRoleRequest(user_id=created.user_id, role_id=role.role_id)
        )
        assert assigned.user_id == created.user_id
        assert assigned.role_id == role.role_id

        rows = await db.select(
            "SELECT user_id, role_id FROM user_roles WHERE user_id = :id",
            {"id": created.user_id},
        )
        assert len(rows) == 1
        assert rows[0]["user_id"] == created.user_id
        assert rows[0]["role_id"] == admin_role

        # so the guarded adapter surfaces UNIMPLEMENTED and the user_roles row
        # stays in place (the adapter method exists for contract).
        with pytest.raises(AppError) as exc:
            await repos.user_role.remove_role_from_user(
                RemoveUserRoleRequest(user_id=created.user_id, role_id=role.role_id)
            )
        internal = exc.value.internal
        assert isinstance(internal, grpc_aio.AioRpcError)
        assert internal.code() == grpc.StatusCode.UNIMPLEMENTED

        rows = await db.select(
            "SELECT user_id FROM user_roles WHERE user_id = :id",
            {"id": created.user_id},
        )
        assert len(rows) == 1
    finally:
        await _cleanup(db)


# ---- reset-token repository ----


async def test_create_reset_token_queues_forgot_password_event(db: Database, make_repos) -> None:
    repos = make_repos(db)
    email = _email()
    try:
        created = await repos.user.create_user(_register(email, _code()))
        expired_at = (datetime.now() + timedelta(hours=24)).strftime(_GO_LAYOUT)

        row = await repos.reset_token.create_reset_token(
            CreateResetTokenRequest(
                user_id=created.user_id,
                reset_token="reset-token-abc",
                expired_at=expired_at,
            )
        )
        assert row.user_id == created.user_id
        assert row.token == "reset-token-abc"

        found = await repos.reset_token.find_by_token("reset-token-abc")
        assert found.user_id == created.user_id

        events = await db.select(
            "SELECT topic, payload FROM outbox_events WHERE event_key = :key",
            {"key": f"auth-forgot-password:{created.user_id}:reset-token-abc"},
        )
        assert len(events) == 1
        assert events[0]["topic"] == "email-service-topic-auth-forgot-password"
        assert events[0]["payload"]["email"] == email
        assert "reset-token-abc" in events[0]["payload"]["body"]

        await repos.reset_token.delete_reset_token(created.user_id)
        with pytest.raises(AppError) as gone:
            await repos.reset_token.find_by_token("reset-token-abc")
        assert gone.value.code == 404
    finally:
        await _cleanup(db)


async def test_create_reset_token_rejects_bad_expiry(db: Database, make_repos) -> None:
    repos = make_repos(db)
    email = _email()
    try:
        created = await repos.user.create_user(_register(email, _code()))
        with pytest.raises(AppError) as excinfo:
            await repos.reset_token.create_reset_token(
                CreateResetTokenRequest(
                    user_id=created.user_id,
                    reset_token="reset-token-bad",
                    expired_at="2026-08-19T10:00:00Z",  # RFC3339, not the layout
                )
            )
        assert excinfo.value.code == 500
    finally:
        await _cleanup(db)


# ---- refresh-token repository ----


async def test_refresh_token_lifecycle(db: Database, make_repos) -> None:
    repos = make_repos(db)
    email = _email()
    try:
        created = await repos.user.create_user(_register(email, _code()))
        expires = (datetime.now() + timedelta(hours=24)).strftime(_GO_LAYOUT)

        token = f"refresh-{uuid.uuid4().hex}"
        row = await repos.refresh_token.create_refresh_token(
            CreateRefreshToken(
                user_id=created.user_id, token=token, expires_at=expires
            )
        )
        assert row.token == token
        assert row.deleted_at is None

        assert (await repos.refresh_token.find_by_token(token)).user_id == created.user_id
        assert (
            await repos.refresh_token.find_by_user_id(created.user_id)
        ).refresh_token_id == row.refresh_token_id

        rotated = f"refresh-{uuid.uuid4().hex}"
        updated = await repos.refresh_token.update_refresh_token(
            UpdateRefreshToken(
                user_id=created.user_id, token=rotated, expires_at=expires
            )
        )
        assert updated.token == rotated

        await repos.refresh_token.delete_refresh_token(rotated)
        with pytest.raises(AppError) as gone:
            await repos.refresh_token.find_by_token(rotated)
        assert gone.value.code == 404
    finally:
        await _cleanup(db)


async def test_refresh_token_delete_by_user_id(db: Database, make_repos) -> None:
    repos = make_repos(db)
    email = _email()
    try:
        created = await repos.user.create_user(_register(email, _code()))
        expires = (datetime.now() + timedelta(hours=24)).strftime(_GO_LAYOUT)
        token = f"refresh-{uuid.uuid4().hex}"
        await repos.refresh_token.create_refresh_token(
            CreateRefreshToken(
                user_id=created.user_id, token=token, expires_at=expires
            )
        )

        await repos.refresh_token.delete_refresh_token_by_user_id(created.user_id)

        with pytest.raises(AppError) as gone:
            await repos.refresh_token.find_by_user_id(created.user_id)
        assert gone.value.code == 404
    finally:
        await _cleanup(db)


async def test_refresh_token_rejects_bad_expiry(db: Database, make_repos) -> None:
    repos = make_repos(db)
    email = _email()
    try:
        created = await repos.user.create_user(_register(email, _code()))
        with pytest.raises(AppError) as excinfo:
            await repos.refresh_token.create_refresh_token(
                CreateRefreshToken(
                    user_id=created.user_id,
                    token=f"refresh-{uuid.uuid4().hex}",
                    expires_at="2026-08-19T10:00:00Z",
                )
            )
        assert excinfo.value.code == 500
    finally:
        await _cleanup(db)

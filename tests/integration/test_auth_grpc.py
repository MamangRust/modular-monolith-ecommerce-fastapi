"""Auth gRPC integration tests: real grpc.aio server, generated client. Marked `integration`. Exercises the full identity lifecycle over the wire — register, verify, login, get-me, refresh rotation, forgot/reset password — and asserts the `ErrorResponse` detail survives each hop (401/403/404/409), the timestamp shape, and that the outbox events are queued by the real SQL."""

from __future__ import annotations

import asyncio
import uuid

import grpc
import pytest

from pb.auth import auth_pb2, auth_pb2_grpc
from pkg.auth import TokenManager
from pkg.database.database import Database
from shared.cache import CacheStore
from shared.errors import parse_grpc_error

pytestmark = pytest.mark.integration

EMAIL_PREFIX = "authgrpc_"


def _email() -> str:
    return f"{EMAIL_PREFIX}{uuid.uuid4().hex[:12]}@test.example"


async def _cleanup(db: Database, store: CacheStore, email: str) -> None:
    pattern = f"{EMAIL_PREFIX}%"
    await db.execute(
        "DELETE FROM outbox_events WHERE payload->>'email' LIKE :pattern",
        {"pattern": pattern},
    )
    await db.execute("DELETE FROM users WHERE email LIKE :pattern", {"pattern": pattern})
    await store.redis.delete(
        store.key(f"auth:login:failed:{email}"),
        store.key(f"auth:login:locked:{email}"),
        store.key(f"register:verify_code:{email}"),
    )


async def _register(stub, email: str) -> auth_pb2.ApiResponseRegister:
    return await stub.RegisterUser(
        auth_pb2.RegisterRequest(
            firstname="John",
            lastname="Doe",
            email=email,
            password="secret1",
            confirm_password="secret1",
        ),
        timeout=5,
    )


async def _verify(stub, db: Database, email: str) -> str:
    row = await db.scalar(
        "SELECT verification_code FROM users WHERE email = :email", {"email": email}
    )
    code = row["verification_code"]
    await stub.VerifyCode(auth_pb2.VerifyCodeRequest(code=code), timeout=5)
    return code


async def test_auth_grpc_full_lifecycle(
    db: Database,
    cache_store: CacheStore,
    auth_grpc_server: str,
    token_manager: TokenManager,
) -> None:
    channel = grpc.aio.insecure_channel(auth_grpc_server)
    stub = auth_pb2_grpc.AuthServiceStub(channel)
    email = _email()

    try:
        registered = await _register(stub, email)
        assert registered.status == "success"
        assert registered.message == "RegisterUser successful"
        assert registered.data.email == email
        user_id = registered.data.id
        # Auth timestamps use shape.
        assert registered.data.created_at.endswith(" +0000 UTC")

        stored = await db.scalar(
            "SELECT password, is_verified FROM users WHERE user_id = :id",
            {"id": user_id},
        )
        assert stored["password"].startswith("$2")
        assert stored["password"] != "secret1"
        assert stored["is_verified"] is False

        # Unverified accounts cannot log in.
        with pytest.raises(grpc.aio.AioRpcError) as unverified:
            await stub.LoginUser(
                auth_pb2.LoginRequest(email=email, password="secret1"), timeout=5
            )
        assert unverified.value.code() is grpc.StatusCode.NOT_FOUND

        await _verify(stub, db, email)

        events = await db.select(
            "SELECT topic FROM outbox_events WHERE event_key = :key",
            {"key": f"auth-verify:{user_id}"},
        )
        assert [row["topic"] for row in events] == [
            "email-service-topic-auth-verify-code-success"
        ]

        login = await stub.LoginUser(
            auth_pb2.LoginRequest(email=email, password="secret1"), timeout=5
        )
        assert login.status == "success"
        assert token_manager.validate_token(login.data.access_token) == str(user_id)
        assert token_manager.validate_token(login.data.refresh_token) == str(user_id)

        me = await stub.GetMe(auth_pb2.GetMeRequest(userId=user_id), timeout=5)
        assert me.data.id == user_id
        assert me.data.email == email
        assert me.data.created_at.endswith(" +0000 UTC")

        # JWTs carry second-granularity `iat`, so wait out the current second
        # to guarantee the rotated token differs from the one presented.
        await asyncio.sleep(1.05)

        refreshed = await stub.RefreshToken(
            auth_pb2.RefreshTokenRequest(refresh_token=login.data.refresh_token),
            timeout=5,
        )
        assert refreshed.status == "success"
        # Deviation: the handler returns the newly issued token, not the
        # presented (already deleted) one.
        assert refreshed.data.refresh_token != login.data.refresh_token
        assert token_manager.validate_token(refreshed.data.refresh_token) == str(user_id)

        old_row = await db.scalar(
            "SELECT count(*) AS c FROM refresh_tokens WHERE token = :token",
            {"token": login.data.refresh_token},
        )
        assert old_row["c"] == 0

        forgot = await stub.ForgotPassword(
            auth_pb2.ForgotPasswordRequest(email=email), timeout=5
        )
        assert forgot.message == "ForgotPassword successful"

        token_row = await db.scalar(
            "SELECT token FROM reset_tokens WHERE user_id = :id", {"id": user_id}
        )
        assert token_row is not None

        reset = await stub.ResetPassword(
            auth_pb2.ResetPasswordRequest(
                reset_token=token_row["token"],
                password="secret2",
                confirm_password="secret2",
            ),
            timeout=5,
        )
        assert reset.message == "Reset password successful"

        # Deviation fix: the new password is hashed, so login succeeds.
        relogin = await stub.LoginUser(
            auth_pb2.LoginRequest(email=email, password="secret2"), timeout=5
        )
        assert relogin.status == "success"

        # The reset token was consumed.
        with pytest.raises(grpc.aio.AioRpcError) as consumed:
            await stub.ResetPassword(
                auth_pb2.ResetPasswordRequest(
                    reset_token=token_row["token"],
                    password="secret3",
                    confirm_password="secret3",
                ),
                timeout=5,
            )
        assert consumed.value.code() is grpc.StatusCode.NOT_FOUND
    finally:
        await channel.close()
        await _cleanup(db, cache_store, email)


async def test_duplicate_register_is_already_exists(
    db: Database, cache_store: CacheStore, auth_grpc_server: str
) -> None:
    channel = grpc.aio.insecure_channel(auth_grpc_server)
    stub = auth_pb2_grpc.AuthServiceStub(channel)
    email = _email()
    try:
        await _register(stub, email)
        with pytest.raises(grpc.aio.AioRpcError) as conflict:
            await _register(stub, email)
        assert conflict.value.code() is grpc.StatusCode.ALREADY_EXISTS
        assert parse_grpc_error(conflict.value).code == 409
    finally:
        await channel.close()
        await _cleanup(db, cache_store, email)


async def test_verify_code_unknown_maps_to_not_found(
    db: Database, cache_store: CacheStore, auth_grpc_server: str
) -> None:
    channel = grpc.aio.insecure_channel(auth_grpc_server)
    stub = auth_pb2_grpc.AuthServiceStub(channel)
    try:
        with pytest.raises(grpc.aio.AioRpcError) as missing:
            await stub.VerifyCode(
                auth_pb2.VerifyCodeRequest(code="definitely-not-a-code"), timeout=5
            )
        assert missing.value.code() is grpc.StatusCode.NOT_FOUND
        assert parse_grpc_error(missing.value).code == 404
    finally:
        await channel.close()


async def test_wrong_password_then_lockout(
    db: Database, cache_store: CacheStore, auth_grpc_server: str
) -> None:
    channel = grpc.aio.insecure_channel(auth_grpc_server)
    stub = auth_pb2_grpc.AuthServiceStub(channel)
    email = _email()
    try:
        await _register(stub, email)
        await _verify(stub, db, email)

        for _ in range(5):
            with pytest.raises(grpc.aio.AioRpcError) as wrong:
                await stub.LoginUser(
                    auth_pb2.LoginRequest(email=email, password="wrongpass"), timeout=5
                )
            assert wrong.value.code() is grpc.StatusCode.UNAUTHENTICATED
            assert parse_grpc_error(wrong.value).code == 401

        # The sixth attempt is rejected before the password is even compared.
        with pytest.raises(grpc.aio.AioRpcError) as locked:
            await stub.LoginUser(
                auth_pb2.LoginRequest(email=email, password="secret1"), timeout=5
            )
        assert locked.value.code() is grpc.StatusCode.PERMISSION_DENIED
        parsed = parse_grpc_error(locked.value)
        assert parsed.code == 403
        assert parsed.message == "Account temporarily locked due to many failed attempts"
    finally:
        await channel.close()
        await _cleanup(db, cache_store, email)

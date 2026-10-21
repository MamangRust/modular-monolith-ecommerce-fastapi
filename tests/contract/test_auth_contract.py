"""Gateway contract tests: FastAPI REST -> real auth gRPC over HTTPX. Marked `integration` because it needs PostgreSQL + Redis (the auth service is real, not mocked). The app wires the JWT middleware so `/api/auth/me` behaves in production: the middleware validates the bearer token and stores the subject on `request.state.user_id`, which the route forwards to the auth service."""

from __future__ import annotations

import asyncio
import uuid

import grpc
import httpx
import pytest
from fastapi import FastAPI

from pb.auth import auth_pb2, auth_pb2_grpc
from pkg.auth import TokenManager
from pkg.database.database import Database
from pkg.logger.logger import get_logger
from service.apigateway.app.client import ServiceConnections
from service.apigateway.handler import register_routers
from service.apigateway.middlewares.auth import JwtAuthMiddleware
from shared.cache import CacheStore
from shared.errorhandler import register_exception_handlers

pytestmark = pytest.mark.integration

EMAIL_PREFIX = "authcontract_"


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
        store.key(f"auth:login:{email}"),
    )


def _app(
    auth_grpc_server: str,
    channel: grpc.aio.Channel,
    cache_store: CacheStore,
    token_manager: TokenManager,
) -> FastAPI:
    app = FastAPI()
    app.state.logger = get_logger("test-contract")
    app.state.connections = ServiceConnections(
        channels={"auth": channel}, addresses={"auth": auth_grpc_server}
    )
    app.state.cache_store = cache_store
    app.state.token_manager = token_manager
    register_exception_handlers(app)
    app.add_middleware(JwtAuthMiddleware)
    register_routers(app)
    return app


async def test_auth_rest_contract(
    db: Database,
    cache_store: CacheStore,
    auth_grpc_server: str,
    token_manager: TokenManager,
) -> None:
    channel = grpc.aio.insecure_channel(auth_grpc_server)
    app = _app(auth_grpc_server, channel, cache_store, token_manager)
    email = _email()
    transport = httpx.ASGITransport(app=app)

    try:
        async with httpx.AsyncClient(transport=transport, base_url="http://test") as client:
            hello = await client.get("/api/auth/hello")
            assert hello.status_code == 200
            assert hello.text == "Hello"
            assert hello.headers["content-type"].startswith("text/plain")

            registered = await client.post(
                "/api/auth/register",
                json={
                    "firstname": "John",
                    "lastname": "Doe",
                    "email": email,
                    "password": "secret1",
                    "confirm_password": "secret1",
                },
            )
            assert registered.status_code == 201
            body = registered.json()
            assert body["status"] == "success"
            assert body["data"]["email"] == email
            assert body["data"]["created_at"].endswith(" +0000 UTC")
            user_id = body["data"]["id"]

            duplicate = await client.post(
                "/api/auth/register",
                json={
                    "firstname": "John",
                    "lastname": "Doe",
                    "email": email,
                    "password": "secret1",
                    "confirm_password": "secret1",
                },
            )
            assert duplicate.status_code == 409

            invalid_body = await client.post(
                "/api/auth/register",
                json={
                    "firstname": "John",
                    "lastname": "Doe",
                    "email": "not-an-email",
                    "password": "secret1",
                    "confirm_password": "secret1",
                },
            )
            assert invalid_body.status_code == 400
            assert invalid_body.json()["message"] == "Validation failed"

            # Unverified accounts cannot log in (404 from the domain).
            unverified = await client.post(
                "/api/auth/login", json={"email": email, "password": "secret1"}
            )
            assert unverified.status_code == 404

            code_row = await db.scalar(
                "SELECT verification_code FROM users WHERE user_id = :id",
                {"id": user_id},
            )
            verified = await client.post(
                "/api/auth/verify-code", json={"code": code_row["verification_code"]}
            )
            assert verified.status_code == 200
            assert verified.json()["message"] == "Verification successfully"

            unknown_code = await client.post(
                "/api/auth/verify-code", json={"code": "definitely-not-a-code"}
            )
            assert unknown_code.status_code == 404

            logged_in = await client.post(
                "/api/auth/login", json={"email": email, "password": "secret1"}
            )
            assert logged_in.status_code == 200
            login_body = logged_in.json()
            assert login_body["message"] == "LoginUser successfull"
            access_token = login_body["data"]["access_token"]
            refresh_token = login_body["data"]["refresh_token"]
            assert token_manager.validate_token(access_token) == str(user_id)

            # /me is protected: no bearer token -> 401 from the middleware.
            unauthorized = await client.get("/api/auth/me")
            assert unauthorized.status_code == 401

            me = await client.get(
                "/api/auth/me", headers={"Authorization": f"Bearer {access_token}"}
            )
            assert me.status_code == 200
            assert me.json()["data"]["id"] == user_id
            assert me.json()["data"]["email"] == email

            # Second call is served from the gateway cache (same payload).
            me_again = await client.get(
                "/api/auth/me", headers={"Authorization": f"Bearer {access_token}"}
            )
            assert me_again.status_code == 200
            assert me_again.json() == me.json()

            # JWTs carry second-granularity `iat`; wait out the second so the
            # rotated token is provably different.
            await asyncio.sleep(1.05)

            refreshed = await client.post(
                "/api/auth/refresh-token", json={"refresh_token": refresh_token}
            )
            assert refreshed.status_code == 200
            refreshed_body = refreshed.json()
            assert refreshed_body["data"]["refresh_token"] != refresh_token
            assert (
                token_manager.validate_token(refreshed_body["data"]["access_token"])
                == str(user_id)
            )

            forgot = await client.post(
                "/api/auth/forgot-password", json={"email": email}
            )
            assert forgot.status_code == 200
            assert forgot.json()["message"] == "ForgotPassword successful"

            token_row = await db.scalar(
                "SELECT token FROM reset_tokens WHERE user_id = :id", {"id": user_id}
            )
            assert token_row is not None

            mismatch = await client.post(
                "/api/auth/reset-password",
                json={
                    "reset_token": token_row["token"],
                    "password": "secret2",
                    "confirm_password": "different2",
                },
            )
            assert mismatch.status_code == 400
            assert (
                mismatch.json()["message"]
                == "password and confirm password do not match"
            )

            reset = await client.post(
                "/api/auth/reset-password",
                json={
                    "reset_token": token_row["token"],
                    "password": "secret2",
                    "confirm_password": "secret2",
                },
            )
            assert reset.status_code == 200
            assert reset.json()["message"] == "Reset password successful"

            relogin = await client.post(
                "/api/auth/login", json={"email": email, "password": "secret2"}
            )
            assert relogin.status_code == 200
    finally:
        await channel.close()
        await _cleanup(db, cache_store, email)


async def test_login_lockout_surfaces_as_403(
    db: Database,
    cache_store: CacheStore,
    auth_grpc_server: str,
    token_manager: TokenManager,
) -> None:
    channel = grpc.aio.insecure_channel(auth_grpc_server)
    stub = auth_pb2_grpc.AuthServiceStub(channel)
    app = _app(auth_grpc_server, channel, cache_store, token_manager)
    email = _email()
    transport = httpx.ASGITransport(app=app)

    try:
        async with httpx.AsyncClient(transport=transport, base_url="http://test") as client:
            await client.post(
                "/api/auth/register",
                json={
                    "firstname": "John",
                    "lastname": "Doe",
                    "email": email,
                    "password": "secret1",
                    "confirm_password": "secret1",
                },
            )
            row = await db.scalar(
                "SELECT verification_code FROM users WHERE email = :email",
                {"email": email},
            )
            await stub.VerifyCode(
                auth_pb2.VerifyCodeRequest(code=row["verification_code"]), timeout=5
            )

            for _ in range(5):
                wrong = await client.post(
                    "/api/auth/login", json={"email": email, "password": "wrongpass"}
                )
                assert wrong.status_code == 401
                assert wrong.json()["message"] == "Password does not match"

            locked = await client.post(
                "/api/auth/login", json={"email": email, "password": "secret1"}
            )
            assert locked.status_code == 403
            assert locked.json()["message"] == (
                "Account temporarily locked due to many failed attempts"
            )
    finally:
        await channel.close()
        await _cleanup(db, cache_store, email)

"""Gateway contract tests: FastAPI REST -> real user gRPC over HTTPX. Marked `integration` because it needs PostgreSQL + Redis (the user service is real, not mocked). The app registers every router, but only the user routes are exercised; the user routes carry no RBAC dependency (matching), so no dependency override is needed."""

from __future__ import annotations

import uuid

import grpc
import httpx
import pytest
from fastapi import FastAPI

from pkg.database.database import Database
from service.apigateway.app.client import ServiceConnections
from service.apigateway.handler import register_routers
from shared.errorhandler import register_exception_handlers

pytestmark = pytest.mark.integration

EMAIL_PREFIX = "usrcontract_"


def _email() -> str:
    return f"{EMAIL_PREFIX}{uuid.uuid4().hex[:12]}@test.example"


async def _cleanup(db: Database) -> None:
    pattern = f"{EMAIL_PREFIX}%"
    await db.execute(
        "DELETE FROM outbox_events WHERE payload->>'email' LIKE :pattern",
        {"pattern": pattern},
    )
    await db.execute("DELETE FROM users WHERE email LIKE :pattern", {"pattern": pattern})


def _app(user_grpc_server: str, channel: grpc.aio.Channel) -> FastAPI:
    app = FastAPI()
    app.state.connections = ServiceConnections(
        channels={"user": channel}, addresses={"user": user_grpc_server}
    )
    register_exception_handlers(app)
    register_routers(app)
    return app


async def test_user_rest_contract(db: Database, user_grpc_server: str) -> None:
    channel = grpc.aio.insecure_channel(user_grpc_server)
    app = _app(user_grpc_server, channel)
    email = _email()
    transport = httpx.ASGITransport(app=app)

    try:
        async with httpx.AsyncClient(transport=transport, base_url="http://test") as client:
            created = await client.post(
                "/api/user-command/create",
                json={
                    "firstname": "John",
                    "lastname": "Doe",
                    "email": email,
                    "password": "secret1",
                    "confirm_password": "secret1",
                },
            )
            assert created.status_code == 200
            body = created.json()
            assert body["status"] == "success"
            assert body["data"]["email"] == email
            assert body["data"]["is_verified"] is False
            user_id = body["data"]["id"]

            listed = await client.get("/api/user-query", params={"search": email})
            assert listed.status_code == 200
            listed_body = listed.json()
            assert listed_body["pagination"]["total_records"] >= 1
            assert listed_body["data"][0]["email"] == email

            by_id = await client.get(f"/api/user-query/{user_id}")
            assert by_id.status_code == 200
            assert by_id.json()["data"]["id"] == user_id

            # user gateway does not clamp path ids, so 0 reaches the
            # domain and comes back as its 400 "Invalid user ID".
            bad_id = await client.get("/api/user-query/0")
            assert bad_id.status_code == 400
            assert bad_id.json()["message"] == "Invalid user ID"

            missing = await client.get("/api/user-query/2000000000")
            assert missing.status_code == 404
            assert missing.json()["type"] == "NOT_FOUND"

            duplicate = await client.post(
                "/api/user-command/create",
                json={
                    "firstname": "John",
                    "lastname": "Doe",
                    "email": email,
                    "password": "secret1",
                    "confirm_password": "secret1",
                },
            )
            assert duplicate.status_code == 409
            assert duplicate.json()["code"] == 409

            invalid_body = await client.post(
                "/api/user-command/create",
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

            updated = await client.post(
                f"/api/user-command/update/{user_id}",
                json={
                    "firstname": "Johnny",
                    "lastname": "Doe",
                    "email": email,
                    "password": "secret2",
                    "confirm_password": "secret2",
                },
            )
            assert updated.status_code == 200
            assert updated.json()["data"]["firstname"] == "Johnny"

            stored = await db.scalar(
                "SELECT password FROM users WHERE user_id = :user_id",
                {"user_id": user_id},
            )
            assert stored is not None
            assert stored["password"].startswith("$2")

            trashed = await client.post(f"/api/user-command/trashed/{user_id}")
            assert trashed.status_code == 200
            assert trashed.json()["data"]["deleted_at"]

            restored = await client.post(f"/api/user-command/restore/{user_id}")
            assert restored.status_code == 200
            assert restored.json()["data"]["deleted_at"] is None

            deleted = await client.delete(f"/api/user-command/permanent/{user_id}")
            assert deleted.status_code == 200
            assert deleted.json()["data"] is None
    finally:
        await channel.close()
        await _cleanup(db)

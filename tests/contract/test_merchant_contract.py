"""Gateway contract tests: FastAPI REST -> real merchant gRPC over HTTPX.

Marked `integration` because it needs PostgreSQL + Redis (the merchant service
is real). Merchant `Create`/`Update` take the owner id from the JWT, so the test
app injects `request.state.user_id` via a tiny middleware (the real gateway uses
`JwtAuthMiddleware`); a missing subject yields 401.

Verifies: create returns 201; the REST `id` field; `%Y-%m-%d %H:%M:%S`
timestamps; static paths (`/active`, `/trashed`, `/restore/all`, `/permanent/all`)
winning over the `{merchant_id}` variants; the gateway 400 `Invalid ID` for
command ids; the forwarded 400 `invalid merchant ID` for `/api/merchant-query/0`;
and the 404 `NOT_FOUND` preservation for a missing merchant.
"""

from __future__ import annotations

import uuid

import grpc
import httpx
import pytest
from fastapi import FastAPI

from pkg.database.database import Database
from pkg.logger.logger import get_logger
from pkg.upload_image import new_image_upload
from service.apigateway.app.client import ServiceConnections
from service.apigateway.handler import register_routers
from shared.errorhandler import register_exception_handlers

pytestmark = pytest.mark.integration


def _app(server: str, channel: grpc.aio.Channel, user_id: int | None) -> FastAPI:
    app = FastAPI()
    app.state.connections = ServiceConnections(
        channels={"merchant": channel}, addresses={"merchant": server}
    )
    app.state.upload_image = new_image_upload(get_logger("test-merchant"))
    register_exception_handlers(app)
    register_routers(app)

    @app.middleware("http")
    async def _inject_user(request, call_next):
        request.state.user_id = user_id
        return await call_next(request)

    return app


async def _seed_user(db: Database) -> int:
    email = f"test_merchant_contract_{uuid.uuid4().hex[:10]}@example.com"
    row = await db.execute(
        """
        INSERT INTO users (firstname, lastname, email, password, verification_code)
        VALUES ('T', 'U', :email, 'x', 'v')
        RETURNING user_id
        """,
        {"email": email},
    )
    assert row is not None
    return int(row["user_id"])


async def _cleanup(db: Database, merchant_id: int | None, user_id: int) -> None:
    if merchant_id is not None:
        await db.execute(
            "DELETE FROM merchant_documents WHERE merchant_id = :merchant_id",
            {"merchant_id": merchant_id},
        )
        await db.execute(
            "DELETE FROM merchants WHERE merchant_id = :merchant_id",
            {"merchant_id": merchant_id},
        )
    await db.execute("DELETE FROM outbox_events WHERE event_key LIKE 'merchant-%'")
    await db.execute("DELETE FROM users WHERE user_id = :user_id", {"user_id": user_id})


def _body(name: str) -> dict[str, object]:
    return {
        "name": name,
        "description": "d",
        "address": "a",
        "contact_email": "e@f.com",
        "contact_phone": "0812",
        "status": "active",
    }


async def test_merchant_rest_contract(
    db: Database, merchant_grpc_server: str
) -> None:
    channel = grpc.aio.insecure_channel(merchant_grpc_server)
    user_id = await _seed_user(db)
    app = _app(merchant_grpc_server, channel, user_id)
    name = f"Merchant {uuid.uuid4().hex[:10]}"
    merchant_id: int | None = None
    transport = httpx.ASGITransport(app=app)

    try:
        async with httpx.AsyncClient(
            transport=transport, base_url="http://test"
        ) as client:
            created = await client.post(
                "/api/merchant-command/create", json=_body(name)
            )
            assert created.status_code == 201
            merchant_id = created.json()["data"]["id"]
            assert merchant_id > 0
            assert created.json()["data"]["status"] == "active"
            assert len(created.json()["data"]["created_at"]) == 19

            listed = await client.get("/api/merchant-query", params={"search": name})
            assert listed.status_code == 200
            assert listed.json()["pagination"]["total_records"] >= 1
            assert listed.json()["data"][0]["id"] == merchant_id

            by_id = await client.get(f"/api/merchant-query/{merchant_id}")
            assert by_id.status_code == 200
            assert by_id.json()["data"]["id"] == merchant_id

            active = await client.get(
                "/api/merchant-query/active", params={"search": name}
            )
            assert active.status_code == 200
            assert active.json()["message"] == "Successfully fetched active merchants"

            trashed_list = await client.get(
                "/api/merchant-query/trashed", params={"search": name}
            )
            assert trashed_list.status_code == 200
            assert (
                trashed_list.json()["message"]
                == "Successfully fetched trashed merchants"
            )

            # Query find_by_id forwards 0 -> gRPC 400 invalid merchant ID.
            bad_id = await client.get("/api/merchant-query/0")
            assert bad_id.status_code == 400
            assert bad_id.json()["message"] == "invalid merchant ID"

            # Command id guard is gateway-side 400 Invalid ID.
            bad_trash = await client.post("/api/merchant-command/trashed/0")
            assert bad_trash.status_code == 400
            assert bad_trash.json()["message"] == "Invalid ID"

            missing = await client.post("/api/merchant-command/trashed/2000000000")
            assert missing.status_code == 404
            assert missing.json()["type"] == "NOT_FOUND"

            updated = await client.post(
                f"/api/merchant-command/update/{merchant_id}",
                json=_body(f"{name} v2"),
            )
            assert updated.status_code == 200
            assert updated.json()["data"]["name"] == f"{name} v2"

            trashed = await client.post(
                f"/api/merchant-command/trashed/{merchant_id}"
            )
            assert trashed.status_code == 200
            assert trashed.json()["data"]["deleted_at"]

            # Static path wins over `/restore/{merchant_id}`.
            restore_all = await client.post("/api/merchant-command/restore/all")
            assert restore_all.status_code == 200
            assert restore_all.json()["message"] == "Successfully restored all merchants"

            await client.post(f"/api/merchant-command/trashed/{merchant_id}")
            deleted = await client.delete(
                f"/api/merchant-command/permanent/{merchant_id}"
            )
            assert deleted.status_code == 200
            assert (
                deleted.json()["message"]
                == "Successfully deleted merchant permanently"
            )

            permanent_all = await client.post("/api/merchant-command/permanent/all")
            assert permanent_all.status_code == 200
            merchant_id = None
    finally:
        await channel.close()
        await _cleanup(db, merchant_id, user_id)


async def test_merchant_create_requires_auth(
    db: Database, merchant_grpc_server: str
) -> None:
    channel = grpc.aio.insecure_channel(merchant_grpc_server)
    app = _app(merchant_grpc_server, channel, user_id=None)
    transport = httpx.ASGITransport(app=app)
    try:
        async with httpx.AsyncClient(
            transport=transport, base_url="http://test"
        ) as client:
            response = await client.post(
                "/api/merchant-command/create", json=_body("No Auth")
            )
            assert response.status_code == 401
    finally:
        await channel.close()


__all__ = []

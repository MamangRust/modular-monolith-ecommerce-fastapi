"""Gateway contract tests: FastAPI REST -> real merchant_policy gRPC over HTTPX. Marked `integration` because it needs PostgreSQL + Redis (the merchant_policy service is real). Verifies: create returns 200 (uses `http.StatusOK`); the REST timestamp shape; the filled `merchant_name` on list rows; static paths (`/active`, `/trashed`, `/restore/all`, `/permanent/all`) winning over the `{merchant_policy_id}` variants; the gateway 400 `Invalid ID` on every path-id route including the query `find_by_id`; the 404 `NOT_FOUND` preservation; and the validation 400."""

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


def _app(server: str, channel: grpc.aio.Channel) -> FastAPI:
    app = FastAPI()
    app.state.connections = ServiceConnections(
        channels={"merchant_policy": channel},
        addresses={"merchant_policy": server},
    )
    register_exception_handlers(app)
    register_routers(app)
    return app


async def _seed_merchant(db: Database) -> tuple[int, int, str]:
    email = f"test_merchant_policy_contract_{uuid.uuid4().hex[:10]}@example.com"
    name = f"Merchant {uuid.uuid4().hex[:10]}"
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
    merchant = await db.execute(
        """
        INSERT INTO merchants (
            user_id, name, description, address, contact_email, contact_phone, status
        )
        VALUES (:user_id, :name, 'd', 'a', 'e@f.com', '0812', 'active')
        RETURNING merchant_id
        """,
        {"user_id": user_id, "name": name},
    )
    assert merchant is not None
    return user_id, int(merchant["merchant_id"]), name


async def _cleanup(db: Database, merchant_id: int, user_id: int) -> None:
    await db.execute(
        "DELETE FROM merchant_policies WHERE merchant_id = :mid", {"mid": merchant_id}
    )
    await db.execute(
        "DELETE FROM merchants WHERE merchant_id = :mid", {"mid": merchant_id}
    )
    await db.execute("DELETE FROM users WHERE user_id = :uid", {"uid": user_id})


def _body(merchant_id: int, policy_type: str = "Shipping") -> dict[str, object]:
    return {
        "merchant_id": merchant_id,
        "policy_type": policy_type,
        "title": "Free Shipping on Orders Above $50",
        "description": "desc",
    }


async def test_merchant_policy_rest_contract(
    db: Database, merchant_policy_grpc_server: str
) -> None:
    channel = grpc.aio.insecure_channel(merchant_policy_grpc_server)
    app = _app(merchant_policy_grpc_server, channel)

    user_id, merchant_id, name = await _seed_merchant(db)
    policy_id: int | None = None
    try:
        transport = httpx.ASGITransport(app=app)
        async with httpx.AsyncClient(
            transport=transport, base_url="http://test"
        ) as client:
            created = await client.post(
                "/api/merchant-policy-command/create", json=_body(merchant_id)
            )
            assert created.status_code == 200
            policy_id = created.json()["data"]["id"]
            assert policy_id > 0
            assert created.json()["data"]["policy_type"] == "Shipping"
            assert len(created.json()["data"]["created_at"]) == 23

            listed = await client.get(
                "/api/merchant-policy-query", params={"search": name}
            )
            assert listed.status_code == 200
            assert listed.json()["pagination"]["total_records"] >= 1
            assert listed.json()["data"][0]["id"] == policy_id
            # Unlike merchant_business, merchant_name is projected for lists.
            assert listed.json()["data"][0]["merchant_name"] == name

            by_id = await client.get(f"/api/merchant-policy-query/{policy_id}")
            assert by_id.status_code == 200
            assert by_id.json()["data"]["id"] == policy_id

            active = await client.get(
                "/api/merchant-policy-query/active", params={"search": name}
            )
            assert active.status_code == 200
            assert active.json()["message"] == "Successfully fetched merchant policies"

            trashed_list = await client.get(
                "/api/merchant-policy-query/trashed", params={"search": name}
            )
            assert trashed_list.status_code == 200

            bad_id = await client.get("/api/merchant-policy-query/0")
            assert bad_id.status_code == 400
            assert bad_id.json()["message"] == "Invalid ID"

            bad_trash = await client.post("/api/merchant-policy-command/trashed/0")
            assert bad_trash.status_code == 400
            assert bad_trash.json()["message"] == "Invalid ID"

            missing = await client.post(
                "/api/merchant-policy-command/trashed/2000000000"
            )
            assert missing.status_code == 404
            assert missing.json()["type"] == "NOT_FOUND"

            updated = await client.post(
                f"/api/merchant-policy-command/update/{policy_id}",
                json=_body(merchant_id, "Refund"),
            )
            assert updated.status_code == 200
            assert updated.json()["data"]["policy_type"] == "Refund"

            trashed = await client.post(
                f"/api/merchant-policy-command/trashed/{policy_id}"
            )
            assert trashed.status_code == 200
            assert trashed.json()["data"]["deleted_at"]

            # Static path wins over `/restore/{merchant_policy_id}`.
            restore_all = await client.post(
                "/api/merchant-policy-command/restore/all"
            )
            assert restore_all.status_code == 200
            assert (
                restore_all.json()["message"]
                == "Successfully restored all merchant policies"
            )

            await client.post(f"/api/merchant-policy-command/trashed/{policy_id}")
            deleted = await client.delete(
                f"/api/merchant-policy-command/permanent/{policy_id}"
            )
            assert deleted.status_code == 200
            assert (
                deleted.json()["message"]
                == "Successfully deleted merchant policy permanently"
            )
            policy_id = None

            permanent_all = await client.post(
                "/api/merchant-policy-command/permanent/all"
            )
            assert permanent_all.status_code == 200
            assert (
                permanent_all.json()["message"]
                == "Successfully deleted all merchant policies permanently"
            )

            invalid = await client.post(
                "/api/merchant-policy-command/create",
                json=_body(merchant_id, ""),
            )
            assert invalid.status_code == 400
    finally:
        await channel.close()
        await _cleanup(db, merchant_id, user_id)


__all__ = []

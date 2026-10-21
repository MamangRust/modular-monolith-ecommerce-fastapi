"""Gateway contract tests: FastAPI REST -> real merchant_business gRPC over HTTPX. Marked `integration` because it needs PostgreSQL + Redis (the merchant_business service is real). Verifies: create returns 200 (uses `http.StatusOK`); the REST timestamp shape (no DATE columns, unlike merchant_award); the empty `merchant_name`; static paths (`/active`, `/trashed`, `/restore/all`, `/permanent/all`) winning over the `{merchant_business_id}` variants; the gateway 400 `Invalid ID` on every path-id route including the query `find_by_id`; the 404 `NOT_FOUND` preservation; and the validation 400."""

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
        channels={"merchant_business": channel},
        addresses={"merchant_business": server},
    )
    register_exception_handlers(app)
    register_routers(app)
    return app


async def _seed_merchant(db: Database) -> tuple[int, int, str]:
    email = f"test_merchant_business_contract_{uuid.uuid4().hex[:10]}@example.com"
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
        "DELETE FROM merchant_business_information WHERE merchant_id = :mid",
        {"mid": merchant_id},
    )
    await db.execute(
        "DELETE FROM merchants WHERE merchant_id = :mid", {"mid": merchant_id}
    )
    await db.execute("DELETE FROM users WHERE user_id = :uid", {"uid": user_id})


def _body(merchant_id: int, business_type: str = "Toko Elektronik") -> dict[str, object]:
    return {
        "merchant_id": merchant_id,
        "business_type": business_type,
        "tax_id": "01.234.567.8-999.000",
        "established_year": 2010,
        "number_of_employees": 15,
        "website_url": "https://technostore.com",
    }


async def test_merchant_business_rest_contract(
    db: Database, merchant_business_grpc_server: str
) -> None:
    channel = grpc.aio.insecure_channel(merchant_business_grpc_server)
    app = _app(merchant_business_grpc_server, channel)

    user_id, merchant_id, name = await _seed_merchant(db)
    business_id: int | None = None
    try:
        transport = httpx.ASGITransport(app=app)
        async with httpx.AsyncClient(
            transport=transport, base_url="http://test"
        ) as client:
            created = await client.post(
                "/api/merchant-business-command/create", json=_body(merchant_id)
            )
            # Create returns 200 (StatusOK), NOT 201.
            assert created.status_code == 200
            business_id = created.json()["data"]["id"]
            assert business_id > 0
            assert created.json()["data"]["business_type"] == "Toko Elektronik"
            assert created.json()["data"]["established_year"] == 2010
            assert len(created.json()["data"]["created_at"]) == 23
            # merchant_name is never projected.
            assert created.json()["data"]["merchant_name"] == ""

            listed = await client.get(
                "/api/merchant-business-query", params={"search": name}
            )
            assert listed.status_code == 200
            assert listed.json()["pagination"]["total_records"] >= 1
            assert listed.json()["data"][0]["id"] == business_id

            by_id = await client.get(f"/api/merchant-business-query/{business_id}")
            assert by_id.status_code == 200
            assert by_id.json()["data"]["id"] == business_id

            active = await client.get(
                "/api/merchant-business-query/active", params={"search": name}
            )
            assert active.status_code == 200
            assert active.json()["message"] == "Successfully fetched active merchant"

            trashed_list = await client.get(
                "/api/merchant-business-query/trashed", params={"search": name}
            )
            assert trashed_list.status_code == 200
            assert (
                trashed_list.json()["message"]
                == "Successfully fetched trashed merchant"
            )

            # The query find_by_id also guards with `Invalid ID`.
            bad_id = await client.get("/api/merchant-business-query/0")
            assert bad_id.status_code == 400
            assert bad_id.json()["message"] == "Invalid ID"

            bad_trash = await client.post("/api/merchant-business-command/trashed/0")
            assert bad_trash.status_code == 400
            assert bad_trash.json()["message"] == "Invalid ID"

            missing = await client.post(
                "/api/merchant-business-command/trashed/2000000000"
            )
            assert missing.status_code == 404
            assert missing.json()["type"] == "NOT_FOUND"

            updated = await client.post(
                f"/api/merchant-business-command/update/{business_id}",
                json=_body(merchant_id, "Retail Gadget"),
            )
            assert updated.status_code == 200
            assert updated.json()["data"]["business_type"] == "Retail Gadget"

            trashed = await client.post(
                f"/api/merchant-business-command/trashed/{business_id}"
            )
            assert trashed.status_code == 200
            assert trashed.json()["data"]["deleted_at"]

            # Static path wins over `/restore/{merchant_business_id}`.
            restore_all = await client.post(
                "/api/merchant-business-command/restore/all"
            )
            assert restore_all.status_code == 200
            assert (
                restore_all.json()["message"]
                == "Successfully restored all trashed merchant businesses"
            )

            await client.post(
                f"/api/merchant-business-command/trashed/{business_id}"
            )
            deleted = await client.delete(
                f"/api/merchant-business-command/permanent/{business_id}"
            )
            assert deleted.status_code == 200
            assert (
                deleted.json()["message"]
                == "Successfully deleted merchant business permanently"
            )
            business_id = None

            permanent_all = await client.post(
                "/api/merchant-business-command/permanent/all"
            )
            assert permanent_all.status_code == 200
            assert (
                permanent_all.json()["message"]
                == "Successfully deleted all merchant businesses permanently"
            )

            # Validation 400 (empty required field).
            invalid = await client.post(
                "/api/merchant-business-command/create",
                json=_body(merchant_id, ""),
            )
            assert invalid.status_code == 400
    finally:
        await channel.close()
        await _cleanup(db, merchant_id, user_id)


__all__ = []

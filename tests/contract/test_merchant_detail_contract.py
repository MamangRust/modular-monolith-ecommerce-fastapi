"""Gateway contract tests: FastAPI REST -> real merchant_detail gRPC over HTTPX. Marked `integration` because it needs PostgreSQL + Redis (the merchant_detail service is real) plus the merchant service (the create path validates the parent merchant over gRPC). Verifies: create returns 201; the REST `id`/`created_at` shape (`.mmm`); the empty `social_media_links`; static paths (`/active`, `/trashed`, `/restore/all`, `/permanent/all`) winning over the `{merchant_detail_id}` variants; the gateway 400 `Invalid ID` for command ids; the message 400 `id is required` for `/api/merchant-detail-query/0`; the 404 `NOT_FOUND` preservation; and the validation 400."""

from __future__ import annotations

import uuid

import grpc
import httpx
import pytest
from fastapi import FastAPI

from pb.merchant import merchant_command_pb2, merchant_command_pb2_grpc
from pkg.database.database import Database
from service.apigateway.app.client import ServiceConnections
from service.apigateway.handler import register_routers
from shared.errorhandler import register_exception_handlers

pytestmark = pytest.mark.integration


def _app(server: str, channel: grpc.aio.Channel) -> FastAPI:
    app = FastAPI()
    app.state.connections = ServiceConnections(
        channels={"merchant_detail": channel},
        addresses={"merchant_detail": server},
    )
    register_exception_handlers(app)
    register_routers(app)
    return app


async def _seed_user(db: Database) -> int:
    email = f"test_merchant_detail_contract_{uuid.uuid4().hex[:10]}@example.com"
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
            "DELETE FROM merchant_social_media_links WHERE merchant_detail_id IN "
            "(SELECT merchant_detail_id FROM merchant_details WHERE merchant_id = :mid)",
            {"mid": merchant_id},
        )
        await db.execute(
            "DELETE FROM merchant_details WHERE merchant_id = :mid",
            {"mid": merchant_id},
        )
        await db.execute(
            "DELETE FROM merchants WHERE merchant_id = :mid", {"mid": merchant_id}
        )
    await db.execute("DELETE FROM outbox_events WHERE event_key LIKE 'merchant-%'")
    await db.execute("DELETE FROM users WHERE user_id = :uid", {"uid": user_id})


def _body(merchant_id: int, display_name: str = "Techno Store") -> dict[str, object]:
    return {
        "merchant_id": merchant_id,
        "display_name": display_name,
        "cover_image_url": "cover/techno.jpg",
        "logo_url": "logo/techno.png",
        "short_description": "Pusat elektronik",
        "website_url": "https://technostore.com",
    }


async def test_merchant_detail_rest_contract(
    db: Database, merchant_grpc_server: str, merchant_detail_grpc_server: str
) -> None:
    merchant_channel = grpc.aio.insecure_channel(merchant_grpc_server)
    channel = grpc.aio.insecure_channel(merchant_detail_grpc_server)
    merchant_command = merchant_command_pb2_grpc.MerchantCommandServiceStub(
        merchant_channel
    )
    app = _app(merchant_detail_grpc_server, channel)

    user_id = await _seed_user(db)
    name = f"Merchant {uuid.uuid4().hex[:10]}"
    merchant_id: int | None = None
    detail_id: int | None = None

    try:
        merchant = await merchant_command.Create(
            merchant_command_pb2.CreateMerchantRequest(
                user_id=user_id,
                name=name,
                description="d",
                address="a",
                contact_email="e@f.com",
                contact_phone="0812",
                status="active",
            ),
            timeout=5,
        )
        merchant_id = merchant.data.id

        transport = httpx.ASGITransport(app=app)
        async with httpx.AsyncClient(
            transport=transport, base_url="http://test"
        ) as client:
            created = await client.post(
                "/api/merchant-detail-command/create", json=_body(merchant_id)
            )
            assert created.status_code == 201
            detail_id = created.json()["data"]["id"]
            assert detail_id > 0
            assert created.json()["data"]["display_name"] == "Techno Store"
            assert len(created.json()["data"]["created_at"]) == 23
            assert created.json()["data"]["social_media_links"] is None

            listed = await client.get(
                "/api/merchant-detail-query", params={"search": name}
            )
            assert listed.status_code == 200
            assert listed.json()["pagination"]["total_records"] >= 1
            assert listed.json()["data"][0]["id"] == detail_id

            by_id = await client.get(f"/api/merchant-detail-query/{detail_id}")
            assert by_id.status_code == 200
            assert by_id.json()["data"]["id"] == detail_id
            assert by_id.json()["data"]["social_media_links"] is None

            active = await client.get(
                "/api/merchant-detail-query/active", params={"search": name}
            )
            assert active.status_code == 200
            assert (
                active.json()["message"]
                == "Successfully fetched active merchant details"
            )

            trashed_list = await client.get(
                "/api/merchant-detail-query/trashed", params={"search": name}
            )
            assert trashed_list.status_code == 200
            assert (
                trashed_list.json()["message"]
                == "Successfully fetched trashed merchant details"
            )

            # Query find_by_id guards id <= 0 with message.
            bad_id = await client.get("/api/merchant-detail-query/0")
            assert bad_id.status_code == 400
            assert bad_id.json()["message"] == "id is required"

            # Command id guard is gateway-side 400 Invalid ID.
            bad_trash = await client.post("/api/merchant-detail-command/trashed/0")
            assert bad_trash.status_code == 400
            assert bad_trash.json()["message"] == "Invalid ID"

            missing = await client.post(
                "/api/merchant-detail-command/trashed/2000000000"
            )
            assert missing.status_code == 404
            assert missing.json()["type"] == "NOT_FOUND"

            updated = await client.post(
                f"/api/merchant-detail-command/update/{detail_id}",
                json=_body(merchant_id, "Techno Store v2"),
            )
            assert updated.status_code == 200
            assert updated.json()["data"]["display_name"] == "Techno Store v2"

            trashed = await client.post(
                f"/api/merchant-detail-command/trashed/{detail_id}"
            )
            assert trashed.status_code == 200
            assert trashed.json()["data"]["deleted_at"]

            # Static path wins over `/restore/{merchant_detail_id}`.
            restore_all = await client.post(
                "/api/merchant-detail-command/restore/all"
            )
            assert restore_all.status_code == 200
            assert (
                restore_all.json()["message"]
                == "Successfully restored all merchant details"
            )

            await client.post(f"/api/merchant-detail-command/trashed/{detail_id}")
            deleted = await client.delete(
                f"/api/merchant-detail-command/permanent/{detail_id}"
            )
            assert deleted.status_code == 200
            assert (
                deleted.json()["message"]
                == "Successfully deleted merchant detail permanently"
            )
            detail_id = None

            permanent_all = await client.post(
                "/api/merchant-detail-command/permanent/all"
            )
            assert permanent_all.status_code == 200

            # Validation 400 (empty required field).
            invalid = await client.post(
                "/api/merchant-detail-command/create",
                json=_body(merchant_id, ""),
            )
            assert invalid.status_code == 400
    finally:
        await channel.close()
        await merchant_channel.close()
        await _cleanup(db, merchant_id, user_id)


__all__ = []

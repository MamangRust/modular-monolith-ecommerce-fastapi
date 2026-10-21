"""Gateway contract tests: FastAPI REST -> merchant_social_link gRPC over HTTPX. Marked `integration`. The social command servicer is hosted by the merchant_detail service, so the test app points the `merchant_detail` channel at the merchant_detail server (`ServiceConnections.MerchantSocial` is never assigned). Verifies: create/update return 200 (NOT 201, unlike merchant detail create); the REST `created_at`/`updated_at` stay `""` (the command mapper ignores the proto timestamps but the struct serialises the zero strings); the update id guard is a gateway 400 `Invalid ID`; and validation 400s (missing `platform`, missing `merchant_detail_id`)."""

from __future__ import annotations

import uuid

import grpc
import httpx
import pytest
from fastapi import FastAPI

from pb.merchant import merchant_command_pb2, merchant_command_pb2_grpc
from pb.merchant_detail import (
    merchant_detail_command_pb2,
    merchant_detail_command_pb2_grpc,
)
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
    email = f"test_merchant_social_contract_{uuid.uuid4().hex[:10]}@example.com"
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


async def test_merchant_social_link_rest_contract(
    db: Database, merchant_grpc_server: str, merchant_detail_grpc_server: str
) -> None:
    merchant_channel = grpc.aio.insecure_channel(merchant_grpc_server)
    channel = grpc.aio.insecure_channel(merchant_detail_grpc_server)
    merchant_command = merchant_command_pb2_grpc.MerchantCommandServiceStub(
        merchant_channel
    )
    detail_command = (
        merchant_detail_command_pb2_grpc.MerchantDetailCommandServiceStub(channel)
    )
    app = _app(merchant_detail_grpc_server, channel)

    user_id = await _seed_user(db)
    name = f"Merchant {uuid.uuid4().hex[:10]}"
    merchant_id: int | None = None

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

        detail = await detail_command.Create(
            merchant_detail_command_pb2.CreateMerchantDetailRequest(
                merchant_id=merchant_id,
                display_name="Techno Store",
                short_description="d",
            ),
            timeout=5,
        )
        detail_id = detail.data.id

        transport = httpx.ASGITransport(app=app)
        async with httpx.AsyncClient(
            transport=transport, base_url="http://test"
        ) as client:
            created = await client.post(
                "/api/merchant-social-link/create",
                json={
                    "merchant_detail_id": detail_id,
                    "platform": "Facebook",
                    "url": "https://facebook.com/merchant1",
                },
            )
            # Social create returns 200 (NOT 201).
            assert created.status_code == 200
            assert created.json()["data"]["id"] > 0
            assert created.json()["data"]["platform"] == "Facebook"
            # The command mapper ignores the proto timestamps -> empty strings.
            assert created.json()["data"]["created_at"] == ""
            assert created.json()["data"]["updated_at"] == ""
            social_id = created.json()["data"]["id"]

            updated = await client.post(
                f"/api/merchant-social-link/update/{social_id}",
                json={
                    "merchant_detail_id": detail_id,
                    "platform": "Twitter",
                    "url": "https://twitter.com/merchant1",
                },
            )
            assert updated.status_code == 200
            assert updated.json()["data"]["platform"] == "Twitter"

            # Update id guard is gateway-side 400 Invalid ID.
            bad_update = await client.post(
                "/api/merchant-social-link/update/0",
                json={
                    "merchant_detail_id": detail_id,
                    "platform": "Twitter",
                    "url": "https://twitter.com/merchant1",
                },
            )
            assert bad_update.status_code == 400
            assert bad_update.json()["message"] == "Invalid ID"

            # Validation: missing platform.
            missing_platform = await client.post(
                "/api/merchant-social-link/create",
                json={
                    "merchant_detail_id": detail_id,
                    "url": "https://facebook.com/merchant1",
                },
            )
            assert missing_platform.status_code == 400

            # Validation: merchant_detail_id is required (`*int` + required).
            missing_detail = await client.post(
                "/api/merchant-social-link/create",
                json={
                    "platform": "Facebook",
                    "url": "https://facebook.com/merchant1",
                },
            )
            assert missing_detail.status_code == 400
    finally:
        await channel.close()
        await merchant_channel.close()
        await _cleanup(db, merchant_id, user_id)


__all__ = []

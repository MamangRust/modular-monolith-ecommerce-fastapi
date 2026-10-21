"""Gateway contract tests: FastAPI REST -> real banner gRPC over HTTPX. Marked `integration` because it needs PostgreSQL + Redis (the banner service is real, not mocked). The banner routes are JWT-only (no `RequireRoles` middleware in the reference), so the test app registers the routers directly without an auth layer."""

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


def _app(banner_grpc_server: str, channel: grpc.aio.Channel) -> FastAPI:
    app = FastAPI()
    app.state.connections = ServiceConnections(
        channels={"banner": channel}, addresses={"banner": banner_grpc_server}
    )
    register_exception_handlers(app)
    register_routers(app)
    return app


def _create_payload(name: str) -> dict:
    return {
        "name": name,
        "start_date": "2023-01-01",
        "end_date": "2023-01-31",
        "start_time": "08:00:00",
        "end_time": "16:00:00",
        "is_active": True,
    }


async def test_banner_rest_contract(
    db: Database, banner_grpc_server: str
) -> None:
    channel = grpc.aio.insecure_channel(banner_grpc_server)
    app = _app(banner_grpc_server, channel)
    name = f"TEST_CONTRACT_{uuid.uuid4().hex[:10]}"
    transport = httpx.ASGITransport(app=app)

    try:
        async with httpx.AsyncClient(
            transport=transport, base_url="http://test"
        ) as client:
            created = await client.post(
                "/api/banner-command/create", json=_create_payload(name)
            )
            assert created.status_code == 200
            body = created.json()
            assert body["status"] == "success"
            assert body["message"] == "Successfully created banner"
            assert body["data"]["name"] == name
            assert body["data"]["start_date"] == "2023-01-01"
            assert body["data"]["start_time"] == "08:00:00"
            banner_id = body["data"]["id"]

            listed = await client.get("/api/banner-query", params={"search": name})
            assert listed.status_code == 200
            listed_body = listed.json()
            assert listed_body["pagination"]["total_records"] >= 1
            assert listed_body["data"][0]["name"] == name

            by_id = await client.get(f"/api/banner-query/{banner_id}")
            assert by_id.status_code == 200
            assert by_id.json()["data"]["id"] == banner_id

            # Route-ordering regression: `/active` and `/trashed` must be
            # matched as static routes, not captured as banner_id="active".
            active = await client.get("/api/banner-query/active")
            assert active.status_code == 200
            assert active.json()["status"] == "success"

            trashed_list = await client.get("/api/banner-query/trashed")
            assert trashed_list.status_code == 200
            assert trashed_list.json()["status"] == "success"

            bad_id = await client.get("/api/banner-query/0")
            assert bad_id.status_code == 400
            assert bad_id.json()["message"] == "Invalid ID"

            missing = await client.get("/api/banner-query/2000000000")
            assert missing.status_code == 404
            assert missing.json()["type"] == "NOT_FOUND"

            invalid_body = await client.post(
                "/api/banner-command/create",
                json={**_create_payload("bad"), "start_date": "2023/01/01"},
            )
            assert invalid_body.status_code == 400
            assert invalid_body.json()["message"] == "Validation failed"

            updated = await client.post(
                f"/api/banner-command/update/{banner_id}",
                json={
                    "name": f"{name}_X",
                    "start_date": "2023-02-01",
                    "end_date": "2023-02-28",
                    "start_time": "09:00:00",
                    "end_time": "17:00:00",
                    "is_active": False,
                },
            )
            assert updated.status_code == 200
            assert updated.json()["data"]["name"] == f"{name}_X"

            trashed = await client.post(f"/api/banner-command/trashed/{banner_id}")
            assert trashed.status_code == 200
            trashed_body = trashed.json()
            assert trashed_body["message"] == "Successfully trashed banner"
            assert trashed_body["data"]["deleted_at"]

            restored = await client.post(f"/api/banner-command/restore/{banner_id}")
            assert restored.status_code == 200
            assert restored.json()["data"]["id"] == banner_id

            # Static path must win over `/restore/{banner_id}`.
            restore_all = await client.post("/api/banner-command/restore/all")
            assert restore_all.status_code == 200
            assert restore_all.json()["message"] == "Successfully restored all banners"

            deleted = await client.delete(f"/api/banner-command/permanent/{banner_id}")
            assert deleted.status_code == 200
            assert deleted.json()["message"] == "Successfully deleted banner permanently"

            permanent_all = await client.post("/api/banner-command/permanent/all")
            assert permanent_all.status_code == 200
            assert (
                permanent_all.json()["message"]
                == "Successfully deleted all banners permanently"
            )
    finally:
        await channel.close()
        await db.execute(
            "DELETE FROM banners WHERE name LIKE :pattern",
            {"pattern": "TEST_CONTRACT%"},
        )

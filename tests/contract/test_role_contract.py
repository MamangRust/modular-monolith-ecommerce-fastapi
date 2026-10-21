"""Gateway contract tests: FastAPI REST -> real role gRPC over HTTPX.

Marked `integration` because it needs PostgreSQL + Redis (the role service
is real, not mocked). RBAC is overridden with an authenticated admin so the
test targets the REST/gRPC contract rather than the Kafka validator.
"""

from __future__ import annotations

import uuid

import grpc
import httpx
import pytest
from fastapi import FastAPI

from pkg.database.database import Database
from service.apigateway.app.client import ServiceConnections
from service.apigateway.handler import register_routers
from service.apigateway.handler.role.command import require_command_admin
from service.apigateway.handler.role.query import require_query_admin
from shared.errorhandler import register_exception_handlers

pytestmark = pytest.mark.integration


def _app(role_grpc_server: str, channel: grpc.aio.Channel) -> FastAPI:
    app = FastAPI()
    app.state.connections = ServiceConnections(
        channels={"role": channel}, addresses={"role": role_grpc_server}
    )
    register_exception_handlers(app)
    register_routers(app)
    app.dependency_overrides[require_query_admin] = lambda: ["Admin_Role_10"]
    app.dependency_overrides[require_command_admin] = lambda: ["Admin_Admin_14"]
    return app


async def test_role_rest_contract(db: Database, role_grpc_server: str) -> None:
    channel = grpc.aio.insecure_channel(role_grpc_server)
    app = _app(role_grpc_server, channel)
    name = f"TEST_CONTRACT_{uuid.uuid4().hex[:10]}"
    transport = httpx.ASGITransport(app=app)

    try:
        async with httpx.AsyncClient(transport=transport, base_url="http://test") as client:
            created = await client.post("/api/role", json={"name": name})
            assert created.status_code == 200
            body = created.json()
            assert body["status"] == "success"
            assert body["data"]["name"] == name
            role_id = body["data"]["id"]

            listed = await client.get("/api/role-query", params={"search": name})
            assert listed.status_code == 200
            listed_body = listed.json()
            assert listed_body["pagination"]["total_records"] >= 1
            assert listed_body["data"][0]["name"] == name

            by_id = await client.get(f"/api/role-query/{role_id}")
            assert by_id.status_code == 200
            assert by_id.json()["data"]["id"] == role_id

            bad_id = await client.get("/api/role-query/0")
            assert bad_id.status_code == 400
            assert bad_id.json()["type"] == "BAD_REQUEST"
            assert bad_id.json()["code"] == 400
            assert bad_id.json()["message"] == "id is required"

            missing = await client.get("/api/role-query/2000000000")
            assert missing.status_code == 404
            assert missing.json()["type"] == "NOT_FOUND"

            duplicate = await client.post("/api/role", json={"name": name})
            assert duplicate.status_code == 409
            assert duplicate.json()["code"] == 409

            invalid_body = await client.post("/api/role", json={"name": ""})
            assert invalid_body.status_code == 400
            assert invalid_body.json()["message"] == "Validation failed"

            trashed = await client.post(f"/api/role/trashed/{role_id}")
            assert trashed.status_code == 200
            # Ecommerce contract: Trash/Restore return the basic `RoleResponse`
            # envelope — the ecommerce proto has no `deleted_at` on the wire
            # (only the trashed *list* uses `RoleResponseDeleteAt`).
            trashed_body = trashed.json()
            assert trashed_body["status"] == "success"
            assert trashed_body["data"]["id"] == role_id
            assert "deleted_at" not in trashed_body["data"]

            restored = await client.put(f"/api/role/restore/{role_id}")
            assert restored.status_code == 200
            assert restored.json()["data"]["id"] == role_id

            deleted = await client.delete(f"/api/role/{role_id}")
            assert deleted.status_code == 200
            assert deleted.json()["data"] is None
    finally:
        await channel.close()
        await db.execute(
            "DELETE FROM roles WHERE role_name LIKE :pattern",
            {"pattern": "TEST_CONTRACT%"},
        )

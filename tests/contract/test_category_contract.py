"""Gateway contract tests: FastAPI REST -> real category gRPC over HTTPX. Marked `integration` because it needs PostgreSQL + Redis (the category service is real, not mocked). The category routes are JWT-only (no `RequireRoles` middleware in the reference), so the test app registers the routers directly without an auth layer. Create/update are multipart (`image` file optional); uploads are redirected to a tmp dir via monkeypatch."""

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
from service.apigateway.handler.category import handler as category_handler
from shared.errorhandler import register_exception_handlers

pytestmark = pytest.mark.integration


def _app(category_grpc_server: str, channel: grpc.aio.Channel) -> FastAPI:
    app = FastAPI()
    app.state.connections = ServiceConnections(
        channels={"category": channel}, addresses={"category": category_grpc_server}
    )
    app.state.upload_image = new_image_upload(get_logger("test-category"))
    register_exception_handlers(app)
    register_routers(app)
    return app


def _create_fields(name: str, slug: str) -> dict:
    return {
        "name": name,
        "description": "contract test category",
        "slug_category": slug,
        "image_category": "contract.png",
    }


async def test_category_rest_contract(
    db: Database, category_grpc_server: str, tmp_path, monkeypatch
) -> None:
    monkeypatch.setattr(category_handler, "_UPLOAD_DIR", str(tmp_path / "category"))
    channel = grpc.aio.insecure_channel(category_grpc_server)
    app = _app(category_grpc_server, channel)
    name = f"TEST_CONTRACT_{uuid.uuid4().hex[:10]}"
    slug = f"test-contract-{uuid.uuid4().hex[:12]}"
    transport = httpx.ASGITransport(app=app)

    try:
        async with httpx.AsyncClient(
            transport=transport, base_url="http://test"
        ) as client:
            created = await client.post(
                "/api/category-command/create",
                data=_create_fields(name, slug),
                files={"image": ("cat.png", b"img-bytes", "image/png")},
            )
            assert created.status_code == 201
            body = created.json()
            assert body["status"] == "success"
            assert body["message"] == "Successfully created category"
            assert body["data"]["name"] == name
            assert body["data"]["created_at"]  # `%Y-%m-%d`
            assert body["data"]["image_category"].startswith(str(tmp_path / "category"))
            category_id = body["data"]["id"]

            listed = await client.get("/api/category-query", params={"search": name})
            assert listed.status_code == 200
            listed_body = listed.json()
            assert listed_body["pagination"]["total_records"] >= 1
            assert listed_body["data"][0]["name"] == name

            by_id = await client.get(f"/api/category-query/{category_id}")
            assert by_id.status_code == 200
            assert by_id.json()["data"]["id"] == category_id

            # Route-ordering regression: `/active` and `/trashed` must be
            # matched as static routes, not captured as category_id="active".
            active = await client.get("/api/category-query/active")
            assert active.status_code == 200
            assert active.json()["status"] == "success"

            trashed_list = await client.get("/api/category-query/trashed")
            assert trashed_list.status_code == 200
            assert trashed_list.json()["status"] == "success"

            bad_id = await client.get("/api/category-query/0")
            assert bad_id.status_code == 400
            assert bad_id.json()["message"] == "Invalid category ID"

            missing = await client.get("/api/category-query/2000000000")
            assert missing.status_code == 404
            # category handler re-maps to `NewGrpcError`, whose detail
            # `Status` is `http.StatusText(404)` ("Not Found") — unlike banner,
            # which propagates `ToGrpcError` (type "NOT_FOUND").
            assert missing.json()["type"] == "Not Found"
            assert missing.json()["message"] == "Category not found"

            invalid_body = await client.post(
                "/api/category-command/create",
                data={**_create_fields("bad", "bad-slug"), "description": ""},
            )
            assert invalid_body.status_code == 400
            assert invalid_body.json()["message"] == "Validation failed"

            # Update without a file keeps the `image_category` form field.
            updated = await client.post(
                f"/api/category-command/update/{category_id}",
                data={
                    "name": f"{name}_X",
                    "description": "updated",
                    "slug_category": f"test-upd-{uuid.uuid4().hex[:12]}",
                    "image_category": "updated.png",
                },
            )
            assert updated.status_code == 200
            assert updated.json()["data"]["name"] == f"{name}_X"
            assert updated.json()["data"]["image_category"] == "updated.png"

            trashed = await client.post(
                f"/api/category-command/trashed/{category_id}"
            )
            assert trashed.status_code == 200
            trashed_body = trashed.json()
            assert trashed_body["message"] == "Successfully trashed category"
            assert trashed_body["data"]["deleted_at"]

            restored = await client.post(
                f"/api/category-command/restore/{category_id}"
            )
            assert restored.status_code == 200
            assert restored.json()["data"]["id"] == category_id

            # Static path must win over `/restore/{category_id}`.
            restore_all = await client.post("/api/category-command/restore/all")
            assert restore_all.status_code == 200
            assert (
                restore_all.json()["message"] == "Successfully restored all categories"
            )

            # `FindByIDTrashed` check), so trash it again first.
            await client.post(f"/api/category-command/trashed/{category_id}")
            deleted = await client.delete(
                f"/api/category-command/permanent/{category_id}"
            )
            assert deleted.status_code == 200
            assert (
                deleted.json()["message"]
                == "Successfully deleted category permanently"
            )

            permanent_all = await client.delete("/api/category-command/permanent/all")
            assert permanent_all.status_code == 200
            assert (
                permanent_all.json()["message"]
                == "Successfully deleted all categories permanently"
            )
    finally:
        await channel.close()
        await db.execute(
            "DELETE FROM categories WHERE name LIKE :pattern",
            {"pattern": "TEST_CONTRACT%"},
        )

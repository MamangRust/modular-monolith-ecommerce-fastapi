"""Gateway contract tests: FastAPI REST -> real slider gRPC over HTTPX. Marked `integration` because it needs PostgreSQL + Redis (the slider service is real, not mocked). Slider's `Create`/`Update` ARE exposed as REST (unlike shipping_address), so the fixture seeds through the REST layer. They are multipart endpoints (`image_slider` file); uploads to a tmp dir. Verifies the REST contract: `id` REST field, date-only timestamps, the static paths (`/active`, `/trashed`, `/restore/all`, `/permanent/all`) winning over the `{slider_id}` variants, the 400 `Invalid ID` mapper for command ids, and the 404 `NOT_FOUND` preservation for a missing slider (FindById has no id==0 guard, so `/{slider_id}` 0 reaches the repo and returns 404)."""

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
from service.apigateway.handler.slider import handler as slider_handler
from shared.errorhandler import register_exception_handlers

pytestmark = pytest.mark.integration


def _app(slider_grpc_server: str, channel: grpc.aio.Channel) -> FastAPI:
    app = FastAPI()
    app.state.connections = ServiceConnections(
        channels={"slider": channel},
        addresses={"slider": slider_grpc_server},
    )
    app.state.upload_image = new_image_upload(get_logger("test-slider"))
    register_exception_handlers(app)
    register_routers(app)
    return app


def _name() -> str:
    return f"Hero {uuid.uuid4().hex[:10]}"


async def _cleanup(db: Database, slider_id: int) -> None:
    await db.execute(
        "DELETE FROM sliders WHERE slider_id = :slider_id", {"slider_id": slider_id}
    )


async def test_slider_rest_contract(
    db: Database, slider_grpc_server: str, tmp_path, monkeypatch
) -> None:
    monkeypatch.setattr(slider_handler, "_UPLOAD_DIR", str(tmp_path / "slider"))
    channel = grpc.aio.insecure_channel(slider_grpc_server)
    app = _app(slider_grpc_server, channel)
    name = _name()
    transport = httpx.ASGITransport(app=app)

    try:
        async with httpx.AsyncClient(transport=transport, base_url="http://test") as client:
            created = await client.post(
                "/api/slider-command/create",
                data={"name": name},
                files={"image_slider": ("slider.png", b"img-bytes", "image/png")},
            )
            assert created.status_code == 201
            slider_id = created.json()["data"]["id"]
            assert slider_id > 0
            assert created.json()["data"]["name"] == name
            assert created.json()["data"]["image"].startswith(str(tmp_path / "slider"))

            # Missing image on create is a mirrored 400.
            no_image = await client.post(
                "/api/slider-command/create", data={"name": name}
            )
            assert no_image.status_code == 400
            assert no_image.json()["message"] == "Image is required"

            listed = await client.get(
                "/api/slider-query", params={"search": name}
            )
            assert listed.status_code == 200
            listed_body = listed.json()
            assert listed_body["pagination"]["total_records"] >= 1
            row = listed_body["data"][0]
            assert row["id"] == slider_id
            assert row["name"] == name
            assert len(row["created_at"]) == 10  # date-only

            by_id = await client.get(f"/api/slider-query/{slider_id}")
            assert by_id.status_code == 200
            assert by_id.json()["data"]["id"] == slider_id

            active = await client.get(
                "/api/slider-query/active", params={"search": name}
            )
            assert active.status_code == 200
            assert active.json()["message"] == "Successfully fetched active slider records"

            trashed_list = await client.get(
                "/api/slider-query/trashed", params={"search": name}
            )
            assert trashed_list.status_code == 200
            assert (
                trashed_list.json()["message"]
                == "Successfully fetched trashed slider records"
            )

            # Static `/active` must win over `/{slider_id}`.
            assert active.json()["status"] == "success"

            # FindById has no id==0 guard: 0 reaches the repo -> 404 NOT_FOUND.
            bad_id = await client.get("/api/slider-query/0")
            assert bad_id.status_code == 404
            assert bad_id.json()["type"] == "NOT_FOUND"

            bad_trash = await client.post("/api/slider-command/trashed/0")
            assert bad_trash.status_code == 400
            assert bad_trash.json()["message"] == "Invalid ID"

            missing = await client.post("/api/slider-command/trashed/2000000000")
            assert missing.status_code == 404
            assert missing.json()["type"] == "NOT_FOUND"

            trashed = await client.post(f"/api/slider-command/trashed/{slider_id}")
            assert trashed.status_code == 200
            assert trashed.json()["message"] == "Successfully trashed slider"
            assert trashed.json()["data"]["deleted_at"]

            after_trash = await client.get(
                "/api/slider-query", params={"search": name}
            )
            assert all(r["id"] != slider_id for r in after_trash.json()["data"])

            in_trash = await client.get(
                "/api/slider-query/trashed", params={"search": name}
            )
            assert any(r["id"] == slider_id for r in in_trash.json()["data"])

            restored = await client.post(
                f"/api/slider-command/restore/{slider_id}"
            )
            assert restored.status_code == 200
            assert restored.json()["data"]["id"] == slider_id

            # Static path must win over `/restore/{slider_id}`.
            restore_all = await client.post("/api/slider-command/restore/all")
            assert restore_all.status_code == 200
            assert restore_all.json()["message"] == "Successfully restored all sliders"

            await client.post(f"/api/slider-command/trashed/{slider_id}")
            deleted = await client.delete(
                f"/api/slider-command/permanent/{slider_id}"
            )
            assert deleted.status_code == 200
            assert deleted.json()["message"] == "Successfully deleted slider permanently"

            permanent_all = await client.post("/api/slider-command/permanent/all")
            assert permanent_all.status_code == 200
            assert (
                permanent_all.json()["message"]
                == "Successfully deleted all sliders permanently"
            )
    finally:
        await channel.close()
        # The slider may already be hard-deleted; ignore if gone.
        try:
            await _cleanup(db, slider_id)
        except Exception:
            pass


__all__ = []

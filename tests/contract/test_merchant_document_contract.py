"""Gateway contract tests: FastAPI REST -> real merchant_document gRPC (multipart). Marked `integration`. Verifies the multipart create/update contract (upload via `upload_image`, `document_url_old` fallback), the JSON update-status endpoint, the REST `id`/`created_at` mapping, the gateway 400 `Invalid ID` guards on both the query and command id routes, and the form-validation messages (`Invalid merchant ID`, `Document type is required`, `Document file is required`). Uploads are redirected to a tmp dir via monkeypatch."""

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
from service.apigateway.handler.merchant_document import handler as document_handler
from shared.errorhandler import register_exception_handlers

pytestmark = pytest.mark.integration


def _app(server: str, channel: grpc.aio.Channel) -> FastAPI:
    app = FastAPI()
    app.state.connections = ServiceConnections(
        channels={"merchant": channel}, addresses={"merchant": server}
    )
    app.state.upload_image = new_image_upload(get_logger("test-merchant-doc"))
    register_exception_handlers(app)
    register_routers(app)
    return app


async def _seed_merchant(db: Database) -> tuple[int, int]:
    email = f"test_merchant_doc_contract_{uuid.uuid4().hex[:10]}@example.com"
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
        INSERT INTO merchants (user_id, name, status)
        VALUES (:user_id, :name, 'active')
        RETURNING merchant_id
        """,
        {"user_id": user_id, "name": f"Merchant {uuid.uuid4().hex[:10]}"},
    )
    assert merchant is not None
    return user_id, int(merchant["merchant_id"])


async def _cleanup(db: Database, user_id: int, merchant_id: int) -> None:
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


async def test_merchant_document_rest_contract(
    db: Database, merchant_grpc_server: str, tmp_path, monkeypatch
) -> None:
    monkeypatch.setattr(
        document_handler, "_CREATE_UPLOAD_DIR", str(tmp_path / "create")
    )
    monkeypatch.setattr(
        document_handler, "_UPDATE_UPLOAD_DIR", str(tmp_path / "update")
    )
    channel = grpc.aio.insecure_channel(merchant_grpc_server)
    user_id, merchant_id = await _seed_merchant(db)
    app = _app(merchant_grpc_server, channel)
    document_type = f"TYPE{uuid.uuid4().hex[:6]}"
    transport = httpx.ASGITransport(app=app)

    try:
        async with httpx.AsyncClient(
            transport=transport, base_url="http://test"
        ) as client:
            created = await client.post(
                "/api/merchant-document-command/create",
                data={"merchant_id": str(merchant_id), "document_type": document_type},
                files={"document_url": ("nib.pdf", b"pdf-bytes", "application/pdf")},
            )
            assert created.status_code == 200
            document_id = created.json()["data"]["id"]
            assert document_id > 0
            assert created.json()["data"]["status"] == "pending"
            assert created.json()["data"]["created_at"]

            listed = await client.get(
                "/api/merchant-document-query", params={"search": document_type}
            )
            assert listed.status_code == 200
            assert listed.json()["pagination"]["total_records"] >= 1

            by_id = await client.get(f"/api/merchant-document-query/{document_id}")
            assert by_id.status_code == 200
            assert by_id.json()["data"]["id"] == document_id

            active = await client.get(
                "/api/merchant-document-query/active",
                params={"search": document_type},
            )
            assert active.status_code == 200
            trashed_list = await client.get(
                "/api/merchant-document-query/trashed",
                params={"search": document_type},
            )
            assert trashed_list.status_code == 200

            # Gateway guards id <= 0 on the document query find_by_id route.
            bad_id = await client.get("/api/merchant-document-query/0")
            assert bad_id.status_code == 400
            assert bad_id.json()["message"] == "Invalid ID"

            # Form validation messages mirror exactly.
            bad_merchant = await client.post(
                "/api/merchant-document-command/create",
                data={"merchant_id": "0", "document_type": document_type},
                files={"document_url": ("nib.pdf", b"x", "application/pdf")},
            )
            assert bad_merchant.status_code == 400
            assert bad_merchant.json()["message"] == "Invalid merchant ID"

            bad_type = await client.post(
                "/api/merchant-document-command/create",
                data={"merchant_id": str(merchant_id), "document_type": "  "},
                files={"document_url": ("nib.pdf", b"x", "application/pdf")},
            )
            assert bad_type.status_code == 400
            assert bad_type.json()["message"] == "Document type is required"

            bad_file = await client.post(
                "/api/merchant-document-command/create",
                data={"merchant_id": str(merchant_id), "document_type": document_type},
            )
            assert bad_file.status_code == 400
            assert bad_file.json()["message"] == "Document file is required"

            # Update with no new file falls back to document_url_old.
            updated = await client.post(
                f"/api/merchant-document-command/update/{document_id}",
                data={
                    "merchant_id": str(merchant_id),
                    "document_type": document_type,
                    "document_url_old": "uploads/merchant_document/old.pdf",
                    "status": "pending",
                    "note": "reviewed",
                },
            )
            assert updated.status_code == 200
            assert (
                updated.json()["data"]["document_url"]
                == "uploads/merchant_document/old.pdf"
            )

            status_row = await client.post(
                f"/api/merchant-document-command/update-status/{document_id}",
                json={"merchant_id": merchant_id, "status": "approved", "note": "ok"},
            )
            assert status_row.status_code == 200
            assert status_row.json()["data"]["status"] == "approved"

            trashed = await client.post(
                f"/api/merchant-document-command/trashed/{document_id}"
            )
            assert trashed.status_code == 200
            # maps Trashed to MerchantDocument (no deleted_at field).
            assert (
                trashed.json()["message"]
                == "Successfully trashed merchant document"
            )
            assert trashed.json()["data"]["id"] == document_id

            restored = await client.post(
                f"/api/merchant-document-command/restore/{document_id}"
            )
            assert restored.status_code == 200

            # Command id guard is gateway-side 400 Invalid ID.
            bad_trash = await client.post("/api/merchant-document-command/trashed/0")
            assert bad_trash.status_code == 400
            assert bad_trash.json()["message"] == "Invalid ID"

            await client.post(
                f"/api/merchant-document-command/trashed/{document_id}"
            )
            deleted = await client.delete(
                f"/api/merchant-document-command/permanent/{document_id}"
            )
            assert deleted.status_code == 200
            assert (
                deleted.json()["message"]
                == "Successfully permanently deleted merchant document"
            )

            restore_all = await client.post(
                "/api/merchant-document-command/restore/all"
            )
            assert restore_all.status_code == 200
            permanent_all = await client.post(
                "/api/merchant-document-command/permanent/all"
            )
            assert permanent_all.status_code == 200
    finally:
        await channel.close()
        await _cleanup(db, user_id, merchant_id)


__all__ = []

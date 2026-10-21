"""Unit tests for the gateway merchant-document transport handler. Unlike the merchant handler, the document gateway guards `id <= 0` on the query `find_by_id` route too (400 `Invalid ID`). The multipart create/update form is validated here to reproduce exact messages (`Invalid merchant ID`, `Document type is required`, `Document file is required`). Create uploads to `uploads/merchant_document`; update uploads to `uploads/merchant_document/files` and falls back to `document_url_old` when no file is sent."""

from __future__ import annotations

from typing import Any

import grpc
import pytest

from pb.merchant_document import merchant_document_common_pb2
from service.apigateway.app.client import ServiceConnections
from service.apigateway.handler.merchant_document.handler import (
    MerchantDocumentHandler,
    parse_merchant_id,
    require_positive_id,
)
from shared.errors import AppError


class FakeUpload:
    def __init__(self) -> None:
        self.calls: list[tuple[str, bool]] = []

    async def process_image_upload(
        self, upload_dir: str, file: Any, is_document: bool
    ) -> str:
        self.calls.append((upload_dir, is_document))
        return f"{upload_dir}/stored.pdf"


class FakeDocumentCommand:
    def __init__(self) -> None:
        self.last: Any = None

    async def Create(self, request: Any, timeout: float | None = None) -> Any:
        self.last = request
        message = merchant_document_common_pb2.ApiResponseMerchantDocument(
            status="success", message="Successfully created merchant document"
        )
        message.data.document_id = 1
        return message

    async def Update(self, request: Any, timeout: float | None = None) -> Any:
        self.last = request
        message = merchant_document_common_pb2.ApiResponseMerchantDocument(
            status="success", message="Successfully updated merchant document"
        )
        message.data.document_id = request.document_id
        return message


class FakeFile:
    filename = "nib.pdf"

    async def read(self) -> bytes:
        return b"hello"


@pytest.mark.parametrize("value", [0, -1])
def test_require_positive_id_rejects_non_positive(value: int) -> None:
    with pytest.raises(AppError) as excinfo:
        require_positive_id(value)
    assert excinfo.value.code == 400
    assert excinfo.value.message == "Invalid ID"


@pytest.mark.parametrize("value", ["", "abc", "0", "-3", None])
def test_parse_merchant_id_rejects_invalid(value: Any) -> None:
    with pytest.raises(AppError) as excinfo:
        parse_merchant_id(value)
    assert excinfo.value.code == 400
    assert excinfo.value.message == "Invalid merchant ID"


@pytest.mark.parametrize(("value", "expected"), [("3", 3), (5, 5), ("12", 12)])
def test_parse_merchant_id_accepts_positive(value: Any, expected: int) -> None:
    assert parse_merchant_id(value) == expected


def _handler() -> tuple[MerchantDocumentHandler, grpc.aio.Channel, Any]:
    channel = grpc.aio.insecure_channel("127.0.0.1:1")
    connections = ServiceConnections(
        channels={"merchant": channel}, addresses={"merchant": "127.0.0.1:1"}
    )
    upload: Any = FakeUpload()
    return MerchantDocumentHandler(connections, upload), channel, upload


async def test_handler_builds_query_and_command_stubs() -> None:
    handler, channel, _ = _handler()
    try:
        assert handler._query is not None
        assert handler._command is not None
    finally:
        await channel.close()


async def test_create_rejects_invalid_merchant_id() -> None:
    handler, channel, _ = _handler()
    try:
        with pytest.raises(AppError) as excinfo:
            await handler.create("0", "NIB", FakeFile())
        assert excinfo.value.message == "Invalid merchant ID"
    finally:
        await channel.close()


async def test_create_rejects_empty_document_type() -> None:
    handler, channel, _ = _handler()
    try:
        with pytest.raises(AppError) as excinfo:
            await handler.create("1", "   ", FakeFile())
        assert excinfo.value.message == "Document type is required"
    finally:
        await channel.close()


async def test_create_rejects_missing_file() -> None:
    handler, channel, _ = _handler()
    try:
        with pytest.raises(AppError) as excinfo:
            await handler.create("1", "NIB", None)
        assert excinfo.value.message == "Document file is required"
    finally:
        await channel.close()


async def test_create_uploads_to_document_dir() -> None:
    handler, channel, upload = _handler()
    fake: Any = FakeDocumentCommand()
    handler._command = fake
    try:
        response = await handler.create("10", "NIB", FakeFile())
        assert response.data.id == 1
        assert upload.calls == [("uploads/merchant_document", True)]
        assert fake.last.document_type == "NIB"
        assert fake.last.document_url == "uploads/merchant_document/stored.pdf"
    finally:
        await channel.close()


async def test_update_rejects_non_positive_id() -> None:
    handler, channel, _ = _handler()
    try:
        with pytest.raises(AppError) as excinfo:
            await handler.update(0, "1", "NIB", None, "old.pdf", "pending", "ok")
        assert excinfo.value.message == "Invalid ID"
    finally:
        await channel.close()


async def test_update_without_file_uses_document_url_old() -> None:
    handler, channel, upload = _handler()
    fake: Any = FakeDocumentCommand()
    handler._command = fake
    try:
        await handler.update(4, "10", "NIB", None, "uploads/old.pdf", "pending", "ok")
        assert upload.calls == []
        assert fake.last.document_url == "uploads/old.pdf"
        assert fake.last.status == "pending"
        assert fake.last.note == "ok"
    finally:
        await channel.close()


async def test_update_with_file_uploads_to_files_dir() -> None:
    handler, channel, upload = _handler()
    fake: Any = FakeDocumentCommand()
    handler._command = fake
    try:
        await handler.update(4, "10", "NIB", FakeFile(), "uploads/old.pdf", "ok", "note")
        assert upload.calls == [("uploads/merchant_document/files", True)]
        assert fake.last.document_url == "uploads/merchant_document/files/stored.pdf"
    finally:
        await channel.close()


async def test_update_rejects_empty_document_type() -> None:
    handler, channel, _ = _handler()
    try:
        with pytest.raises(AppError) as excinfo:
            await handler.update(4, "10", "", None, "old.pdf", "pending", "ok")
        assert excinfo.value.message == "Document type is required"
    finally:
        await channel.close()


__all__ = []

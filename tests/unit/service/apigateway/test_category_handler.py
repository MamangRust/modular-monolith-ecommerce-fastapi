"""Unit tests for the gateway category transport helpers. `create`/`update` accept a multipart `image` file (`FormFile("image")` -> `uploads/category`); when no file is sent the `image_category` field is used as-is. This documents the fix of (always sends the uploaded path, discarding `image_category`)."""

from __future__ import annotations

from typing import Any

import grpc
import pytest

from pb.category import category_common_pb2
from service.apigateway.app.client import ServiceConnections
from service.apigateway.handler.category.handler import (
    CategoryHandler,
    normalize_pagination,
)


class FakeUpload:
    def __init__(self) -> None:
        self.calls: list[tuple[str, bool]] = []

    async def process_image_upload(
        self, upload_dir: str, file: Any, is_document: bool
    ) -> str:
        self.calls.append((upload_dir, is_document))
        return f"{upload_dir}/stored.png"


class FakeCategoryCommand:
    def __init__(self) -> None:
        self.last: Any = None

    async def Create(self, request: Any, timeout: float | None = None) -> Any:
        self.last = request
        message = category_common_pb2.ApiResponseCategory(
            status="success", message="Successfully created category"
        )
        message.data.id = 1
        return message

    async def Update(self, request: Any, timeout: float | None = None) -> Any:
        self.last = request
        message = category_common_pb2.ApiResponseCategory(
            status="success", message="Successfully updated category"
        )
        message.data.id = request.category_id
        return message


class FakeFile:
    filename = "cat.png"

    async def read(self) -> bytes:
        return b"img"


@pytest.mark.parametrize(
    ("page", "page_size", "expected"),
    [
        (1, 10, (1, 10)),
        (0, 0, (1, 10)),
        (-5, -1, (1, 10)),
        (3, 0, (3, 10)),
        (0, 25, (1, 25)),
    ],
)
def test_normalize_pagination(
    page: int, page_size: int, expected: tuple[int, int]
) -> None:
    assert normalize_pagination(page, page_size) == expected


def _handler() -> tuple[CategoryHandler, grpc.aio.Channel, Any]:
    channel = grpc.aio.insecure_channel("127.0.0.1:1")
    connections = ServiceConnections(
        channels={"category": channel}, addresses={"category": "127.0.0.1:1"}
    )
    upload: Any = FakeUpload()
    return CategoryHandler(connections, upload), channel, upload


async def test_handler_builds_all_five_stubs() -> None:
    handler, channel, _ = _handler()
    try:
        assert handler._query is not None
        assert handler._command is not None
        assert handler._stats is not None
        assert handler._stats_by_id is not None
        assert handler._stats_by_merchant is not None
    finally:
        await channel.close()


async def test_create_with_file_uploads_to_category_dir() -> None:
    handler, channel, upload = _handler()
    fake: Any = FakeCategoryCommand()
    handler._command = fake
    try:
        await handler.create("Electronics", "desc", "electronics", "ignored.png", FakeFile())
        assert upload.calls == [("uploads/category", False)]
        assert fake.last.image_category == "uploads/category/stored.png"
    finally:
        await channel.close()


async def test_create_without_file_uses_image_category_field() -> None:
    handler, channel, upload = _handler()
    fake: Any = FakeCategoryCommand()
    handler._command = fake
    try:
        await handler.create("Electronics", "desc", "electronics", "keep.png", None)
        assert upload.calls == []
        assert fake.last.image_category == "keep.png"
    finally:
        await channel.close()


async def test_update_with_file_uploads_to_category_dir() -> None:
    handler, channel, upload = _handler()
    fake: Any = FakeCategoryCommand()
    handler._command = fake
    try:
        await handler.update(7, "Electronics", "desc", "electronics", "x.png", FakeFile())
        assert upload.calls == [("uploads/category", False)]
        assert fake.last.image_category == "uploads/category/stored.png"
        assert fake.last.category_id == 7
    finally:
        await channel.close()


async def test_update_without_file_uses_image_category_field() -> None:
    handler, channel, upload = _handler()
    fake: Any = FakeCategoryCommand()
    handler._command = fake
    try:
        await handler.update(7, "Electronics", "desc", "electronics", "keep.png", None)
        assert upload.calls == []
        assert fake.last.image_category == "keep.png"
    finally:
        await channel.close()


__all__ = []

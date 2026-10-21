"""Unit tests for the gateway slider transport helpers. `require_positive_id` Matches the expected gateway's `strconv.Atoi` + `<= 0` guard: a bad path id must fail at the gateway with `BAD_REQUEST` before any gRPC hop, using `"Invalid ID"` for every path-id route. The multipart create/update form is validated here to reproduce `parseSliderForm` messages (`Name is required`, `Image is required`). Create uploads to `uploads/slider`; update uploads only when a file is sent and otherwise forwards an empty image, matching."""

from __future__ import annotations

from typing import Any

import grpc
import pytest

from pb.slider import slider_common_pb2
from service.apigateway.app.client import ServiceConnections
from service.apigateway.handler.slider.handler import (
    SliderHandler,
    normalize_pagination,
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
        return f"{upload_dir}/stored.png"


class FakeSliderCommand:
    def __init__(self) -> None:
        self.last: Any = None

    async def Create(self, request: Any, timeout: float | None = None) -> Any:
        self.last = request
        message = slider_common_pb2.ApiResponseSlider(
            status="success", message="Successfully created slider"
        )
        message.data.id = 1
        return message

    async def Update(self, request: Any, timeout: float | None = None) -> Any:
        self.last = request
        message = slider_common_pb2.ApiResponseSlider(
            status="success", message="Successfully updated slider"
        )
        message.data.id = request.id
        return message


class FakeFile:
    filename = "slider.png"

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


@pytest.mark.parametrize("value", [0, -1, -2_000_000_000])
def test_require_positive_id_rejects_non_positive(value: int) -> None:
    with pytest.raises(AppError) as excinfo:
        require_positive_id(value)

    assert excinfo.value.code == 400
    assert excinfo.value.type == "BAD_REQUEST"
    assert excinfo.value.message == "Invalid ID"


@pytest.mark.parametrize("value", [1, 42])
def test_require_positive_id_accepts_positive(value: int) -> None:
    require_positive_id(value)


def _handler() -> tuple[SliderHandler, grpc.aio.Channel, Any]:
    channel = grpc.aio.insecure_channel("127.0.0.1:1")
    connections = ServiceConnections(
        channels={"slider": channel},
        addresses={"slider": "127.0.0.1:1"},
    )
    upload: Any = FakeUpload()
    return SliderHandler(connections, upload), channel, upload


async def test_handler_builds_query_and_command_stubs() -> None:
    handler, channel, _ = _handler()
    try:
        assert handler._query is not None
        assert handler._command is not None
    finally:
        await channel.close()


async def test_create_rejects_empty_name() -> None:
    handler, channel, _ = _handler()
    try:
        with pytest.raises(AppError) as excinfo:
            await handler.create("   ", FakeFile())
        assert excinfo.value.message == "Name is required"
    finally:
        await channel.close()


async def test_create_rejects_missing_image() -> None:
    handler, channel, _ = _handler()
    try:
        with pytest.raises(AppError) as excinfo:
            await handler.create("Hero", None)
        assert excinfo.value.message == "Image is required"
    finally:
        await channel.close()


async def test_create_uploads_to_slider_dir() -> None:
    handler, channel, upload = _handler()
    fake: Any = FakeSliderCommand()
    handler._command = fake
    try:
        response = await handler.create("  Hero  ", FakeFile())
        assert response.data is not None
        assert response.data.id == 1
        assert upload.calls == [("uploads/slider", False)]
        assert fake.last.name == "Hero"
        assert fake.last.image == "uploads/slider/stored.png"
    finally:
        await channel.close()


async def test_update_rejects_non_positive_id() -> None:
    handler, channel, _ = _handler()
    try:
        with pytest.raises(AppError) as excinfo:
            await handler.update(0, "Hero", FakeFile())
        assert excinfo.value.message == "Invalid ID"
    finally:
        await channel.close()


async def test_update_rejects_empty_name() -> None:
    handler, channel, _ = _handler()
    try:
        with pytest.raises(AppError) as excinfo:
            await handler.update(4, "", FakeFile())
        assert excinfo.value.message == "Name is required"
    finally:
        await channel.close()


async def test_update_without_file_sends_empty_image() -> None:
    handler, channel, upload = _handler()
    fake: Any = FakeSliderCommand()
    handler._command = fake
    try:
        await handler.update(4, "Hero", None)
        assert upload.calls == []
        assert fake.last.image == ""
        assert fake.last.name == "Hero"
    finally:
        await channel.close()


async def test_update_with_file_uploads_to_slider_dir() -> None:
    handler, channel, upload = _handler()
    fake: Any = FakeSliderCommand()
    handler._command = fake
    try:
        await handler.update(4, "Hero", FakeFile())
        assert upload.calls == [("uploads/slider", False)]
        assert fake.last.image == "uploads/slider/stored.png"
    finally:
        await channel.close()


__all__ = []

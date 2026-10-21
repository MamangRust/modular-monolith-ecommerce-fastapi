"""Unit tests for the gateway review_detail transport helpers. `require_positive_id` Matches the expected gateway's `strconv.Atoi` + `<= 0` guard: a bad path id must fail at the gateway with `BAD_REQUEST` before any gRPC hop, using `"Invalid ID"` for every path-id route. Unlike slider, the gRPC `FindById` handler *does* guard `id <= 0`, so the gateway `find_by_id` route does NOT add its own guard (it forwards 0 to gRPC, which returns 400). The gateway also replicates create/update form validation (`review_id`, non-empty type / caption) and resolves `url` as an uploaded file (`uploads/review_detail`) or a plain URL string."""

from __future__ import annotations

from typing import Any

import grpc
import pytest

from pb.review_detail import review_detail_common_pb2
from service.apigateway.app.client import ServiceConnections
from service.apigateway.handler.review_detail.handler import (
    ReviewDetailHandler,
    normalize_pagination,
    parse_review_id,
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


class FakeReviewDetailCommand:
    def __init__(self) -> None:
        self.last: Any = None

    async def Create(self, request: Any, timeout: float | None = None) -> Any:
        self.last = request
        message = review_detail_common_pb2.ApiResponseReviewDetail(
            status="success", message="Successfully created review detail"
        )
        message.data.id = 1
        return message

    async def Update(self, request: Any, timeout: float | None = None) -> Any:
        self.last = request
        message = review_detail_common_pb2.ApiResponseReviewDetail(
            status="success", message="Successfully updated review detail"
        )
        message.data.id = request.review_detail_id
        return message


class FakeFile:
    filename = "photo.jpg"

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


@pytest.mark.parametrize(("value", "expected"), [("", 0), (None, 0), ("5", 5), (7, 7)])
def test_parse_review_id_accepts(value: Any, expected: int) -> None:
    assert parse_review_id(value) == expected


@pytest.mark.parametrize("value", ["abc", "0", "-3", 0, -1])
def test_parse_review_id_rejects_invalid(value: Any) -> None:
    with pytest.raises(AppError) as excinfo:
        parse_review_id(value)
    assert excinfo.value.code == 400
    assert excinfo.value.message == "Invalid Review ID"


def _handler() -> tuple[ReviewDetailHandler, grpc.aio.Channel, Any]:
    channel = grpc.aio.insecure_channel("127.0.0.1:1")
    connections = ServiceConnections(
        channels={"review_detail": channel},
        addresses={"review_detail": "127.0.0.1:1"},
    )
    upload: Any = FakeUpload()
    return ReviewDetailHandler(connections, upload), channel, upload


async def test_handler_builds_query_and_command_stubs() -> None:
    handler, channel, _ = _handler()
    try:
        assert handler._query is not None
        assert handler._command is not None
    finally:
        await channel.close()


async def test_create_rejects_non_positive_review_id() -> None:
    handler, channel, _ = _handler()
    try:
        with pytest.raises(AppError) as excinfo:
            await handler.create(0, "photo", "/a.png", "cap")
        assert excinfo.value.code == 400
        assert excinfo.value.message == "Invalid Review ID"
    finally:
        await channel.close()


async def test_create_rejects_empty_type() -> None:
    handler, channel, _ = _handler()
    try:
        with pytest.raises(AppError) as excinfo:
            await handler.create(1, "  ", "/a.png", "cap")
        assert excinfo.value.code == 400
        assert excinfo.value.message == "Type is required"
    finally:
        await channel.close()


async def test_create_rejects_empty_caption() -> None:
    handler, channel, _ = _handler()
    try:
        with pytest.raises(AppError) as excinfo:
            await handler.create(1, "photo", "/a.png", "  ")
        assert excinfo.value.code == 400
        assert excinfo.value.message == "Caption is required"
    finally:
        await channel.close()


async def test_update_rejects_non_positive_id() -> None:
    handler, channel, _ = _handler()
    try:
        with pytest.raises(AppError) as excinfo:
            await handler.update(0, "photo", "/a.png", "cap")
        assert excinfo.value.code == 400
        assert excinfo.value.message == "Invalid ID"
    finally:
        await channel.close()


async def test_create_with_file_uploads_to_review_detail_dir() -> None:
    handler, channel, upload = _handler()
    fake: Any = FakeReviewDetailCommand()
    handler._command = fake
    try:
        await handler.create("3", "photo", FakeFile(), "cap")
        assert upload.calls == [("uploads/review_detail", False)]
        assert fake.last.url == "uploads/review_detail/stored.png"
        assert fake.last.review_id == 3
    finally:
        await channel.close()


async def test_create_with_string_url_skips_upload() -> None:
    handler, channel, upload = _handler()
    fake: Any = FakeReviewDetailCommand()
    handler._command = fake
    try:
        await handler.create("3", "photo", "https://cdn/a.png", "cap")
        assert upload.calls == []
        assert fake.last.url == "https://cdn/a.png"
    finally:
        await channel.close()


async def test_update_with_file_uploads_to_review_detail_dir() -> None:
    handler, channel, upload = _handler()
    fake: Any = FakeReviewDetailCommand()
    handler._command = fake
    try:
        await handler.update(9, "photo", FakeFile(), "cap")
        assert upload.calls == [("uploads/review_detail", False)]
        assert fake.last.url == "uploads/review_detail/stored.png"
    finally:
        await channel.close()


__all__ = []

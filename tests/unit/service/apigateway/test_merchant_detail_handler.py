"""Unit tests for the gateway merchant_detail / merchant_social_link transport handlers. `normalize_pagination` Matches the expected gateway clamp (no `page_size` cap). `require_positive_id` guards command path ids at the gateway with 400 `Invalid ID` (the deliberate cross-domain deviation). The query `find_by_id` route guards with own message `id is required` (BEDA dari merchant, which forwards 0). The social handler rides the `merchant_detail` channel, since `ServiceConnections.MerchantSocial` is never assigned."""

from __future__ import annotations

from typing import Any

import grpc
import pytest

from pb.merchant_detail import merchant_detail_common_pb2
from pb.merchant_social_link import merchant_social_link_common_pb2
from service.apigateway.app.client import ServiceConnections
from service.apigateway.handler.merchant_detail.handler import (
    MerchantDetailHandler,
    normalize_pagination,
    require_positive_id,
)
from service.apigateway.handler.merchant_social_link.handler import (
    MerchantSocialLinkHandler,
)
from shared.errors import AppError


class FakeQuery:
    def __init__(self) -> None:
        self.last: Any = None

    async def FindById(self, request: Any, timeout: float | None = None) -> Any:
        self.last = request
        message = merchant_detail_common_pb2.ApiResponseMerchantDetail(
            status="success", message="Successfully fetched merchant detail"
        )
        message.data.id = request.id
        return message


class FakeCommand:
    def __init__(self) -> None:
        self.last: Any = None

    async def Create(self, request: Any, timeout: float | None = None) -> Any:
        self.last = request
        message = merchant_detail_common_pb2.ApiResponseMerchantDetail(
            status="success", message="Successfully created merchant detail"
        )
        message.data.id = 1
        message.data.merchant_id = request.merchant_id
        return message

    async def Update(self, request: Any, timeout: float | None = None) -> Any:
        self.last = request
        message = merchant_detail_common_pb2.ApiResponseMerchantDetail(
            status="success", message="Successfully updated merchant detail"
        )
        message.data.id = request.merchant_detail_id
        return message

    async def TrashedMerchantDetail(self, request: Any, timeout: float | None = None) -> Any:
        message = merchant_detail_common_pb2.ApiResponseMerchantDetailDeleteAt(
            status="success", message="Successfully trashed merchant detail"
        )
        message.data.id = request.id
        return message


class FakeSocialCommand:
    def __init__(self) -> None:
        self.last: Any = None

    async def Create(self, request: Any, timeout: float | None = None) -> Any:
        self.last = request
        message = merchant_social_link_common_pb2.ApiResponseMerchantSocial(
            status="success", message="Successfully created merchant social link"
        )
        message.data.id = 1
        message.data.merchant_detail_id = request.merchant_detail_id
        message.data.platform = request.platform
        return message

    async def Update(self, request: Any, timeout: float | None = None) -> Any:
        self.last = request
        message = merchant_social_link_common_pb2.ApiResponseMerchantSocial(
            status="success", message="Successfully updated merchant social link"
        )
        message.data.id = request.id
        return message


@pytest.mark.parametrize(
    ("page", "page_size", "expected"),
    [
        (1, 10, (1, 10)),
        (0, 0, (1, 10)),
        (-5, -1, (1, 10)),
        (3, 0, (3, 10)),
        (0, 25, (1, 25)),
        # No page_size cap in the gateway (unlike the request DTO validator).
        (1, 500, (1, 500)),
    ],
)
def test_normalize_pagination(page: int, page_size: int, expected: tuple[int, int]) -> None:
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


def _handler() -> tuple[MerchantDetailHandler, grpc.aio.Channel]:
    channel = grpc.aio.insecure_channel("127.0.0.1:1")
    connections = ServiceConnections(
        channels={"merchant_detail": channel},
        addresses={"merchant_detail": "127.0.0.1:1"},
    )
    return MerchantDetailHandler(connections), channel


def _social_handler() -> tuple[MerchantSocialLinkHandler, grpc.aio.Channel]:
    channel = grpc.aio.insecure_channel("127.0.0.1:1")
    connections = ServiceConnections(
        channels={"merchant_detail": channel},
        addresses={"merchant_detail": "127.0.0.1:1"},
    )
    return MerchantSocialLinkHandler(connections), channel


async def test_handler_builds_query_and_command_stubs() -> None:
    handler, channel = _handler()
    try:
        assert handler._query is not None
        assert handler._command is not None
    finally:
        await channel.close()


async def test_query_find_by_id_rejects_non_positive_with_go_message() -> None:
    handler, channel = _handler()
    try:
        with pytest.raises(AppError) as excinfo:
            await handler.find_by_id(0)
        assert excinfo.value.code == 400
        assert excinfo.value.message == "id is required"
    finally:
        await channel.close()


async def test_query_find_by_id_success_maps_relation() -> None:
    handler, channel = _handler()
    fake: Any = FakeQuery()
    handler._query = fake
    try:
        response = await handler.find_by_id(7)
        assert response.status == "success"
        assert response.data.id == 7
        assert fake.last.id == 7
    finally:
        await channel.close()


async def test_command_update_rejects_non_positive_id() -> None:
    handler, channel = _handler()
    try:
        with pytest.raises(AppError) as excinfo:
            await handler.update(0, "N", "c", "l", "d", "https://x.com")
        assert excinfo.value.code == 400
        assert excinfo.value.message == "Invalid ID"
    finally:
        await channel.close()


async def test_command_trash_rejects_non_positive_id() -> None:
    handler, channel = _handler()
    try:
        with pytest.raises(AppError) as excinfo:
            await handler.trash(0)
        assert excinfo.value.code == 400
        assert excinfo.value.message == "Invalid ID"
    finally:
        await channel.close()


async def test_command_create_success_maps_response() -> None:
    handler, channel = _handler()
    fake: Any = FakeCommand()
    handler._command = fake
    try:
        response = await handler.create(5, "N", "c", "l", "d", "https://x.com")
        assert response.status == "success"
        assert response.data.id == 1
        assert response.data.merchant_id == 5
        assert fake.last.merchant_id == 5
    finally:
        await channel.close()


async def test_command_update_success_maps_response() -> None:
    handler, channel = _handler()
    handler._command = FakeCommand()
    try:
        response = await handler.update(7, "N", "c", "l", "d", "https://x.com")
        assert response.data.id == 7
    finally:
        await channel.close()


async def test_command_trash_success_maps_delete_at() -> None:
    handler, channel = _handler()
    handler._command = FakeCommand()
    try:
        response = await handler.trash(3)
        assert response.status == "success"
        assert response.data.id == 3
    finally:
        await channel.close()


async def test_social_handler_uses_merchant_detail_channel() -> None:
    handler, channel = _social_handler()
    try:
        assert handler._command is not None
    finally:
        await channel.close()


async def test_social_update_rejects_non_positive_id() -> None:
    handler, channel = _social_handler()
    try:
        with pytest.raises(AppError) as excinfo:
            await handler.update(0, 1, "Facebook", "https://facebook.com/x")
        assert excinfo.value.code == 400
        assert excinfo.value.message == "Invalid ID"
    finally:
        await channel.close()


async def test_social_create_success_maps_response() -> None:
    handler, channel = _social_handler()
    fake: Any = FakeSocialCommand()
    handler._command = fake
    try:
        response = await handler.create(1, "Facebook", "https://facebook.com/x")
        assert response.status == "success"
        assert response.data.id == 1
        assert response.data.platform == "Facebook"
        assert fake.last.merchant_detail_id == 1
    finally:
        await channel.close()


async def test_social_update_success_maps_response() -> None:
    handler, channel = _social_handler()
    handler._command = FakeSocialCommand()
    try:
        response = await handler.update(5, 1, "Twitter", "https://twitter.com/x")
        assert response.data.id == 5
    finally:
        await channel.close()


__all__ = []

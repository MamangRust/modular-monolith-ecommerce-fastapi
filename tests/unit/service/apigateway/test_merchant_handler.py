"""Unit tests for the gateway merchant transport handler. `normalize_pagination` Matches the expected gateway clamp (no `page_size` cap). `require_positive_id` guards command path ids at the gateway with 400 `Invalid ID` (a deliberate cross-domain deviation — only guards the parse error). The query `find_by_id` route does NOT guard (it forwards 0 so the gRPC handler answers `invalid merchant ID`). `Create`/`Update` require a JWT subject and raise 401 when it is missing."""

from __future__ import annotations

from typing import Any

import grpc
import pytest

from pb.merchant import merchant_common_pb2
from service.apigateway.app.client import ServiceConnections
from service.apigateway.handler.merchant.handler import (
    MerchantHandler,
    normalize_pagination,
    require_positive_id,
)
from shared.errors import AppError


class FakeCommand:
    def __init__(self) -> None:
        self.last: Any = None

    async def Create(self, request: Any, timeout: float | None = None) -> Any:
        self.last = request
        message = merchant_common_pb2.ApiResponseMerchant(
            status="success", message="Successfully created merchant"
        )
        message.data.id = 1
        message.data.user_id = request.user_id
        message.data.name = request.name
        return message

    async def Update(self, request: Any, timeout: float | None = None) -> Any:
        self.last = request
        message = merchant_common_pb2.ApiResponseMerchant(
            status="success", message="Successfully updated merchant"
        )
        message.data.id = request.merchant_id
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


def _handler() -> tuple[MerchantHandler, grpc.aio.Channel]:
    channel = grpc.aio.insecure_channel("127.0.0.1:1")
    connections = ServiceConnections(
        channels={"merchant": channel}, addresses={"merchant": "127.0.0.1:1"}
    )
    return MerchantHandler(connections), channel


async def test_handler_builds_query_and_command_stubs() -> None:
    handler, channel = _handler()
    try:
        assert handler._query is not None
        assert handler._command is not None
    finally:
        await channel.close()


async def test_create_requires_jwt_subject() -> None:
    handler, channel = _handler()
    try:
        for user_id in (None, 0, -1):
            with pytest.raises(AppError) as excinfo:
                await handler.create(user_id, "N", "d", "a", "e@f.com", "0812", "active")
            assert excinfo.value.code == 401
    finally:
        await channel.close()


async def test_update_requires_jwt_subject() -> None:
    handler, channel = _handler()
    try:
        with pytest.raises(AppError) as excinfo:
            await handler.update(1, None, "N", "d", "a", "e@f.com", "0812", "active")
        assert excinfo.value.code == 401
    finally:
        await channel.close()


async def test_update_rejects_non_positive_id() -> None:
    handler, channel = _handler()
    try:
        with pytest.raises(AppError) as excinfo:
            await handler.update(0, 5, "N", "d", "a", "e@f.com", "0812", "active")
        assert excinfo.value.code == 400
        assert excinfo.value.message == "Invalid ID"
    finally:
        await channel.close()


async def test_create_success_maps_response() -> None:
    handler, channel = _handler()
    fake: Any = FakeCommand()
    handler._command = fake
    try:
        response = await handler.create(
            5, "N", "d", "a", "e@f.com", "0812", "active"
        )
        assert response.status == "success"
        assert response.data.id == 1
        assert response.data.user_id == 5
        assert fake.last.user_id == 5
    finally:
        await channel.close()


async def test_update_success_maps_response() -> None:
    handler, channel = _handler()
    handler._command = FakeCommand()
    try:
        response = await handler.update(
            7, 5, "N", "d", "a", "e@f.com", "0812", "active"
        )
        assert response.data.id == 7
    finally:
        await channel.close()


__all__ = []

"""Unit tests for the gateway shipping address transport helpers. `require_positive_id` Matches the expected gateway's `strconv.Atoi` + `<= 0` guard: a bad path id must fail at the gateway with `BAD_REQUEST` before any gRPC hop, using `"Invalid ID"` for both the by-id and by-order routes (uses that same message for both)."""

from __future__ import annotations

import grpc
import pytest

from service.apigateway.app.client import ServiceConnections
from service.apigateway.handler.shipping_address.handler import (
    ShippingAddressHandler,
    normalize_pagination,
    require_positive_id,
)
from shared.errors import AppError


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


async def test_handler_builds_query_and_command_stubs() -> None:
    channel = grpc.aio.insecure_channel("127.0.0.1:1")
    try:
        connections = ServiceConnections(
            channels={"shipping_address": channel},
            addresses={"shipping_address": "127.0.0.1:1"},
        )
        handler = ShippingAddressHandler(connections)
        assert handler._query is not None
        assert handler._command is not None
    finally:
        await channel.close()

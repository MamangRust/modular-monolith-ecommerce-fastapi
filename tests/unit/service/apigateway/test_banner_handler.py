"""Unit tests for the gateway banner transport helpers.

`require_positive_id` Matches the expected banner gateway's `strconv.Atoi` +
`<= 0` guard: a bad path id must fail at the gateway with `BAD_REQUEST`
and the message `"Invalid ID"` before any gRPC hop."""

from __future__ import annotations

import pytest

from service.apigateway.handler.banner.handler import (
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

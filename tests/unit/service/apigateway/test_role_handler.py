"""Unit tests for the gateway role transport helpers."""

from __future__ import annotations

import pytest

from service.apigateway.handler.role.handler import normalize_pagination, require_positive_id
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
        require_positive_id(value, "id")

    assert excinfo.value.code == 400
    assert excinfo.value.type == "BAD_REQUEST"
    assert excinfo.value.message == "id is required"


def test_require_positive_id_names_the_field() -> None:
    with pytest.raises(AppError) as excinfo:
        require_positive_id(0, "user_id")

    assert excinfo.value.message == "user_id is required"


@pytest.mark.parametrize("value", [1, 42])
def test_require_positive_id_accepts_positive(value: int) -> None:
    require_positive_id(value, "id")

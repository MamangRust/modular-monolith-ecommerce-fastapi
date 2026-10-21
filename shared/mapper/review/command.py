"""Review command-side REST mappers."""

from __future__ import annotations

from typing import Any

from shared.domain.response.responses import ApiResponse
from shared.domain.response.review import ReviewResponseDeleteAt
from shared.domain.response.review import (
    to_api_response_review_all as _to_all,
)
from shared.domain.response.review import (
    to_api_response_review_delete as _to_delete,
)
from shared.mapper.review.mapper import map_review_response_delete_at


def to_api_response_review_delete_at(pb: Any) -> ApiResponse[ReviewResponseDeleteAt]:
    return ApiResponse[ReviewResponseDeleteAt](
        status=pb.status,
        message=pb.message,
        data=map_review_response_delete_at(pb.data),
    )


def to_api_response_review_delete(pb: Any) -> ApiResponse[None]:
    return _to_delete(pb)


def to_api_response_review_all(pb: Any) -> ApiResponse[None]:
    return _to_all(pb)


__all__ = [
    "to_api_response_review_all",
    "to_api_response_review_delete",
    "to_api_response_review_delete_at",
]

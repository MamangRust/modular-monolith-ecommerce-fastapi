"""User command response mapping. Delete/permanent/restore-all envelopes carry no `data`, so they render as `data: null` exactly like the pointer-free structs."""

from __future__ import annotations

from typing import Any

from shared.domain.response.responses import ApiResponse
from shared.domain.response.user import UserResponse, UserResponseDeleteAt
from shared.mapper.user.query import _map_user, _map_user_delete_at


def to_api_response_user(pb: Any) -> ApiResponse[UserResponse]:
    return ApiResponse[UserResponse](
        status=pb.status,
        message=pb.message,
        data=_map_user(pb.data),
    )


def to_api_response_user_delete_at(pb: Any) -> ApiResponse[UserResponseDeleteAt]:
    return ApiResponse[UserResponseDeleteAt](
        status=pb.status,
        message=pb.message,
        data=_map_user_delete_at(pb.data),
    )


def to_api_response_user_delete(pb: Any) -> ApiResponse[None]:
    return ApiResponse[None](status=pb.status, message=pb.message, data=None)


def to_api_response_user_all(pb: Any) -> ApiResponse[None]:
    return ApiResponse[None](status=pb.status, message=pb.message, data=None)


__all__ = [
    "to_api_response_user",
    "to_api_response_user_all",
    "to_api_response_user_delete",
    "to_api_response_user_delete_at",
]

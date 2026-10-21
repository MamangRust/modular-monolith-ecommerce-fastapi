"""User query response mapping. Deviation from (recorded in the matrix): `ToResponseUserDeleteAt` builds `deletedAt string` and always sets `DeletedAt: &deletedAt`, so an active row serialises `"deleted_at": ""` (despite the struct comment saying "nil if active"). renders `null` instead, which matches the struct's documented intent and the role mapper's handling of the same."""

from __future__ import annotations

from typing import Any

from shared.domain.response.responses import (
    ApiResponse,
    APIResponsePagination,
    PaginationMeta,
)
from shared.domain.response.user import UserResponse, UserResponseDeleteAt


def map_pagination_meta(meta: Any) -> PaginationMeta:
    if meta is None:
        return PaginationMeta()
    return PaginationMeta(
        current_page=int(meta.current_page),
        page_size=int(meta.page_size),
        total_pages=int(meta.total_pages),
        total_records=int(meta.total_records),
    )


def _map_user(pb: Any) -> UserResponse:
    return UserResponse(
        id=int(pb.id),
        firstname=pb.firstname,
        lastname=pb.lastname,
        email=pb.email,
        is_verified=False,
        created_at=pb.created_at,
        updated_at=pb.updated_at,
    )


def _map_user_delete_at(pb: Any) -> UserResponseDeleteAt:
    deleted_at = pb.deleted_at.value if pb.HasField("deleted_at") else None
    return UserResponseDeleteAt(
        id=int(pb.id),
        firstname=pb.firstname,
        lastname=pb.lastname,
        email=pb.email,
        is_verified=False,
        created_at=pb.created_at,
        updated_at=pb.updated_at,
        deleted_at=deleted_at,
    )


def to_api_response_user(pb: Any) -> ApiResponse[UserResponse]:
    return ApiResponse[UserResponse](
        status=pb.status,
        message=pb.message,
        data=_map_user(pb.data),
    )


def to_api_responses_user(pb: Any) -> ApiResponse[list[UserResponse]]:
    return ApiResponse[list[UserResponse]](
        status=pb.status,
        message=pb.message,
        data=[_map_user(item) for item in pb.data],
    )


def to_api_response_user_delete_at(pb: Any) -> ApiResponse[UserResponseDeleteAt]:
    return ApiResponse[UserResponseDeleteAt](
        status=pb.status,
        message=pb.message,
        data=_map_user_delete_at(pb.data),
    )


def to_api_response_pagination_user(
    pb: Any,
) -> APIResponsePagination[list[UserResponse]]:
    return APIResponsePagination[list[UserResponse]](
        status=pb.status,
        message=pb.message,
        data=[_map_user(item) for item in pb.data],
        pagination=map_pagination_meta(pb.pagination),
    )


def to_api_response_pagination_user_delete_at(
    pb: Any,
) -> APIResponsePagination[list[UserResponseDeleteAt]]:
    return APIResponsePagination[list[UserResponseDeleteAt]](
        status=pb.status,
        message=pb.message,
        data=[_map_user_delete_at(item) for item in pb.data],
        pagination=map_pagination_meta(pb.pagination),
    )


__all__ = [
    "map_pagination_meta",
    "to_api_response_pagination_user",
    "to_api_response_pagination_user_delete_at",
    "to_api_response_user",
    "to_api_response_user_delete_at",
    "to_api_responses_user",
]

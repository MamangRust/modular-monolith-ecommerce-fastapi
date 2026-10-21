"""Role query response mapping. Timestamps pass through unchanged: the gRPC handlers already format them as `YYYY-MM-DD`, and the mapper must not re-format or the wire behaviour would drift from the reference."""

from __future__ import annotations

from typing import Any

from shared.domain.response.responses import (
    ApiResponse,
    APIResponsePagination,
    PaginationMeta,
)
from shared.domain.response.role import RoleResponse, RoleResponseDeleteAt


def map_pagination_meta(meta: Any) -> PaginationMeta:
    if meta is None:
        return PaginationMeta()
    return PaginationMeta(
        current_page=int(meta.current_page),
        page_size=int(meta.page_size),
        total_pages=int(meta.total_pages),
        total_records=int(meta.total_records),
    )


def _map_role(pb: Any) -> RoleResponse:
    return RoleResponse(
        id=int(pb.id),
        name=pb.name,
        created_at=pb.created_at,
        updated_at=pb.updated_at,
    )


def _map_role_delete_at(pb: Any) -> RoleResponseDeleteAt:
    # always sets the pointer, so an absent wrapper renders as "".
    deleted_at = pb.deleted_at.value if pb.HasField("deleted_at") else ""
    return RoleResponseDeleteAt(
        id=int(pb.id),
        name=pb.name,
        created_at=pb.created_at,
        updated_at=pb.updated_at,
        deleted_at=deleted_at,
    )


def to_api_response_role(pb: Any) -> ApiResponse[RoleResponse]:
    return ApiResponse[RoleResponse](
        status=pb.status,
        message=pb.message,
        data=_map_role(pb.data),
    )


def to_api_responses_role(pb: Any) -> ApiResponse[list[RoleResponse]]:
    return ApiResponse[list[RoleResponse]](
        status=pb.status,
        message=pb.message,
        data=[_map_role(item) for item in pb.data],
    )


def to_api_response_pagination_role(
    pb: Any,
) -> APIResponsePagination[list[RoleResponse]]:
    return APIResponsePagination[list[RoleResponse]](
        status=pb.status,
        message=pb.message,
        data=[_map_role(item) for item in pb.data],
        pagination=map_pagination_meta(pb.pagination),
    )


def to_api_response_pagination_role_delete_at(
    pb: Any,
) -> APIResponsePagination[list[RoleResponseDeleteAt]]:
    return APIResponsePagination[list[RoleResponseDeleteAt]](
        status=pb.status,
        message=pb.message,
        data=[_map_role_delete_at(item) for item in pb.data],
        pagination=map_pagination_meta(pb.pagination),
    )


__all__ = [
    "map_pagination_meta",
    "to_api_response_pagination_role",
    "to_api_response_pagination_role_delete_at",
    "to_api_response_role",
    "to_api_responses_role",
]

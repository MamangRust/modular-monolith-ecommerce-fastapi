"""User response DTOs. the structs carry `is_verified`, but the user gRPC contract does not, so the mapper always renders it as `false` — the field is kept here to preserve the REST wire shape exactly."""

from __future__ import annotations

from dataclasses import dataclass

from shared.domain.response.responses import (
    ApiResponse,
    APIResponsePagination,
    PaginationMeta,
)


@dataclass
class UserResponse:
    id: int
    firstname: str
    lastname: str
    email: str
    is_verified: bool
    created_at: str
    updated_at: str


@dataclass
class UserResponseDeleteAt:
    id: int
    firstname: str
    lastname: str
    email: str
    is_verified: bool
    created_at: str
    updated_at: str
    deleted_at: str | None = None


# API response wrappers (kept close to the names) ----

UserResponseAll = ApiResponse[None]
UserResponseDelete = ApiResponse[None]
UserResponseApi = ApiResponse[UserResponse]
UserResponseDeleteAtApi = ApiResponse[UserResponseDeleteAt]
UserResponses = ApiResponse[list[UserResponse]]
UserResponsePagination = APIResponsePagination[list[UserResponse]]
UserResponsePaginationDeleteAt = APIResponsePagination[list[UserResponseDeleteAt]]


def pagination_meta(page: int, page_size: int, total_records: int) -> PaginationMeta:
    import math

    total_pages = math.ceil(total_records / page_size) if page_size else 0
    return PaginationMeta(
        current_page=page,
        page_size=page_size,
        total_pages=total_pages,
        total_records=total_records,
    )


__all__ = [
    "UserResponse",
    "UserResponseAll",
    "UserResponseApi",
    "UserResponseDelete",
    "UserResponseDeleteAt",
    "UserResponseDeleteAtApi",
    "UserResponsePagination",
    "UserResponsePaginationDeleteAt",
    "UserResponses",
    "pagination_meta",
]

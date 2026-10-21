"""Role response DTOs. Timestamps use the same `YYYY-MM-DD` shape the gRPC handlers emit (CreatedAt/UpdatedAt formatted as "2006-01-02"), so gateway mapping can Matches the expected wire behaviour exactly."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime

from shared.domain.response.responses import (
    ApiResponse,
    APIResponsePagination,
    PaginationMeta,
)


@dataclass
class RoleResponsePayload:
    """Kafka reply shape."""

    correlation_id: str
    valid: bool
    role_names: list[str]

    def to_dict(self) -> dict:
        return {
            "correlation_id": self.correlation_id,
            "valid": self.valid,
            "role_names": list(self.role_names),
        }

    @staticmethod
    def from_dict(data: dict) -> RoleResponsePayload:
        return RoleResponsePayload(
            correlation_id=str(data.get("correlation_id", "")),
            valid=bool(data.get("valid", False)),
            role_names=[str(name) for name in (data.get("role_names") or [])],
        )


def _fmt(ts: datetime | None) -> str | None:
    return ts.strftime("%Y-%m-%d") if ts else None


@dataclass
class RoleResponse:
    id: int
    name: str
    created_at: str
    updated_at: str


@dataclass
class RoleResponseDeleteAt:
    id: int
    name: str
    created_at: str
    updated_at: str
    deleted_at: str | None = None


# API response wrappers (kept close to the names) ----

RoleResponseAll = ApiResponse[None]
RoleResponseDelete = ApiResponse[None]
RoleResponseApi = ApiResponse[RoleResponse]
RoleResponseDeleteAtApi = ApiResponse[RoleResponseDeleteAt]
RoleResponses = ApiResponse[list[RoleResponse]]
RoleResponsePagination = APIResponsePagination[list[RoleResponse]]
RoleResponsePaginationDeleteAt = APIResponsePagination[list[RoleResponseDeleteAt]]


def pagination_meta(
    page: int, page_size: int, total_records: int
) -> PaginationMeta:
    import math

    total_pages = math.ceil(total_records / page_size) if page_size else 0
    return PaginationMeta(
        current_page=page,
        page_size=page_size,
        total_pages=total_pages,
        total_records=total_records,
    )

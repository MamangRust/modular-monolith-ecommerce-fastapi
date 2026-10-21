"""Role command response mapping. Delete/restore-all responses carry no `data`, so the envelope renders as `data: null` exactly like the pointer-based structs."""

from __future__ import annotations

from typing import Any

from shared.domain.response.responses import ApiResponse


def to_api_response_role_delete(pb: Any) -> ApiResponse[None]:
    return ApiResponse[None](status=pb.status, message=pb.message, data=None)


def to_api_response_role_all(pb: Any) -> ApiResponse[None]:
    return ApiResponse[None](status=pb.status, message=pb.message, data=None)


__all__ = [
    "to_api_response_role_all",
    "to_api_response_role_delete",
]

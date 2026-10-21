"""Role query gRPC handler. Timestamps are emitted as `YYYY-MM-DD` because that is what the handlers produce, and the gateway mapper passes them through unchanged. Deviation from (recorded in the matrix): for active rows formatted a NULL `deleted_at` as `"0001-01-01"`; omits the wrapper instead, so the gateway maps it to an empty string."""

from __future__ import annotations

import math
from typing import Any

from google.protobuf import wrappers_pb2

from pb.common import api_pb2 as common_pb2
from pb.role import role_common_pb2, role_query_pb2_grpc
from pkg.logger.logger import Logger
from pkg.middleware import grpc_method
from service.role.service.interfaces import RoleQueryService
from service.role.service.service import SERVICE_NAME
from shared.errors import err_grpc_role_invalid_id, err_grpc_role_invalid_name

_DATE_LAYOUT = "%Y-%m-%d"


def _date(value: Any) -> str:
    return value.strftime(_DATE_LAYOUT) if value else ""


def _fill_role(message: Any, role: Any) -> None:
    message.id = role.role_id
    message.name = role.role_name
    message.created_at = _date(role.created_at)
    message.updated_at = _date(role.updated_at)


def _fill_role_delete_at(message: Any, role: Any) -> None:
    _fill_role(message, role)
    if role.deleted_at is not None:
        message.deleted_at.CopyFrom(wrappers_pb2.StringValue(value=_date(role.deleted_at)))


def _total_pages(total: int, page_size: int) -> int:
    return math.ceil(total / page_size) if page_size else 0


def _normalize(page: int, page_size: int) -> tuple[int, int]:
    if page <= 0:
        page = 1
    if page_size <= 0:
        page_size = 10
    return page, page_size


class RoleQueryHandler(role_query_pb2_grpc.RoleQueryServiceServicer):
    def __init__(self, service: RoleQueryService, logger: Logger) -> None:
        self._service = service
        self.logger = logger

    @grpc_method("RoleService.FindAllRole", SERVICE_NAME)
    async def FindAllRole(self, request: Any, context: Any) -> Any:
        page, page_size = _normalize(request.page, request.page_size)
        rows, total = await self._service.find_all(request.search, page, page_size)
        response = role_common_pb2.ApiResponsePaginationRole(
            status="success", message="Successfully fetch all roles"
        )
        for row in rows:
            _fill_role(response.data.add(), row)
        response.pagination.CopyFrom(
            common_pb2.PaginationMeta(
                current_page=page,
                page_size=page_size,
                total_pages=_total_pages(total, page_size),
                total_records=total,
            )
        )
        return response

    @grpc_method("RoleService.FindByIdRole", SERVICE_NAME)
    async def FindByIdRole(self, request: Any, context: Any) -> Any:
        if request.role_id <= 0:
            raise err_grpc_role_invalid_id
        role = await self._service.find_by_id(request.role_id)
        response = role_common_pb2.ApiResponseRole(
            status="success", message="Successfully fetch role"
        )
        _fill_role(response.data, role)
        return response

    @grpc_method("RoleService.FindByNameRole", SERVICE_NAME)
    async def FindByNameRole(self, request: Any, context: Any) -> Any:
        if not request.name:
            raise err_grpc_role_invalid_name
        role = await self._service.find_by_name(request.name)
        response = role_common_pb2.ApiResponseRole(
            status="success", message="Successfully fetched role by name"
        )
        _fill_role(response.data, role)
        return response

    @grpc_method("RoleService.FindByActive", SERVICE_NAME)
    async def FindByActive(self, request: Any, context: Any) -> Any:
        page, page_size = _normalize(request.page, request.page_size)
        rows, total = await self._service.find_active(request.search, page, page_size)
        response = role_common_pb2.ApiResponsePaginationRoleDeleteAt(
            status="success", message="Successfully fetch active roles"
        )
        for row in rows:
            _fill_role_delete_at(response.data.add(), row)
        response.pagination.CopyFrom(
            common_pb2.PaginationMeta(
                current_page=page,
                page_size=page_size,
                total_pages=_total_pages(total, page_size),
                total_records=total,
            )
        )
        return response

    @grpc_method("RoleService.FindByTrashed", SERVICE_NAME)
    async def FindByTrashed(self, request: Any, context: Any) -> Any:
        page, page_size = _normalize(request.page, request.page_size)
        rows, total = await self._service.find_trashed(request.search, page, page_size)
        response = role_common_pb2.ApiResponsePaginationRoleDeleteAt(
            status="success", message="Successfully fetch trashed roles"
        )
        for row in rows:
            _fill_role_delete_at(response.data.add(), row)
        response.pagination.CopyFrom(
            common_pb2.PaginationMeta(
                current_page=page,
                page_size=page_size,
                total_pages=_total_pages(total, page_size),
                total_records=total,
            )
        )
        return response

    @grpc_method("RoleService.FindByUserId", SERVICE_NAME)
    async def FindByUserId(self, request: Any, context: Any) -> Any:
        if request.user_id <= 0:
            raise err_grpc_role_invalid_id
        roles = await self._service.find_by_user_id(request.user_id)
        response = role_common_pb2.ApiResponsesRole(
            status="success", message="Successfully fetch roles by user id"
        )
        for role in roles:
            _fill_role(response.data.add(), role)
        return response


__all__ = ["RoleQueryHandler"]

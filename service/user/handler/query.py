"""User query gRPC handler. Timestamps are emitted as RFC3339 because that is what the handlers produce (`time.RFC3339`) and the gateway mapper passes them through unchanged. Note this differs from the role service, which formats dates only — both mirror their respective references. Deviation from (recorded in the matrix): always attaches a `deleted_at` wrapper, so an active row renders the zero time. omits the wrapper when `deleted_at` is null, matching the role handler."""

from __future__ import annotations

import math
from typing import Any

from google.protobuf import wrappers_pb2

from pb.common import api_pb2 as common_pb2
from pb.user import user_common_pb2, user_query_pb2_grpc
from pkg.logger.logger import Logger
from pkg.middleware import grpc_method
from service.user.service.interfaces import UserQueryService
from service.user.service.service import SERVICE_NAME
from shared.errors import err_grpc_user_invalid_id


def rfc3339(value: Any) -> str:
    """Format a DB timestamp the way `time.RFC3339` does."""
    if value is None:
        return ""
    if value.tzinfo is None:
        return value.strftime("%Y-%m-%dT%H:%M:%SZ")
    return value.isoformat()


def _fill_user(message: Any, user: Any) -> None:
    message.id = user.user_id
    message.firstname = user.firstname
    message.lastname = user.lastname
    message.email = user.email
    message.created_at = rfc3339(user.created_at)
    message.updated_at = rfc3339(user.updated_at)


def _fill_user_delete_at(message: Any, user: Any) -> None:
    _fill_user(message, user)
    if user.deleted_at is not None:
        message.deleted_at.CopyFrom(
            wrappers_pb2.StringValue(value=rfc3339(user.deleted_at))
        )


def _total_pages(total: int, page_size: int) -> int:
    return math.ceil(total / page_size) if page_size else 0


def _normalize(page: int, page_size: int) -> tuple[int, int]:
    if page <= 0:
        page = 1
    if page_size <= 0:
        page_size = 10
    return page, page_size


def _pagination(page: int, page_size: int, total: int) -> Any:
    return common_pb2.PaginationMeta(
        current_page=page,
        page_size=page_size,
        total_pages=_total_pages(total, page_size),
        total_records=total,
    )


class UserQueryHandler(user_query_pb2_grpc.UserQueryServiceServicer):
    def __init__(self, service: UserQueryService, logger: Logger) -> None:
        self._service = service
        self.logger = logger

    @grpc_method("UserQueryService.FindAll", SERVICE_NAME)
    async def FindAll(self, request: Any, context: Any) -> Any:
        page, page_size = _normalize(request.page, request.page_size)
        users, total = await self._service.find_all(request.search, page, page_size)
        response = user_common_pb2.ApiResponsePaginationUser(
            status="success", message="Successfully fetched users"
        )
        for user in users:
            _fill_user(response.data.add(), user)
        response.pagination.CopyFrom(_pagination(page, page_size, total))
        return response

    @grpc_method("UserQueryService.FindById", SERVICE_NAME)
    async def FindById(self, request: Any, context: Any) -> Any:
        if request.id <= 0:
            raise err_grpc_user_invalid_id
        user = await self._service.find_by_id(request.id)
        response = user_common_pb2.ApiResponseUser(
            status="success", message="Successfully fetched user"
        )
        _fill_user(response.data, user)
        return response

    @grpc_method("UserQueryService.FindByActive", SERVICE_NAME)
    async def FindByActive(self, request: Any, context: Any) -> Any:
        page, page_size = _normalize(request.page, request.page_size)
        users, total = await self._service.find_active(request.search, page, page_size)
        response = user_common_pb2.ApiResponsePaginationUserDeleteAt(
            status="success", message="Successfully fetched active users"
        )
        for user in users:
            _fill_user_delete_at(response.data.add(), user)
        response.pagination.CopyFrom(_pagination(page, page_size, total))
        return response

    @grpc_method("UserQueryService.FindByTrashed", SERVICE_NAME)
    async def FindByTrashed(self, request: Any, context: Any) -> Any:
        page, page_size = _normalize(request.page, request.page_size)
        users, total = await self._service.find_trashed(request.search, page, page_size)
        response = user_common_pb2.ApiResponsePaginationUserDeleteAt(
            status="success", message="Successfully fetched trashed users"
        )
        for user in users:
            _fill_user_delete_at(response.data.add(), user)
        response.pagination.CopyFrom(_pagination(page, page_size, total))
        return response


__all__ = ["UserQueryHandler", "rfc3339"]

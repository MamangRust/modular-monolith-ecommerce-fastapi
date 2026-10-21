"""Category query gRPC handler. Pagination clamps match (page <= 0 -> 1, page_size <= 0 -> 10). Unlike the banner/role handlers, `FindById` rejects only `id == 0` (checks `if id == 0`), so a negative id is passed through to the repository."""

from __future__ import annotations

import math
from typing import Any

from pb.category import category_common_pb2, category_query_pb2_grpc
from pb.common import api_pb2 as common_pb2
from pkg.logger.logger import Logger
from pkg.middleware import grpc_method
from service.category.handler.mapping import (
    fill_category_response,
    fill_category_response_delete_at,
)
from service.category.service.interfaces import CategoryQueryService
from service.category.service.service import SERVICE_NAME
from shared.errors import (
    err_grpc_category_invalid_id,
    err_grpc_category_not_found,
    err_grpc_find_all_category,
)


def _normalize(page: int, page_size: int) -> tuple[int, int]:
    if page <= 0:
        page = 1
    if page_size <= 0:
        page_size = 10
    return page, page_size


def _total_pages(total: int, page_size: int) -> int:
    return math.ceil(total / page_size) if page_size else 0


def _pagination(page: int, page_size: int, total: int) -> Any:
    return common_pb2.PaginationMeta(
        current_page=page,
        page_size=page_size,
        total_pages=_total_pages(total, page_size),
        total_records=total,
    )


class CategoryQueryHandler(category_query_pb2_grpc.CategoryQueryServiceServicer):
    def __init__(self, service: CategoryQueryService, logger: Logger) -> None:
        self._service = service
        self.logger = logger

    @grpc_method("CategoryQueryService.FindAll", SERVICE_NAME)
    async def FindAll(self, request: Any, context: Any) -> Any:
        page, page_size = _normalize(request.page, request.page_size)
        try:
            categories, total = await self._service.find_all(
                request.search, page, page_size
            )
        except Exception as exc:  # noqa: BLE001 - collapses to one grpc error
            self.logger.error(f"Failed to find all categories: {exc}")
            raise err_grpc_find_all_category from exc

        response = category_common_pb2.ApiResponsePaginationCategory(
            status="success", message="Successfully fetched categories"
        )
        for category in categories:
            fill_category_response(response.data.add(), category)
        response.pagination.CopyFrom(_pagination(page, page_size, total))
        return response

    @grpc_method("CategoryQueryService.FindById", SERVICE_NAME)
    async def FindById(self, request: Any, context: Any) -> Any:
        if request.id == 0:
            raise err_grpc_category_invalid_id
        try:
            category = await self._service.find_by_id(request.id)
        except Exception as exc:  # noqa: BLE001 - maps any error to NotFound
            self.logger.error(f"Failed to find category by ID: {exc}")
            raise err_grpc_category_not_found from exc

        response = category_common_pb2.ApiResponseCategory(
            status="success", message="Successfully fetched category"
        )
        fill_category_response(response.data, category)
        return response

    @grpc_method("CategoryQueryService.FindByActive", SERVICE_NAME)
    async def FindByActive(self, request: Any, context: Any) -> Any:
        page, page_size = _normalize(request.page, request.page_size)
        try:
            categories, total = await self._service.find_active(
                request.search, page, page_size
            )
        except Exception as exc:  # noqa: BLE001 - collapses to one grpc error
            self.logger.error(f"Failed to find active categories: {exc}")
            raise err_grpc_find_all_category from exc

        response = category_common_pb2.ApiResponsePaginationCategoryDeleteAt(
            status="success", message="Successfully fetched active categories"
        )
        for category in categories:
            fill_category_response_delete_at(response.data.add(), category)
        response.pagination.CopyFrom(_pagination(page, page_size, total))
        return response

    @grpc_method("CategoryQueryService.FindByTrashed", SERVICE_NAME)
    async def FindByTrashed(self, request: Any, context: Any) -> Any:
        page, page_size = _normalize(request.page, request.page_size)
        try:
            categories, total = await self._service.find_trashed(
                request.search, page, page_size
            )
        except Exception as exc:  # noqa: BLE001 - collapses to one grpc error
            self.logger.error(f"Failed to find trashed categories: {exc}")
            raise err_grpc_find_all_category from exc

        response = category_common_pb2.ApiResponsePaginationCategoryDeleteAt(
            status="success", message="Successfully fetched trashed categories"
        )
        for category in categories:
            fill_category_response_delete_at(response.data.add(), category)
        response.pagination.CopyFrom(_pagination(page, page_size, total))
        return response


__all__ = ["CategoryQueryHandler"]

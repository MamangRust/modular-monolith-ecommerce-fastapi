"""Shipping address query gRPC handler. Pagination clamps match (page <= 0 -> 1, page_size <= 0 -> 10). Failures propagate as `AppError` and the `@grpc_method` decorator maps them exactly as `errors.ToGrpcError` does. `FindById`/`FindByOrder` guard `id == 0` and raise the bare `ErrGrpcInvalidID` (400); `FindAll`/`FindByActive`/`FindByTrashed` perform no id guard."""

from __future__ import annotations

import math
from typing import Any

from pb.common import api_pb2 as common_pb2
from pb.shipping_address import (
    shipping_address_common_pb2,
    shipping_address_query_pb2_grpc,
)
from pkg.logger.logger import Logger
from pkg.middleware import grpc_method
from service.shipping_address.handler.mapping import (
    fill_shipping_response,
    fill_shipping_response_delete_at,
)
from service.shipping_address.service.interfaces import ShippingAddressQueryService
from service.shipping_address.service.service import SERVICE_NAME
from shared.errors.shipping_address_errors import err_grpc_invalid_id


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


class ShippingQueryHandler(
    shipping_address_query_pb2_grpc.ShippingQueryServiceServicer
):
    def __init__(self, service: ShippingAddressQueryService, logger: Logger) -> None:
        self._service = service
        self.logger = logger

    @grpc_method("ShippingQueryService.FindAll", SERVICE_NAME)
    async def FindAll(self, request: Any, context: Any) -> Any:
        page, page_size = _normalize(request.page, request.page_size)
        rows, total = await self._service.find_all(request.search, page, page_size)

        response = shipping_address_common_pb2.ApiResponsePaginationShipping(
            status="success", message="Successfully fetched shipping addresses"
        )
        for row in rows:
            fill_shipping_response(response.data.add(), row)
        response.pagination.CopyFrom(_pagination(page, page_size, total))
        return response

    @grpc_method("ShippingQueryService.FindById", SERVICE_NAME)
    async def FindById(self, request: Any, context: Any) -> Any:
        if request.id == 0:
            raise err_grpc_invalid_id
        row = await self._service.find_by_id(int(request.id))

        response = shipping_address_common_pb2.ApiResponseShipping(
            status="success", message="Successfully fetched shipping address"
        )
        fill_shipping_response(response.data, row)
        return response

    @grpc_method("ShippingQueryService.FindByOrder", SERVICE_NAME)
    async def FindByOrder(self, request: Any, context: Any) -> Any:
        if request.id == 0:
            raise err_grpc_invalid_id
        row = await self._service.find_by_order(int(request.id))

        response = shipping_address_common_pb2.ApiResponseShipping(
            status="success",
            message="Successfully fetched shipping address by order ID",
        )
        fill_shipping_response(response.data, row)
        return response

    @grpc_method("ShippingQueryService.FindByActive", SERVICE_NAME)
    async def FindByActive(self, request: Any, context: Any) -> Any:
        page, page_size = _normalize(request.page, request.page_size)
        rows, total = await self._service.find_active(request.search, page, page_size)

        response = (
            shipping_address_common_pb2.ApiResponsePaginationShippingDeleteAt(
                status="success",
                message="Successfully fetched active shipping addresses",
            )
        )
        for row in rows:
            fill_shipping_response_delete_at(response.data.add(), row)
        response.pagination.CopyFrom(_pagination(page, page_size, total))
        return response

    @grpc_method("ShippingQueryService.FindByTrashed", SERVICE_NAME)
    async def FindByTrashed(self, request: Any, context: Any) -> Any:
        page, page_size = _normalize(request.page, request.page_size)
        rows, total = await self._service.find_trashed(request.search, page, page_size)

        response = (
            shipping_address_common_pb2.ApiResponsePaginationShippingDeleteAt(
                status="success",
                message="Successfully fetched trashed shipping addresses",
            )
        )
        for row in rows:
            fill_shipping_response_delete_at(response.data.add(), row)
        response.pagination.CopyFrom(_pagination(page, page_size, total))
        return response


__all__ = ["ShippingQueryHandler"]

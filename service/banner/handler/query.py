"""Banner query gRPC handler. Banner timestamps are emitted as `%Y-%m-%d %H:%M:%S.mmm`, dates as `%Y-%m-%d` and clock times as `%H:%M:%S` — the banner-specific wire shape the handlers produce. Do not unify with role/user layouts. Unlike the role/user handlers, a NULL `deleted_at` is rendered as the zero-value wrapper ("" via `formatTimestamp`), because the banner mapping always attaches the wrapper; the gateway therefore always emits `deleted_at` (empty string when unset)."""

from __future__ import annotations

import math
from typing import Any

from google.protobuf import wrappers_pb2

from pb.banner import banner_common_pb2, banner_query_pb2_grpc
from pb.common import api_pb2 as common_pb2
from pkg.logger.logger import Logger
from pkg.middleware import grpc_method
from service.banner.service.interfaces import BannerQueryService
from service.banner.service.service import SERVICE_NAME
from shared.convert.convert import (
    format_clock,
    format_iso_date,
    format_timestamp_millis,
)
from shared.errors import err_grpc_banner_invalid_id


def _fill_banner(message: Any, banner: Any) -> None:
    message.banner_id = banner.banner_id
    message.name = banner.name
    message.start_date = format_iso_date(banner.start_date)
    message.end_date = format_iso_date(banner.end_date)
    message.start_time = format_clock(banner.start_time)
    message.end_time = format_clock(banner.end_time)
    message.is_active = banner.is_active
    message.created_at = format_timestamp_millis(banner.created_at)
    message.updated_at = format_timestamp_millis(banner.updated_at)


def _fill_banner_delete_at(message: Any, banner: Any) -> None:
    _fill_banner(message, banner)
    # always sets the pointer ("" for an invalid/NULL timestamp).
    message.deleted_at.CopyFrom(
        wrappers_pb2.StringValue(value=format_timestamp_millis(banner.deleted_at))
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


class BannerQueryHandler(banner_query_pb2_grpc.BannerQueryServiceServicer):
    def __init__(self, service: BannerQueryService, logger: Logger) -> None:
        self._service = service
        self.logger = logger

    @grpc_method("BannerQueryService.FindAll", SERVICE_NAME)
    async def FindAll(self, request: Any, context: Any) -> Any:
        page, page_size = _normalize(request.page, request.page_size)
        banners, total = await self._service.find_all(request.search, page, page_size)
        response = banner_common_pb2.ApiResponsePaginationBanner(
            status="success", message="Successfully fetched banners"
        )
        for banner in banners:
            _fill_banner(response.data.add(), banner)
        response.pagination.CopyFrom(_pagination(page, page_size, total))
        return response

    @grpc_method("BannerQueryService.FindById", SERVICE_NAME)
    async def FindById(self, request: Any, context: Any) -> Any:
        if request.id <= 0:
            raise err_grpc_banner_invalid_id
        banner = await self._service.find_by_id(request.id)
        response = banner_common_pb2.ApiResponseBanner(
            status="success", message="Successfully fetched banner"
        )
        _fill_banner(response.data, banner)
        return response

    @grpc_method("BannerQueryService.FindByActive", SERVICE_NAME)
    async def FindByActive(self, request: Any, context: Any) -> Any:
        page, page_size = _normalize(request.page, request.page_size)
        banners, total = await self._service.find_active(request.search, page, page_size)
        response = banner_common_pb2.ApiResponsePaginationBannerDeleteAt(
            status="success", message="Successfully fetched active banners"
        )
        for banner in banners:
            _fill_banner_delete_at(response.data.add(), banner)
        response.pagination.CopyFrom(_pagination(page, page_size, total))
        return response

    @grpc_method("BannerQueryService.FindByTrashed", SERVICE_NAME)
    async def FindByTrashed(self, request: Any, context: Any) -> Any:
        page, page_size = _normalize(request.page, request.page_size)
        banners, total = await self._service.find_trashed(
            request.search, page, page_size
        )
        response = banner_common_pb2.ApiResponsePaginationBannerDeleteAt(
            status="success", message="Successfully fetched trashed banners"
        )
        for banner in banners:
            _fill_banner_delete_at(response.data.add(), banner)
        response.pagination.CopyFrom(_pagination(page, page_size, total))
        return response


__all__ = ["BannerQueryHandler"]

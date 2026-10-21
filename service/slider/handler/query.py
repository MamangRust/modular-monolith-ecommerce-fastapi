"""Slider query gRPC handler. Slider timestamps are emitted as date-only strings (`%Y-%m-%d`), matching the `2006-01-02` layout. A NULL `deleted_at` is rendered with no wrapper (the mapping only attaches it when `DeletedAt.Valid`), so the gateway emits `deleted_at: null` rather than an empty string."""

from __future__ import annotations

import math
from typing import Any

from google.protobuf import wrappers_pb2

from pb.common import api_pb2 as common_pb2
from pb.slider import slider_common_pb2, slider_query_pb2_grpc
from pkg.logger.logger import Logger
from pkg.middleware import grpc_method
from service.slider.service.interfaces import SliderQueryService
from service.slider.service.service import SERVICE_NAME
from shared.convert.convert import format_date


def _fill_slider(message: Any, slider: Any) -> None:
    message.id = slider.slider_id
    message.name = slider.name
    message.image = slider.image
    message.created_at = format_date(slider.created_at)
    message.updated_at = format_date(slider.updated_at)


def _fill_slider_delete_at(message: Any, slider: Any) -> None:
    _fill_slider(message, slider)
    deleted_at = format_date(slider.deleted_at)
    if deleted_at:
        message.deleted_at.CopyFrom(wrappers_pb2.StringValue(value=deleted_at))


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


class SliderQueryHandler(slider_query_pb2_grpc.SliderQueryServiceServicer):
    def __init__(self, service: SliderQueryService, logger: Logger) -> None:
        self._service = service
        self.logger = logger

    @grpc_method("SliderQueryService.FindAll", SERVICE_NAME)
    async def FindAll(self, request: Any, context: Any) -> Any:
        page, page_size = _normalize(request.page, request.page_size)
        sliders, total = await self._service.find_all(request.search, page, page_size)
        response = slider_common_pb2.ApiResponsePaginationSlider(
            status="success", message="Successfully fetched slider records"
        )
        for slider in sliders:
            _fill_slider(response.data.add(), slider)
        response.pagination.CopyFrom(_pagination(page, page_size, total))
        return response

    @grpc_method("SliderQueryService.FindById", SERVICE_NAME)
    async def FindById(self, request: Any, context: Any) -> Any:
        slider = await self._service.find_by_id(request.id)
        response = slider_common_pb2.ApiResponseSlider(
            status="success", message="Successfully fetched slider by ID"
        )
        _fill_slider(response.data, slider)
        return response

    @grpc_method("SliderQueryService.FindByActive", SERVICE_NAME)
    async def FindByActive(self, request: Any, context: Any) -> Any:
        page, page_size = _normalize(request.page, request.page_size)
        sliders, total = await self._service.find_active(request.search, page, page_size)
        response = slider_common_pb2.ApiResponsePaginationSliderDeleteAt(
            status="success", message="Successfully fetched active slider records"
        )
        for slider in sliders:
            _fill_slider_delete_at(response.data.add(), slider)
        response.pagination.CopyFrom(_pagination(page, page_size, total))
        return response

    @grpc_method("SliderQueryService.FindByTrashed", SERVICE_NAME)
    async def FindByTrashed(self, request: Any, context: Any) -> Any:
        page, page_size = _normalize(request.page, request.page_size)
        sliders, total = await self._service.find_trashed(request.search, page, page_size)
        response = slider_common_pb2.ApiResponsePaginationSliderDeleteAt(
            status="success", message="Successfully fetched trashed slider records"
        )
        for slider in sliders:
            _fill_slider_delete_at(response.data.add(), slider)
        response.pagination.CopyFrom(_pagination(page, page_size, total))
        return response


__all__ = ["SliderQueryHandler"]

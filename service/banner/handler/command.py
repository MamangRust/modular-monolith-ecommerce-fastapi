"""Banner command gRPC handler. Request-shape validation happens here (not in the service) the shared request DTOs re-run the same `datetime=...` rules the `validator` tags expressed."""

from __future__ import annotations

from typing import Any

from pydantic import ValidationError

from pb.banner import banner_command_pb2_grpc, banner_common_pb2
from pkg.logger.logger import Logger
from pkg.middleware import grpc_method
from service.banner.handler.query import _fill_banner, _fill_banner_delete_at
from service.banner.service.interfaces import BannerCommandService
from service.banner.service.service import SERVICE_NAME
from shared.domain.requests.banner import CreateBannerRequest, UpdateBannerRequest
from shared.errors import (
    err_grpc_banner_invalid_id,
    err_grpc_validate_create_banner,
    err_grpc_validate_update_banner,
)


class BannerCommandHandler(banner_command_pb2_grpc.BannerCommandServiceServicer):
    def __init__(self, service: BannerCommandService, logger: Logger) -> None:
        self._service = service
        self.logger = logger

    @grpc_method("BannerCommandService.Create", SERVICE_NAME)
    async def Create(self, request: Any, context: Any) -> Any:
        try:
            create_request = CreateBannerRequest(
                name=request.name,
                start_date=request.start_date,
                end_date=request.end_date,
                start_time=request.start_time,
                end_time=request.end_time,
                is_active=request.is_active,
            )
        except ValidationError as exc:
            raise err_grpc_validate_create_banner.with_internal(exc) from exc

        banner = await self._service.create(create_request)
        response = banner_common_pb2.ApiResponseBanner(
            status="success", message="Successfully created banner"
        )
        _fill_banner(response.data, banner)
        return response

    @grpc_method("BannerCommandService.Update", SERVICE_NAME)
    async def Update(self, request: Any, context: Any) -> Any:
        if request.banner_id <= 0:
            raise err_grpc_banner_invalid_id
        try:
            update_request = UpdateBannerRequest(
                banner_id=request.banner_id,
                name=request.name,
                start_date=request.start_date,
                end_date=request.end_date,
                start_time=request.start_time,
                end_time=request.end_time,
                is_active=request.is_active,
            )
        except ValidationError as exc:
            raise err_grpc_validate_update_banner.with_internal(exc) from exc

        banner = await self._service.update(update_request)
        response = banner_common_pb2.ApiResponseBanner(
            status="success", message="Successfully updated banner"
        )
        _fill_banner(response.data, banner)
        return response

    @grpc_method("BannerCommandService.Trash", SERVICE_NAME)
    async def Trash(self, request: Any, context: Any) -> Any:
        if request.id <= 0:
            raise err_grpc_banner_invalid_id
        banner = await self._service.trash(request.id)
        response = banner_common_pb2.ApiResponseBannerDeleteAt(
            status="success", message="Successfully trashed banner"
        )
        _fill_banner_delete_at(response.data, banner)
        return response

    @grpc_method("BannerCommandService.Restore", SERVICE_NAME)
    async def Restore(self, request: Any, context: Any) -> Any:
        if request.id <= 0:
            raise err_grpc_banner_invalid_id
        banner = await self._service.restore(request.id)
        response = banner_common_pb2.ApiResponseBannerDeleteAt(
            status="success", message="Successfully restored banner"
        )
        _fill_banner_delete_at(response.data, banner)
        return response

    @grpc_method("BannerCommandService.DeletePermanent", SERVICE_NAME)
    async def DeletePermanent(self, request: Any, context: Any) -> Any:
        if request.id <= 0:
            raise err_grpc_banner_invalid_id
        await self._service.delete_permanent(request.id)
        return banner_common_pb2.ApiResponseBannerDelete(
            status="success", message="Successfully deleted banner permanently"
        )

    @grpc_method("BannerCommandService.RestoreAll", SERVICE_NAME)
    async def RestoreAll(self, request: Any, context: Any) -> Any:
        await self._service.restore_all()
        return banner_common_pb2.ApiResponseBannerAll(
            status="success", message="Successfully restored all banners"
        )

    @grpc_method("BannerCommandService.DeleteAll", SERVICE_NAME)
    async def DeleteAll(self, request: Any, context: Any) -> Any:
        await self._service.delete_all_permanent()
        return banner_common_pb2.ApiResponseBannerAll(
            status="success", message="Successfully deleted all banners permanently"
        )


__all__ = ["BannerCommandHandler"]

"""Slider command gRPC handler. Unlike banner, the slider create/update requests carry no `validate` tags, so there is no request-shape validation here — the handler forwards the proto fields straight to the service. The `id == 0` guard uses `err_grpc_invalid_id` (400); every other failure is propagated from the service and mapped to its original code by the `grpc_method` decorator (a 404 `slider not found` stays `NOT_FOUND` on the wire)."""

from __future__ import annotations

from typing import Any

from pb.slider import slider_command_pb2_grpc, slider_common_pb2
from pkg.logger.logger import Logger
from pkg.middleware import grpc_method
from service.slider.handler.query import _fill_slider, _fill_slider_delete_at
from service.slider.service.interfaces import SliderCommandService
from service.slider.service.service import SERVICE_NAME
from shared.domain.requests.slider import CreateSliderRequest, UpdateSliderRequest
from shared.errors.slider_errors import err_grpc_invalid_id


class SliderCommandHandler(slider_command_pb2_grpc.SliderCommandServiceServicer):
    def __init__(self, service: SliderCommandService, logger: Logger) -> None:
        self._service = service
        self.logger = logger

    @grpc_method("SliderCommandService.Create", SERVICE_NAME)
    async def Create(self, request: Any, context: Any) -> Any:
        create_request = CreateSliderRequest(name=request.name, image=request.image)
        slider = await self._service.create(create_request)
        response = slider_common_pb2.ApiResponseSlider(
            status="success", message="Successfully created slider"
        )
        _fill_slider(response.data, slider)
        return response

    @grpc_method("SliderCommandService.Update", SERVICE_NAME)
    async def Update(self, request: Any, context: Any) -> Any:
        if request.id <= 0:
            raise err_grpc_invalid_id
        update_request = UpdateSliderRequest(
            slider_id=request.id, name=request.name, image=request.image
        )
        slider = await self._service.update(update_request)
        response = slider_common_pb2.ApiResponseSlider(
            status="success", message="Successfully updated slider"
        )
        _fill_slider(response.data, slider)
        return response

    @grpc_method("SliderCommandService.TrashedSlider", SERVICE_NAME)
    async def TrashedSlider(self, request: Any, context: Any) -> Any:
        if request.id <= 0:
            raise err_grpc_invalid_id
        slider = await self._service.trash(request.id)
        response = slider_common_pb2.ApiResponseSliderDeleteAt(
            status="success", message="Successfully trashed slider"
        )
        _fill_slider_delete_at(response.data, slider)
        return response

    @grpc_method("SliderCommandService.RestoreSlider", SERVICE_NAME)
    async def RestoreSlider(self, request: Any, context: Any) -> Any:
        if request.id <= 0:
            raise err_grpc_invalid_id
        slider = await self._service.restore(request.id)
        response = slider_common_pb2.ApiResponseSliderDeleteAt(
            status="success", message="Successfully restored slider"
        )
        _fill_slider_delete_at(response.data, slider)
        return response

    @grpc_method("SliderCommandService.DeleteSliderPermanent", SERVICE_NAME)
    async def DeleteSliderPermanent(self, request: Any, context: Any) -> Any:
        if request.id <= 0:
            raise err_grpc_invalid_id
        await self._service.delete_permanent(request.id)
        return slider_common_pb2.ApiResponseSliderDelete(
            status="success", message="Successfully deleted slider permanently"
        )

    @grpc_method("SliderCommandService.RestoreAllSlider", SERVICE_NAME)
    async def RestoreAllSlider(self, request: Any, context: Any) -> Any:
        await self._service.restore_all()
        return slider_common_pb2.ApiResponseSliderAll(
            status="success", message="Successfully restored all sliders"
        )

    @grpc_method("SliderCommandService.DeleteAllSliderPermanent", SERVICE_NAME)
    async def DeleteAllSliderPermanent(self, request: Any, context: Any) -> Any:
        await self._service.delete_all_permanent()
        return slider_common_pb2.ApiResponseSliderAll(
            status="success", message="Successfully deleted all sliders permanently"
        )


__all__ = ["SliderCommandHandler"]

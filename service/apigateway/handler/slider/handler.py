"""Gateway slider handler: REST <-> slider gRPC. Only transport concerns live here: build the proto request, call the domain over gRPC, convert a gRPC failure back to its original AppError, and map the proto response to the shared response envelope. No SQL, no business rules. `create`/`update` mirror `parseSliderForm`: the name is trimmed and must be non-empty (400 `"Name is required"`), and the optional `image_slider` file is uploaded through `pkg.upload_image` (`uploads/slider`). Create requires the file (400 `"Image is required"`); update sends an empty image when no file is provided,. Like the slider gateway (and unlike user), a non-positive path id is rejected before the gRPC hop with a 400 `"Invalid ID"`."""

from __future__ import annotations

from typing import Any

import grpc

from pb.slider import (
    slider_command_pb2,
    slider_command_pb2_grpc,
    slider_common_pb2,
    slider_query_pb2,
    slider_query_pb2_grpc,
)
from pkg.upload_image import ImageUpload
from service.apigateway.app.client import ServiceConnections
from shared.domain.response.responses import ApiResponse, APIResponsePagination
from shared.domain.response.slider import (
    SliderResponse,
    SliderResponseDeleteAt,
)
from shared.errors import new_bad_request_error, parse_grpc_error
from shared.mapper.slider import (
    to_api_response_pagination_slider,
    to_api_response_pagination_slider_delete_at,
    to_api_response_slider,
    to_api_response_slider_all,
    to_api_response_slider_delete,
    to_api_response_slider_delete_at,
)

RPC_TIMEOUT = 30.0

_UPLOAD_DIR = "uploads/slider"


def normalize_pagination(page: int, page_size: int) -> tuple[int, int]:
    """Gateway-side clamping."""
    if page <= 0:
        page = 1
    if page_size <= 0:
        page_size = 10
    return page, page_size


def require_positive_id(slider_id: int) -> None:
    """Reject a non-positive path id before the gRPC hop (command routes). Used for the command routes (`/trashed/{id}`, `/restore/{id}`, `/permanent/{id}`). The slider gRPC handlers guard `id <= 0` and return `err_grpc_invalid_id` (400); this catches it one hop earlier with the same `Invalid ID` body. The query `find_by_id` route deliberately does NOT use this — gateway `FindById` forwards `id == 0` to the gRPC handler, which has no id guard and returns 404 NOT_FOUND from the repository."""
    if slider_id <= 0:
        raise new_bad_request_error("Invalid ID")


class SliderHandler:
    def __init__(self, connections: ServiceConnections, upload: ImageUpload) -> None:
        channel = connections.channel("slider")
        self._query = slider_query_pb2_grpc.SliderQueryServiceStub(channel)
        self._command = slider_command_pb2_grpc.SliderCommandServiceStub(channel)
        self._upload = upload

    # ---- query ----

    async def find_all(
        self, page: int, page_size: int, search: str
    ) -> APIResponsePagination[list[SliderResponse]]:
        page, page_size = normalize_pagination(page, page_size)
        request = slider_query_pb2.FindAllSliderRequest(page=page, page_size=page_size, search=search or "")
        try:
            response = await self._query.FindAll(request, timeout=RPC_TIMEOUT)
        except grpc.aio.AioRpcError as exc:
            raise parse_grpc_error(exc) from exc
        return to_api_response_pagination_slider(response)

    async def find_by_id(self, slider_id: int) -> ApiResponse[SliderResponse]:
        request = slider_common_pb2.FindByIdSliderRequest(id=slider_id)
        try:
            response = await self._query.FindById(request, timeout=RPC_TIMEOUT)
        except grpc.aio.AioRpcError as exc:
            raise parse_grpc_error(exc) from exc
        return to_api_response_slider(response)

    async def find_by_active(
        self, page: int, page_size: int, search: str
    ) -> APIResponsePagination[list[SliderResponseDeleteAt]]:
        page, page_size = normalize_pagination(page, page_size)
        request = slider_query_pb2.FindAllSliderRequest(page=page, page_size=page_size, search=search or "")
        try:
            response = await self._query.FindByActive(request, timeout=RPC_TIMEOUT)
        except grpc.aio.AioRpcError as exc:
            raise parse_grpc_error(exc) from exc
        return to_api_response_pagination_slider_delete_at(response)

    async def find_by_trashed(
        self, page: int, page_size: int, search: str
    ) -> APIResponsePagination[list[SliderResponseDeleteAt]]:
        page, page_size = normalize_pagination(page, page_size)
        request = slider_query_pb2.FindAllSliderRequest(page=page, page_size=page_size, search=search or "")
        try:
            response = await self._query.FindByTrashed(request, timeout=RPC_TIMEOUT)
        except grpc.aio.AioRpcError as exc:
            raise parse_grpc_error(exc) from exc
        return to_api_response_pagination_slider_delete_at(response)

    # ---- command ----

    async def create(self, name: str, image_file: Any) -> ApiResponse[SliderResponse]:
        clean_name = (name or "").strip()
        if not clean_name:
            raise new_bad_request_error("Name is required")
        if image_file is None:
            raise new_bad_request_error("Image is required")
        image = await self._upload.process_image_upload(_UPLOAD_DIR, image_file, False)
        request = slider_command_pb2.CreateSliderRequest(name=clean_name, image=image)
        try:
            response = await self._command.Create(request, timeout=RPC_TIMEOUT)
        except grpc.aio.AioRpcError as exc:
            raise parse_grpc_error(exc) from exc
        return to_api_response_slider(response)

    async def update(
        self, slider_id: int, name: str, image_file: Any
    ) -> ApiResponse[SliderResponse]:
        require_positive_id(slider_id)
        clean_name = (name or "").strip()
        if not clean_name:
            raise new_bad_request_error("Name is required")
        image = ""
        if image_file is not None:
            image = await self._upload.process_image_upload(
                _UPLOAD_DIR, image_file, False
            )
        request = slider_command_pb2.UpdateSliderRequest(
            id=slider_id, name=clean_name, image=image
        )
        try:
            response = await self._command.Update(request, timeout=RPC_TIMEOUT)
        except grpc.aio.AioRpcError as exc:
            raise parse_grpc_error(exc) from exc
        return to_api_response_slider(response)

    async def trash(self, slider_id: int) -> ApiResponse[SliderResponseDeleteAt]:
        require_positive_id(slider_id)
        request = slider_common_pb2.FindByIdSliderRequest(id=slider_id)
        try:
            response = await self._command.TrashedSlider(
                request, timeout=RPC_TIMEOUT
            )
        except grpc.aio.AioRpcError as exc:
            raise parse_grpc_error(exc) from exc
        return to_api_response_slider_delete_at(response)

    async def restore(self, slider_id: int) -> ApiResponse[SliderResponseDeleteAt]:
        require_positive_id(slider_id)
        request = slider_common_pb2.FindByIdSliderRequest(id=slider_id)
        try:
            response = await self._command.RestoreSlider(
                request, timeout=RPC_TIMEOUT
            )
        except grpc.aio.AioRpcError as exc:
            raise parse_grpc_error(exc) from exc
        return to_api_response_slider_delete_at(response)

    async def delete_permanent(self, slider_id: int) -> ApiResponse[None]:
        require_positive_id(slider_id)
        request = slider_common_pb2.FindByIdSliderRequest(id=slider_id)
        try:
            response = await self._command.DeleteSliderPermanent(
                request, timeout=RPC_TIMEOUT
            )
        except grpc.aio.AioRpcError as exc:
            raise parse_grpc_error(exc) from exc
        return to_api_response_slider_delete(response)

    async def restore_all(self) -> ApiResponse[None]:
        try:
            response = await self._command.RestoreAllSlider(
                _empty(), timeout=RPC_TIMEOUT
            )
        except grpc.aio.AioRpcError as exc:
            raise parse_grpc_error(exc) from exc
        return to_api_response_slider_all(response)

    async def delete_all_permanent(self) -> ApiResponse[None]:
        try:
            response = await self._command.DeleteAllSliderPermanent(
                _empty(), timeout=RPC_TIMEOUT
            )
        except grpc.aio.AioRpcError as exc:
            raise parse_grpc_error(exc) from exc
        return to_api_response_slider_all(response)


def _empty():
    from google.protobuf import empty_pb2

    return empty_pb2.Empty()


__all__ = ["SliderHandler", "normalize_pagination", "require_positive_id"]

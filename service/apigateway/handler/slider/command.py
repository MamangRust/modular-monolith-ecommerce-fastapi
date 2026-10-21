"""Slider command REST routes. Static paths (`/restore/all`, `/permanent/all`) are registered before the `{slider_id}` variants because Starlette matches in registration order. `Create`/`Update` are multipart form endpoints (`@Accept mpfd`): the name and optional `image_slider` file are read as form data and validated in the handler to reproduce exact messages (`Name is required`, `Image is required`). Create returns 201, matching."""

from __future__ import annotations

from fastapi import APIRouter, File, Form, Request, UploadFile, status

from service.apigateway.handler.slider.handler import SliderHandler
from shared.domain.response.responses import ApiResponse
from shared.domain.response.slider import SliderResponse, SliderResponseDeleteAt

router = APIRouter(prefix="/api/slider-command", tags=["slider-command"])


def get_slider_handler(request: Request) -> SliderHandler:
    return SliderHandler(request.app.state.connections, request.app.state.upload_image)


@router.post("/create", status_code=status.HTTP_201_CREATED)
async def create_slider(
    request: Request,
    name: str = Form(""),
    image_slider: UploadFile | None = File(None),
) -> ApiResponse[SliderResponse]:
    return await get_slider_handler(request).create(name, image_slider)


# Static paths first — `/restore/all` and `/permanent/all` must not be
# captured as slider_id by `/{slider_id}` variants below.
@router.post("/restore/all")
async def restore_all_slider(request: Request) -> ApiResponse[None]:
    return await get_slider_handler(request).restore_all()


@router.post("/permanent/all")
async def delete_all_slider_permanent(request: Request) -> ApiResponse[None]:
    return await get_slider_handler(request).delete_all_permanent()


@router.post("/update/{slider_id}")
async def update_slider(
    request: Request,
    slider_id: int,
    name: str = Form(""),
    image_slider: UploadFile | None = File(None),
) -> ApiResponse[SliderResponse]:
    return await get_slider_handler(request).update(slider_id, name, image_slider)


@router.post("/trashed/{slider_id}")
async def trash_slider(
    request: Request,
    slider_id: int,
) -> ApiResponse[SliderResponseDeleteAt]:
    return await get_slider_handler(request).trash(slider_id)


@router.post("/restore/{slider_id}")
async def restore_slider(
    request: Request,
    slider_id: int,
) -> ApiResponse[SliderResponseDeleteAt]:
    return await get_slider_handler(request).restore(slider_id)


@router.delete("/permanent/{slider_id}")
async def delete_slider_permanent(
    request: Request,
    slider_id: int,
) -> ApiResponse[None]:
    return await get_slider_handler(request).delete_permanent(slider_id)


__all__ = ["router"]

"""Category command REST routes. Static paths (`/restore/all`, `/permanent/all`) are registered before the `{category_id}` variants because Starlette matches in registration order. `Create`/`Update` are multipart form endpoints (`@Accept mpfd`): the required fields (`name`, `description`, `image_category`) are declared with `min_length=1` so a missing/empty value yields the same 400 `"Validation failed"` envelope as `req.Validate`, and an optional `image` file is uploaded through `upload_image` (see the handler). Create returns 201."""

from __future__ import annotations

from fastapi import APIRouter, File, Form, Request, UploadFile, status

from service.apigateway.handler.category.handler import CategoryHandler
from shared.domain.response.category import (
    CategoryResponse,
    CategoryResponseDeleteAt,
)
from shared.domain.response.responses import ApiResponse

router = APIRouter(prefix="/api/category-command", tags=["category-command"])


def get_category_handler(request: Request) -> CategoryHandler:
    return CategoryHandler(
        request.app.state.connections, request.app.state.upload_image
    )


@router.post("/create", status_code=status.HTTP_201_CREATED)
async def create_category(
    request: Request,
    name: str = Form(..., min_length=1),
    description: str = Form(..., min_length=1),
    slug_category: str = Form(""),
    image_category: str = Form(..., min_length=1),
    image: UploadFile | None = File(None),
) -> ApiResponse[CategoryResponse]:
    return await get_category_handler(request).create(
        name,
        description,
        slug_category,
        image_category,
        image,
    )


# Static paths first — `/restore/all` and `/permanent/all` must not be
# captured as category_id="all".
@router.post("/restore/all")
async def restore_all_category(request: Request) -> ApiResponse[None]:
    return await get_category_handler(request).restore_all()


@router.delete("/permanent/all")
async def delete_all_category_permanent(request: Request) -> ApiResponse[None]:
    return await get_category_handler(request).delete_all_permanent()


@router.post("/update/{category_id}")
async def update_category(
    request: Request,
    category_id: int,
    name: str = Form(..., min_length=1),
    description: str = Form(..., min_length=1),
    slug_category: str = Form(""),
    image_category: str = Form(..., min_length=1),
    image: UploadFile | None = File(None),
) -> ApiResponse[CategoryResponse]:
    return await get_category_handler(request).update(
        category_id,
        name,
        description,
        slug_category,
        image_category,
        image,
    )


@router.post("/trashed/{category_id}")
async def trash_category(
    request: Request,
    category_id: int,
) -> ApiResponse[CategoryResponseDeleteAt]:
    return await get_category_handler(request).trash(category_id)


@router.post("/restore/{category_id}")
async def restore_category(
    request: Request,
    category_id: int,
) -> ApiResponse[CategoryResponseDeleteAt]:
    return await get_category_handler(request).restore(category_id)


@router.delete("/permanent/{category_id}")
async def delete_category_permanent(
    request: Request,
    category_id: int,
) -> ApiResponse[None]:
    return await get_category_handler(request).delete_permanent(category_id)


__all__ = ["router"]

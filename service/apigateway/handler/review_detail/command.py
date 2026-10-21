"""Review detail command REST routes. Static paths (`/restore/all`, `/permanent/all`) are registered before the `{review_detail_id}` variants because Starlette matches in registration order. `Create`/`Update` are multipart form endpoints (`@Accept mpfd`). `review_id`, `type` and `caption` are declared as form fields; `url` is read from the raw form because accepts it either as an uploaded file or as a plain string under the same field name (then). Validation lives in the handler so the messages match exactly. Create returns 201."""

from __future__ import annotations

from fastapi import APIRouter, Form, Request, status

from service.apigateway.handler.review_detail.handler import ReviewDetailHandler
from shared.domain.response.responses import ApiResponse
from shared.domain.response.review_detail import (
    ReviewDetailResponse,
    ReviewDetailResponseDeleteAt,
)

router = APIRouter(prefix="/api/review-detail-command", tags=["review-detail-command"])


def get_review_detail_handler(request: Request) -> ReviewDetailHandler:
    return ReviewDetailHandler(
        request.app.state.connections, request.app.state.upload_image
    )


@router.post("/create", status_code=status.HTTP_201_CREATED)
async def create_review_detail(
    request: Request,
    review_id: str = Form(""),
    type: str = Form(""),
    caption: str = Form(""),
) -> ApiResponse[ReviewDetailResponse]:
    form = await request.form()
    return await get_review_detail_handler(request).create(
        review_id, type, form.get("url"), caption
    )


# Static paths first — `/restore/all` and `/permanent/all` must not be captured
# as review_detail_id by the `/{review_detail_id}` variants below.
@router.post("/restore/all")
async def restore_all_review_detail(request: Request) -> ApiResponse[None]:
    return await get_review_detail_handler(request).restore_all()


@router.post("/permanent/all")
async def delete_all_review_detail_permanent(request: Request) -> ApiResponse[None]:
    return await get_review_detail_handler(request).delete_all_permanent()


@router.post("/update/{review_detail_id}")
async def update_review_detail(
    request: Request,
    review_detail_id: int,
    type: str = Form(""),
    caption: str = Form(""),
) -> ApiResponse[ReviewDetailResponse]:
    form = await request.form()
    return await get_review_detail_handler(request).update(
        review_detail_id, type, form.get("url"), caption
    )


@router.post("/trashed/{review_detail_id}")
async def trash_review_detail(
    request: Request,
    review_detail_id: int,
) -> ApiResponse[ReviewDetailResponseDeleteAt]:
    return await get_review_detail_handler(request).trash(review_detail_id)


@router.post("/restore/{review_detail_id}")
async def restore_review_detail(
    request: Request,
    review_detail_id: int,
) -> ApiResponse[ReviewDetailResponseDeleteAt]:
    return await get_review_detail_handler(request).restore(review_detail_id)


@router.delete("/permanent/{review_detail_id}")
async def delete_review_detail_permanent(
    request: Request,
    review_detail_id: int,
) -> ApiResponse[None]:
    return await get_review_detail_handler(request).delete_permanent(review_detail_id)


__all__ = ["router"]

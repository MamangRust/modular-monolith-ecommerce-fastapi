"""Product command REST routes. Static paths (`/restore/all`, `/permanent/all`) are registered before the `{product_id}` variants because Starlette matches in registration order. `Create` returns 201 (`http.StatusCreated`); every path-id route guards `id <= 0` with 400 `Invalid ID`. `Create`/`Update` are multipart form endpoints (`@Accept mpfd`). reads the form values with `strconv.Atoi` (missing/invalid -> 0) and lets the domain request validator reject them, so declares the numeric/string fields with zero defaults and leaves validation to the product service — a missing field yields the same 400 `"validation failed: invalid create/update product request"` as rather than a FastAPI 422. An optional `image` file is uploaded through `upload_image` (see the handler). `DeletePermanent`/`RestoreAll`/`DeleteAllPermanent` return the data-less `ApiResponse[None]` envelope,."""

from __future__ import annotations

from fastapi import APIRouter, File, Form, Request, UploadFile, status

from service.apigateway.handler.product.handler import ProductHandler
from shared.domain.response.product import (
    ProductResponse,
    ProductResponseDeleteAt,
)
from shared.domain.response.responses import ApiResponse

router = APIRouter(prefix="/api/product-command", tags=["product-command"])


def get_product_handler(request: Request) -> ProductHandler:
    return ProductHandler(request.app.state.connections, request.app.state.upload_image)


@router.post("/create", status_code=status.HTTP_201_CREATED)
async def create_product(
    request: Request,
    merchant_id: int = Form(0),
    category_id: int = Form(0),
    name: str = Form(""),
    description: str = Form(""),
    price: int = Form(0),
    count_in_stock: int = Form(0),
    brand: str = Form(""),
    weight: int = Form(0),
    rating: int = Form(0),
    slug_product: str = Form(""),
    image: UploadFile | None = File(None),
) -> ApiResponse[ProductResponse]:
    return await get_product_handler(request).create(
        merchant_id,
        category_id,
        name,
        description,
        price,
        count_in_stock,
        brand,
        weight,
        rating,
        slug_product,
        image,
    )


# Static paths first — `/restore/all` and `/permanent/all` must not be captured
# as product_id="all".
@router.post("/restore/all")
async def restore_all_product(request: Request) -> ApiResponse[None]:
    return await get_product_handler(request).restore_all()


@router.post("/permanent/all")
async def delete_all_product_permanent(request: Request) -> ApiResponse[None]:
    return await get_product_handler(request).delete_all_permanent()


@router.post("/update/{product_id}")
async def update_product(
    request: Request,
    product_id: int,
    merchant_id: int = Form(0),
    category_id: int = Form(0),
    name: str = Form(""),
    description: str = Form(""),
    price: int = Form(0),
    count_in_stock: int = Form(0),
    brand: str = Form(""),
    weight: int = Form(0),
    rating: int = Form(0),
    slug_product: str = Form(""),
    image: UploadFile | None = File(None),
) -> ApiResponse[ProductResponse]:
    return await get_product_handler(request).update(
        product_id,
        merchant_id,
        category_id,
        name,
        description,
        price,
        count_in_stock,
        brand,
        weight,
        rating,
        slug_product,
        image,
    )


@router.post("/trashed/{product_id}")
async def trash_product(
    request: Request,
    product_id: int,
) -> ApiResponse[ProductResponseDeleteAt]:
    return await get_product_handler(request).trash(product_id)


@router.post("/restore/{product_id}")
async def restore_product(
    request: Request,
    product_id: int,
) -> ApiResponse[ProductResponseDeleteAt]:
    return await get_product_handler(request).restore(product_id)


@router.delete("/permanent/{product_id}")
async def delete_product_permanent(
    request: Request,
    product_id: int,
) -> ApiResponse[None]:
    return await get_product_handler(request).delete_permanent(product_id)


__all__ = ["router"]

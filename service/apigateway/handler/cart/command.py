"""Cart command REST routes. binds a JSON body and validates it (`CreateCartRequest`/`DeleteCartRequest`/ `DeleteAllCartRequest`); reuses the shared pydantic DTOs, so an invalid body yields the global 400 `"Validation failed"` envelope rather than FastAPI's 422. The owner id is always taken from the JWT (`request.state.user_id`) and the body `user_id` is ignored,. `Create` returns 201 (`http.StatusCreated`); the gateway does not cache."""

from __future__ import annotations

from fastapi import APIRouter, Request, status

from service.apigateway.handler.cart.handler import CartHandler
from shared.domain.requests.cart import (
    CreateCartRequest,
    DeleteAllCartRequest,
    DeleteCartRequest,
)
from shared.domain.response.cart import CartResponse
from shared.domain.response.responses import ApiResponse

router = APIRouter(prefix="/api/cart-command", tags=["cart-command"])


def get_cart_handler(request: Request) -> CartHandler:
    return CartHandler(request.app.state.connections)


@router.post("/create", status_code=status.HTTP_201_CREATED)
async def create_cart(
    request: Request,
    body: CreateCartRequest,
) -> ApiResponse[CartResponse]:
    return await get_cart_handler(request).create(
        getattr(request.state, "user_id", None), body.product_id, body.quantity
    )


@router.delete("/delete")
async def delete_cart(
    request: Request,
    body: DeleteCartRequest,
) -> ApiResponse[None]:
    return await get_cart_handler(request).delete(
        getattr(request.state, "user_id", None), body.cart_id
    )


@router.post("/delete-all")
async def delete_all_cart(
    request: Request,
    body: DeleteAllCartRequest,
) -> ApiResponse[None]:
    return await get_cart_handler(request).delete_all(
        getattr(request.state, "user_id", None), body.cart_ids
    )


__all__ = ["router"]

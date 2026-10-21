"""cart command gRPC handler. Each RPC builds the request DTO and validates it; a validation failure raises the matching sentinel (`err_grpc_validate_create_cart` / `err_grpc_validate_delete_cart` / `err_grpc_validate_delete_all_cart`). There is no explicit `id == 0` guard — the pydantic `ge=1` constraints cover it, matching `Validate`. The catalogue's `err_grpc_cart_invalid_id` / `err_grpc_cart_not_found` are therefore unreferenced, like product's `err_grpc_invalid_id`."""

from __future__ import annotations

from typing import Any

from pydantic import ValidationError

from pb.cart import cart_command_pb2_grpc, cart_common_pb2
from pkg.logger.logger import Logger
from pkg.middleware import grpc_method
from service.cart.handler.mapping import fill_cart_response
from service.cart.service.interfaces import CartCommandService
from service.cart.service.service import SERVICE_NAME
from shared.domain.requests.cart import (
    CreateCartRequest,
    DeleteAllCartRequest,
    DeleteCartRequest,
)
from shared.errors.cart_errors import (
    err_grpc_validate_create_cart,
    err_grpc_validate_delete_all_cart,
    err_grpc_validate_delete_cart,
)


class CartCommandHandler(cart_command_pb2_grpc.CartCommandServiceServicer):
    def __init__(self, service: CartCommandService, logger: Logger) -> None:
        self._service = service
        self.logger = logger

    @grpc_method("CartCommandService.Create", SERVICE_NAME)
    async def Create(self, request: Any, context: Any) -> Any:
        try:
            create_request = CreateCartRequest(
                product_id=request.product_id,
                user_id=request.user_id,
                quantity=request.quantity,
            )
        except ValidationError as exc:
            raise err_grpc_validate_create_cart from exc
        cart = await self._service.create(create_request)
        response = cart_common_pb2.ApiResponseCart(
            status="success", message="Successfully created cart"
        )
        fill_cart_response(response.data, cart)
        return response

    @grpc_method("CartCommandService.Delete", SERVICE_NAME)
    async def Delete(self, request: Any, context: Any) -> Any:
        try:
            delete_request = DeleteCartRequest(
                cart_id=request.cart_id,
                user_id=request.user_id,
            )
        except ValidationError as exc:
            raise err_grpc_validate_delete_cart from exc
        await self._service.delete_permanent(delete_request)
        return cart_common_pb2.ApiResponseCartDelete(
            status="success",
            message="Successfully deleted cart item permanently",
        )

    @grpc_method("CartCommandService.DeleteAll", SERVICE_NAME)
    async def DeleteAll(self, request: Any, context: Any) -> Any:
        try:
            delete_all_request = DeleteAllCartRequest(
                user_id=request.user_id,
                cart_ids=list(request.cart_ids),
            )
        except ValidationError as exc:
            raise err_grpc_validate_delete_all_cart from exc
        await self._service.delete_all(delete_all_request)
        return cart_common_pb2.ApiResponseCartAll(
            status="success",
            message="Successfully deleted all cart items permanently",
        )


__all__ = ["CartCommandHandler"]

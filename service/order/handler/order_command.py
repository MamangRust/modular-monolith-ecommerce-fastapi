"""order command gRPC handler. `Create`/`Update` build the request DTO and validate it; a validation failure raises the matching sentinel (`err_grpc_validate_create_order` / `err_grpc_validate_update_order`). The nested item DTOs are not deep-validated (`validate:"required"` has no `dive`), so a zero-valued item only fails in the service. `Update` attaches the shipping DTO only when the proto `shipping` message is present (`HasField`); `pointerIntToInt` maps a non-positive `shipping_id` to `nil`, so the service falls back to `FindByOrder`. Every single-row mutation guards `id == 0` with `err_grpc_order_invalid_id` (400 "Invalid ID")."""

from __future__ import annotations

from typing import Any

from pydantic import ValidationError

from pb.order import order_command_pb2_grpc, order_common_pb2
from pkg.logger.logger import Logger
from pkg.middleware import grpc_method
from service.order.handler.mapping import (
    fill_order_response,
    fill_order_response_delete_at,
)
from service.order.service.interfaces import OrderCommandService
from service.order.service.service import SERVICE_NAME
from shared.domain.requests.order import (
    CreateOrderItemRequest,
    CreateOrderRequest,
    UpdateOrderItemRequest,
    UpdateOrderRequest,
)
from shared.domain.requests.shipping_address import (
    CreateShippingAddressRequest,
    UpdateShippingAddressRequest,
)
from shared.errors.order_errors import (
    err_grpc_order_invalid_id,
    err_grpc_validate_create_order,
    err_grpc_validate_update_order,
)


def _pointer_int_to_int(value: int) -> int | None:
    return value if value > 0 else None


class OrderCommandHandler(order_command_pb2_grpc.OrderCommandServiceServicer):
    def __init__(self, service: OrderCommandService, logger: Logger) -> None:
        self._service = service
        self.logger = logger

    @grpc_method("OrderCommandService.Create", SERVICE_NAME)
    async def Create(self, request: Any, context: Any) -> Any:
        items = [
            CreateOrderItemRequest(
                product_id=item.product_id,
                quantity=item.quantity,
                price=item.price,
            )
            for item in request.items
        ]
        try:
            create_request = CreateOrderRequest(
                merchant_id=request.merchant_id,
                user_id=request.user_id,
                total_price=request.total_price,
                items=items,
                shipping_address=CreateShippingAddressRequest(
                    alamat=request.shipping.alamat,
                    provinsi=request.shipping.provinsi,
                    kota=request.shipping.kota,
                    courier=request.shipping.courier,
                    shipping_method=request.shipping.shipping_method,
                    shipping_cost=request.shipping.shipping_cost,
                    negara=request.shipping.negara,
                ),
            )
        except ValidationError as exc:
            raise err_grpc_validate_create_order from exc

        order = await self._service.create(create_request)
        response = order_common_pb2.ApiResponseOrder(
            status="success", message="Successfully created order"
        )
        fill_order_response(response.data, order)
        return response

    @grpc_method("OrderCommandService.Update", SERVICE_NAME)
    async def Update(self, request: Any, context: Any) -> Any:
        items = [
            UpdateOrderItemRequest(
                order_item_id=item.order_item_id,
                product_id=item.product_id,
                quantity=item.quantity,
                price=item.price,
            )
            for item in request.items
        ]

        shipping_address: UpdateShippingAddressRequest | None = None
        if request.HasField("shipping"):
            shipping = request.shipping
            shipping_address = UpdateShippingAddressRequest(
                shipping_id=_pointer_int_to_int(shipping.shipping_id),
                alamat=shipping.alamat,
                provinsi=shipping.provinsi,
                kota=shipping.kota,
                courier=shipping.courier,
                shipping_method=shipping.shipping_method,
                shipping_cost=shipping.shipping_cost,
                negara=shipping.negara,
            )

        try:
            update_request = UpdateOrderRequest(
                order_id=int(request.order_id),
                user_id=request.user_id,
                total_price=request.total_price,
                items=items,
                shipping_address=shipping_address,
            )
        except ValidationError as exc:
            raise err_grpc_validate_update_order from exc

        order = await self._service.update(update_request)
        response = order_common_pb2.ApiResponseOrder(
            status="success", message="Successfully updated order"
        )
        fill_order_response(response.data, order)
        return response

    @grpc_method("OrderCommandService.TrashedOrder", SERVICE_NAME)
    async def TrashedOrder(self, request: Any, context: Any) -> Any:
        if request.id == 0:
            raise err_grpc_order_invalid_id
        order = await self._service.trash(int(request.id))
        response = order_common_pb2.ApiResponseOrderDeleteAt(
            status="success", message="Successfully trashed order"
        )
        fill_order_response_delete_at(response.data, order)
        return response

    @grpc_method("OrderCommandService.RestoreOrder", SERVICE_NAME)
    async def RestoreOrder(self, request: Any, context: Any) -> Any:
        if request.id == 0:
            raise err_grpc_order_invalid_id
        order = await self._service.restore(int(request.id))
        response = order_common_pb2.ApiResponseOrderDeleteAt(
            status="success", message="Successfully restored order"
        )
        fill_order_response_delete_at(response.data, order)
        return response

    @grpc_method("OrderCommandService.DeleteOrderPermanent", SERVICE_NAME)
    async def DeleteOrderPermanent(self, request: Any, context: Any) -> Any:
        if request.id == 0:
            raise err_grpc_order_invalid_id
        await self._service.delete_permanent(int(request.id))
        return order_common_pb2.ApiResponseOrderDelete(
            status="success",
            message="Successfully deleted order permanently",
        )

    @grpc_method("OrderCommandService.RestoreAllOrder", SERVICE_NAME)
    async def RestoreAllOrder(self, request: Any, context: Any) -> Any:
        await self._service.restore_all()
        return order_common_pb2.ApiResponseOrderAll(
            status="success", message="Successfully restored all orders"
        )

    @grpc_method("OrderCommandService.DeleteAllOrderPermanent", SERVICE_NAME)
    async def DeleteAllOrderPermanent(self, request: Any, context: Any) -> Any:
        await self._service.delete_all()
        return order_common_pb2.ApiResponseOrderAll(
            status="success",
            message="Successfully deleted all orders permanently",
        )


__all__ = ["OrderCommandHandler"]

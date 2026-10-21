"""Order item command gRPC handler. Service failures propagate through the `@grpc_method` decorator, matching `errors.ToGrpcError` (the repository's 404 is preserved on the wire). `Create`/`Update`/`Trash`/`Restore` return the full `OrderItemResponse`; the permanent deletes and the bulk operations return the data-less envelopes."""

from __future__ import annotations

from typing import Any

from pydantic import ValidationError

from pb.order_item import (
    order_item_command_pb2,
    order_item_command_pb2_grpc,
    order_item_common_pb2,
)
from pkg.logger.logger import Logger
from pkg.middleware import grpc_method
from service.order_item.handler.mapping import fill_order_item_response
from service.order_item.service.interfaces import OrderItemCommandService
from service.order_item.service.service import SERVICE_NAME
from shared.domain.requests.order_item import (
    CreateOrderItemRecordRequest,
    UpdateOrderItemRecordRequest,
)
from shared.errors import err_grpc_invalid_id


class OrderItemCommandHandler(
    order_item_command_pb2_grpc.OrderItemCommandServiceServicer
):
    def __init__(self, service: OrderItemCommandService, logger: Logger) -> None:
        self._service = service
        self.logger = logger

    @grpc_method("OrderItemCommandService.CreateOrderItem", SERVICE_NAME)
    async def CreateOrderItem(self, request: Any, context: Any) -> Any:
        try:
            create_request = CreateOrderItemRecordRequest(
                order_id=request.order_id,
                product_id=request.product_id,
                quantity=request.quantity,
                price=request.price,
            )
        except ValidationError as exc:
            raise err_grpc_invalid_id.with_internal(exc) from exc

        row = await self._service.create(create_request)

        response = order_item_common_pb2.ApiResponseOrderItem(
            status="success", message="Successfully created order item"
        )
        fill_order_item_response(response.data, row)
        return response

    @grpc_method("OrderItemCommandService.UpdateOrderItem", SERVICE_NAME)
    async def UpdateOrderItem(self, request: Any, context: Any) -> Any:
        try:
            update_request = UpdateOrderItemRecordRequest(
                order_item_id=request.order_item_id,
                quantity=request.quantity,
                price=request.price,
            )
        except ValidationError as exc:
            raise err_grpc_invalid_id.with_internal(exc) from exc

        row = await self._service.update(update_request)

        response = order_item_common_pb2.ApiResponseOrderItem(
            status="success", message="Successfully updated order item"
        )
        fill_order_item_response(response.data, row)
        return response

    @grpc_method("OrderItemCommandService.TrashOrderItem", SERVICE_NAME)
    async def TrashOrderItem(self, request: Any, context: Any) -> Any:
        if request.id == 0:
            raise err_grpc_invalid_id
        row = await self._service.trash(int(request.id))

        response = order_item_common_pb2.ApiResponseOrderItem(
            status="success", message="Successfully trashed order item"
        )
        fill_order_item_response(response.data, row)
        return response

    @grpc_method("OrderItemCommandService.RestoreOrderItem", SERVICE_NAME)
    async def RestoreOrderItem(self, request: Any, context: Any) -> Any:
        if request.id == 0:
            raise err_grpc_invalid_id
        row = await self._service.restore(int(request.id))

        response = order_item_common_pb2.ApiResponseOrderItem(
            status="success", message="Successfully restored order item"
        )
        fill_order_item_response(response.data, row)
        return response

    @grpc_method("OrderItemCommandService.DeleteOrderItemPermanent", SERVICE_NAME)
    async def DeleteOrderItemPermanent(self, request: Any, context: Any) -> Any:
        if request.id == 0:
            raise err_grpc_invalid_id
        await self._service.delete_permanent(int(request.id))

        return order_item_common_pb2.ApiResponseOrderItemDelete(
            status="success", message="Successfully deleted order item permanently"
        )

    @grpc_method("OrderItemCommandService.RestoreAllOrdersItem", SERVICE_NAME)
    async def RestoreAllOrdersItem(self, request: Any, context: Any) -> Any:
        await self._service.restore_all()
        return order_item_common_pb2.ApiResponseOrderItemAll(
            status="success", message="Successfully restored all order items"
        )

    @grpc_method("OrderItemCommandService.DeleteAllPermanentOrdersItem", SERVICE_NAME)
    async def DeleteAllPermanentOrdersItem(self, request: Any, context: Any) -> Any:
        await self._service.delete_all()
        return order_item_common_pb2.ApiResponseOrderItemAll(
            status="success",
            message="Successfully deleted all order items permanently",
        )

    @grpc_method("OrderItemCommandService.DeleteOrderItemByOrderPermanent", SERVICE_NAME)
    async def DeleteOrderItemByOrderPermanent(self, request: Any, context: Any) -> Any:
        if request.id == 0:
            raise err_grpc_invalid_id
        await self._service.delete_by_order_permanent(int(request.id))

        return order_item_common_pb2.ApiResponseOrderItemDelete(
            status="success",
            message="Successfully deleted order items by order permanently",
        )

    @grpc_method("OrderItemCommandService.CalculateTotalPrice", SERVICE_NAME)
    async def CalculateTotalPrice(self, request: Any, context: Any) -> Any:
        if request.order_id == 0:
            raise err_grpc_invalid_id
        total = await self._service.calculate_total_price(int(request.order_id))

        return order_item_command_pb2.CalculateTotalPriceResponse(
            status="success",
            message="Successfully calculated total price",
            total_price=int(total),
        )


__all__ = ["OrderItemCommandHandler"]

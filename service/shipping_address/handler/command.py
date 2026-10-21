"""Shipping address command gRPC handler. Unlike order_item, the shipping_address handler never validates the request DTOs (the `validate` tags on `CreateShippingAddressRequest` / `UpdateShippingAddressRequest` are unused), so `CreateShipping` / `UpdateShipping` cannot fail on the handler side — a bad payload only fails at the repository, collapsed by the service to its `Failed to...` sentinel. The id-guarded operations raise the bare `ErrGrpcInvalidID` (400) when the id is 0. Service failures propagate through the `@grpc_method` decorator, matching `errors.ToGrpcError` (the repository's 404 is preserved on the wire)."""

from __future__ import annotations

from typing import Any

from pb.shipping_address import (
    shipping_address_command_pb2_grpc,
    shipping_address_common_pb2,
)
from pkg.logger.logger import Logger
from pkg.middleware import grpc_method
from service.shipping_address.handler.mapping import (
    fill_shipping_response,
    fill_shipping_response_delete_at,
)
from service.shipping_address.service.interfaces import ShippingAddressCommandService
from service.shipping_address.service.service import SERVICE_NAME
from shared.domain.requests.shipping_address import (
    CreateShippingAddressRequest,
    UpdateShippingAddressRequest,
)
from shared.errors.shipping_address_errors import err_grpc_invalid_id


class ShippingCommandHandler(
    shipping_address_command_pb2_grpc.ShippingCommandServiceServicer
):
    def __init__(self, service: ShippingAddressCommandService, logger: Logger) -> None:
        self._service = service
        self.logger = logger

    @grpc_method("ShippingCommandService.CreateShipping", SERVICE_NAME)
    async def CreateShipping(self, request: Any, context: Any) -> Any:
        create_request = CreateShippingAddressRequest(
            order_id=request.order_id,
            alamat=request.alamat,
            provinsi=request.provinsi,
            negara=request.negara,
            kota=request.kota,
            courier=request.courier,
            shipping_method=request.shipping_method,
            shipping_cost=request.shipping_cost,
        )
        row = await self._service.create(create_request)

        response = shipping_address_common_pb2.ApiResponseShipping(
            status="success", message="Successfully created shipping address"
        )
        fill_shipping_response(response.data, row)
        return response

    @grpc_method("ShippingCommandService.UpdateShipping", SERVICE_NAME)
    async def UpdateShipping(self, request: Any, context: Any) -> Any:
        update_request = UpdateShippingAddressRequest(
            shipping_id=request.shipping_id,
            order_id=request.order_id,
            alamat=request.alamat,
            provinsi=request.provinsi,
            negara=request.negara,
            kota=request.kota,
            courier=request.courier,
            shipping_method=request.shipping_method,
            shipping_cost=request.shipping_cost,
        )
        row = await self._service.update(update_request)

        response = shipping_address_common_pb2.ApiResponseShipping(
            status="success", message="Successfully updated shipping address"
        )
        fill_shipping_response(response.data, row)
        return response

    @grpc_method("ShippingCommandService.TrashedShipping", SERVICE_NAME)
    async def TrashedShipping(self, request: Any, context: Any) -> Any:
        if request.id == 0:
            raise err_grpc_invalid_id
        row = await self._service.trash(int(request.id))

        response = shipping_address_common_pb2.ApiResponseShippingDeleteAt(
            status="success", message="Successfully trashed shipping address"
        )
        fill_shipping_response_delete_at(response.data, row)
        return response

    @grpc_method("ShippingCommandService.RestoreShipping", SERVICE_NAME)
    async def RestoreShipping(self, request: Any, context: Any) -> Any:
        if request.id == 0:
            raise err_grpc_invalid_id
        row = await self._service.restore(int(request.id))

        response = shipping_address_common_pb2.ApiResponseShippingDeleteAt(
            status="success", message="Successfully restored shipping address"
        )
        fill_shipping_response_delete_at(response.data, row)
        return response

    @grpc_method("ShippingCommandService.DeleteShippingPermanent", SERVICE_NAME)
    async def DeleteShippingPermanent(self, request: Any, context: Any) -> Any:
        if request.id == 0:
            raise err_grpc_invalid_id
        await self._service.delete_permanent(int(request.id))

        return shipping_address_common_pb2.ApiResponseShippingDelete(
            status="success",
            message="Successfully deleted shipping address permanently",
        )

    @grpc_method("ShippingCommandService.RestoreAllShipping", SERVICE_NAME)
    async def RestoreAllShipping(self, request: Any, context: Any) -> Any:
        await self._service.restore_all()
        return shipping_address_common_pb2.ApiResponseShippingAll(
            status="success", message="Successfully restored all shipping addresses"
        )

    @grpc_method("ShippingCommandService.DeleteShippingByOrderPermanent", SERVICE_NAME)
    async def DeleteShippingByOrderPermanent(self, request: Any, context: Any) -> Any:
        if request.id == 0:
            raise err_grpc_invalid_id
        await self._service.delete_by_order_id_permanent(int(request.id))

        return shipping_address_common_pb2.ApiResponseShippingDelete(
            status="success",
            message="Successfully deleted shipping addresses by order permanently",
        )

    @grpc_method("ShippingCommandService.DeleteAllShippingPermanent", SERVICE_NAME)
    async def DeleteAllShippingPermanent(self, request: Any, context: Any) -> Any:
        await self._service.delete_all()
        return shipping_address_common_pb2.ApiResponseShippingAll(
            status="success",
            message="Successfully deleted all shipping addresses permanently",
        )


__all__ = ["ShippingCommandHandler"]

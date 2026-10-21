"""Merchant command gRPC handler. Id-carrying commands guard `id == 0` with `err_grpc_invalid_merchant_id` (400). `Create`/`Update`/`UpdateStatus` validate the request body; a validation failure raises the matching sentinel. Note that `UpdateStatus` uses `err_grpc_validate_update_merchant` (not the status-specific sentinel), exactly. Every other failure is propagated and mapped by `grpc_method`."""

from __future__ import annotations

from typing import Any

from pydantic import ValidationError

from pb.merchant import merchant_command_pb2_grpc, merchant_common_pb2
from pkg.logger.logger import Logger
from pkg.middleware import grpc_method
from service.merchant.handler.mapping import (
    fill_merchant_response,
    fill_merchant_response_delete_at,
)
from service.merchant.service.interfaces import MerchantCommandService
from service.merchant.service.service import SERVICE_NAME
from shared.domain.requests.merchant import (
    CreateMerchantRequest,
    UpdateMerchantRequest,
    UpdateMerchantStatusRequest,
)
from shared.errors.merchant_errors import (
    err_grpc_invalid_merchant_id,
    err_grpc_validate_create_merchant,
    err_grpc_validate_update_merchant,
)


class MerchantCommandHandler(
    merchant_command_pb2_grpc.MerchantCommandServiceServicer
):
    def __init__(self, service: MerchantCommandService, logger: Logger) -> None:
        self._service = service
        self.logger = logger

    @grpc_method("MerchantCommandService.Create", SERVICE_NAME)
    async def Create(self, request: Any, context: Any) -> Any:
        try:
            create_request = CreateMerchantRequest(
                user_id=request.user_id,
                name=request.name,
                description=request.description,
                address=request.address,
                contact_email=request.contact_email,
                contact_phone=request.contact_phone,
                status=request.status,
            )
        except ValidationError as exc:
            raise err_grpc_validate_create_merchant from exc
        merchant = await self._service.create(create_request)
        response = merchant_common_pb2.ApiResponseMerchant(
            status="success", message="Successfully created merchant"
        )
        fill_merchant_response(response.data, merchant)
        return response

    @grpc_method("MerchantCommandService.Update", SERVICE_NAME)
    async def Update(self, request: Any, context: Any) -> Any:
        if request.merchant_id == 0:
            raise err_grpc_invalid_merchant_id
        try:
            update_request = UpdateMerchantRequest(
                merchant_id=request.merchant_id,
                user_id=request.user_id,
                name=request.name,
                description=request.description,
                address=request.address,
                contact_email=request.contact_email,
                contact_phone=request.contact_phone,
                status=request.status,
            )
        except ValidationError as exc:
            raise err_grpc_validate_update_merchant from exc
        merchant = await self._service.update(update_request)
        response = merchant_common_pb2.ApiResponseMerchant(
            status="success", message="Successfully updated merchant"
        )
        fill_merchant_response(response.data, merchant)
        return response

    @grpc_method("MerchantCommandService.UpdateStatus", SERVICE_NAME)
    async def UpdateStatus(self, request: Any, context: Any) -> Any:
        if request.merchant_id == 0:
            raise err_grpc_invalid_merchant_id
        try:
            status_request = UpdateMerchantStatusRequest(
                merchant_id=request.merchant_id, status=request.status
            )
        except ValidationError as exc:
            # uses ErrGrpcValidateUpdateMerchant here (not the status-specific
            # sentinel); the status-specific one is unused dead code.
            raise err_grpc_validate_update_merchant from exc
        merchant = await self._service.update_status(status_request)
        response = merchant_common_pb2.ApiResponseMerchant(
            status="success", message="Successfully updated merchant status"
        )
        fill_merchant_response(response.data, merchant)
        return response

    @grpc_method("MerchantCommandService.TrashedMerchant", SERVICE_NAME)
    async def TrashedMerchant(self, request: Any, context: Any) -> Any:
        if request.id == 0:
            raise err_grpc_invalid_merchant_id
        merchant = await self._service.trash(request.id)
        response = merchant_common_pb2.ApiResponseMerchantDeleteAt(
            status="success", message="Successfully trashed merchant"
        )
        fill_merchant_response_delete_at(response.data, merchant)
        return response

    @grpc_method("MerchantCommandService.RestoreMerchant", SERVICE_NAME)
    async def RestoreMerchant(self, request: Any, context: Any) -> Any:
        if request.id == 0:
            raise err_grpc_invalid_merchant_id
        merchant = await self._service.restore(request.id)
        response = merchant_common_pb2.ApiResponseMerchant(
            status="success", message="Successfully restored merchant"
        )
        fill_merchant_response(response.data, merchant)
        return response

    @grpc_method("MerchantCommandService.DeleteMerchantPermanent", SERVICE_NAME)
    async def DeleteMerchantPermanent(self, request: Any, context: Any) -> Any:
        if request.id == 0:
            raise err_grpc_invalid_merchant_id
        await self._service.delete_permanent(request.id)
        return merchant_common_pb2.ApiResponseMerchantDelete(
            status="success", message="Successfully deleted merchant permanently"
        )

    @grpc_method("MerchantCommandService.RestoreAllMerchant", SERVICE_NAME)
    async def RestoreAllMerchant(self, request: Any, context: Any) -> Any:
        await self._service.restore_all()
        return merchant_common_pb2.ApiResponseMerchantAll(
            status="success", message="Successfully restored all merchants"
        )

    @grpc_method("MerchantCommandService.DeleteAllMerchantPermanent", SERVICE_NAME)
    async def DeleteAllMerchantPermanent(self, request: Any, context: Any) -> Any:
        await self._service.delete_all()
        return merchant_common_pb2.ApiResponseMerchantAll(
            status="success", message="Successfully deleted all merchants permanently"
        )


__all__ = ["MerchantCommandHandler"]

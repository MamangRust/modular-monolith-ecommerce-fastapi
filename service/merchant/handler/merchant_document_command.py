"""Merchant document command gRPC handler. Id-carrying commands guard `document_id == 0` with `err_grpc_merchant_invalid_id` (400). `Create` maps a validation failure to `err_grpc_validate_create_merchant_document`; `Update`/`UpdateStatus` map a validation failure to `err_grpc_failed_update_merchant_document` (500, exactly). The `Trashed`/`Restore` responses reuse `MerchantDocument` (no deleted-at wrapper), matching the response types."""

from __future__ import annotations

from typing import Any

from pydantic import ValidationError

from pb.merchant_document import (
    merchant_document_command_pb2_grpc,
    merchant_document_common_pb2,
)
from pkg.logger.logger import Logger
from pkg.middleware import grpc_method
from service.merchant.handler.mapping import fill_merchant_document
from service.merchant.service.interfaces import MerchantDocumentCommandService
from service.merchant.service.service import SERVICE_NAME
from shared.domain.requests.merchant import (
    CreateMerchantDocumentRequest,
    UpdateMerchantDocumentRequest,
    UpdateMerchantDocumentStatusRequest,
)
from shared.errors.merchant_errors import (
    err_grpc_failed_update_merchant_document,
    err_grpc_merchant_invalid_id,
    err_grpc_validate_create_merchant_document,
)


class MerchantDocumentCommandHandler(
    merchant_document_command_pb2_grpc.MerchantDocumentCommandServiceServicer
):
    def __init__(self, service: MerchantDocumentCommandService, logger: Logger) -> None:
        self._service = service
        self.logger = logger

    @grpc_method("MerchantDocumentCommandService.Create", SERVICE_NAME)
    async def Create(self, request: Any, context: Any) -> Any:
        try:
            create_request = CreateMerchantDocumentRequest(
                merchant_id=request.merchant_id,
                document_type=request.document_type,
                document_url=request.document_url,
            )
        except ValidationError as exc:
            raise err_grpc_validate_create_merchant_document from exc
        document = await self._service.create(create_request)
        response = merchant_document_common_pb2.ApiResponseMerchantDocument(
            status="success", message="Successfully created merchant document"
        )
        fill_merchant_document(response.data, document)
        return response

    @grpc_method("MerchantDocumentCommandService.Update", SERVICE_NAME)
    async def Update(self, request: Any, context: Any) -> Any:
        if request.document_id == 0:
            raise err_grpc_merchant_invalid_id
        try:
            update_request = UpdateMerchantDocumentRequest(
                document_id=request.document_id,
                merchant_id=request.merchant_id,
                document_type=request.document_type,
                document_url=request.document_url,
                status=request.status,
                note=request.note,
            )
        except ValidationError as exc:
            raise err_grpc_failed_update_merchant_document from exc
        document = await self._service.update(update_request)
        response = merchant_document_common_pb2.ApiResponseMerchantDocument(
            status="success", message="Successfully updated merchant document"
        )
        fill_merchant_document(response.data, document)
        return response

    @grpc_method("MerchantDocumentCommandService.UpdateStatus", SERVICE_NAME)
    async def UpdateStatus(self, request: Any, context: Any) -> Any:
        if request.document_id == 0:
            raise err_grpc_merchant_invalid_id
        try:
            status_request = UpdateMerchantDocumentStatusRequest(
                document_id=request.document_id,
                merchant_id=request.merchant_id,
                status=request.status,
                note=request.note,
            )
        except ValidationError as exc:
            raise err_grpc_failed_update_merchant_document from exc
        document = await self._service.update_status(status_request)
        response = merchant_document_common_pb2.ApiResponseMerchantDocument(
            status="success", message="Successfully updated merchant document status"
        )
        fill_merchant_document(response.data, document)
        return response

    @grpc_method("MerchantDocumentCommandService.Trashed", SERVICE_NAME)
    async def Trashed(self, request: Any, context: Any) -> Any:
        if request.document_id == 0:
            raise err_grpc_merchant_invalid_id
        document = await self._service.trash(request.document_id)
        response = merchant_document_common_pb2.ApiResponseMerchantDocument(
            status="success", message="Successfully trashed merchant document"
        )
        fill_merchant_document(response.data, document)
        return response

    @grpc_method("MerchantDocumentCommandService.Restore", SERVICE_NAME)
    async def Restore(self, request: Any, context: Any) -> Any:
        if request.document_id == 0:
            raise err_grpc_merchant_invalid_id
        document = await self._service.restore(request.document_id)
        response = merchant_document_common_pb2.ApiResponseMerchantDocument(
            status="success", message="Successfully restored merchant document"
        )
        fill_merchant_document(response.data, document)
        return response

    @grpc_method("MerchantDocumentCommandService.DeletePermanent", SERVICE_NAME)
    async def DeletePermanent(self, request: Any, context: Any) -> Any:
        if request.document_id == 0:
            raise err_grpc_merchant_invalid_id
        await self._service.delete_permanent(request.document_id)
        return merchant_document_common_pb2.ApiResponseMerchantDocumentDelete(
            status="success",
            message="Successfully permanently deleted merchant document",
        )

    @grpc_method("MerchantDocumentCommandService.RestoreAll", SERVICE_NAME)
    async def RestoreAll(self, request: Any, context: Any) -> Any:
        await self._service.restore_all()
        return merchant_document_common_pb2.ApiResponseMerchantDocumentAll(
            status="success", message="Successfully restored all merchant documents"
        )

    @grpc_method("MerchantDocumentCommandService.DeleteAllPermanent", SERVICE_NAME)
    async def DeleteAllPermanent(self, request: Any, context: Any) -> Any:
        await self._service.delete_all()
        return merchant_document_common_pb2.ApiResponseMerchantDocumentAll(
            status="success",
            message="Successfully permanently deleted all merchant documents",
        )


__all__ = ["MerchantDocumentCommandHandler"]

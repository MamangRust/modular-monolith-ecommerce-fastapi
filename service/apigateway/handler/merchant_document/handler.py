"""Gateway merchant-document handler: REST <-> merchant_document gRPC. `Create`/`Update` are multipart form endpoints. the gateway validates the form itself (merchant_id > 0 else 400 "Invalid merchant ID"; a non-empty document_type else "Document type is required"; a required file on create else "Document file is required") and uploads through `upload_image`; replicates that here. `Update` uploads into `uploads/merchant_document/files` and falls back to the `document_url_old` form field when no new file is sent. `UpdateStatus` is a JSON body endpoint."""

from __future__ import annotations

from typing import Any

import grpc
from google.protobuf import empty_pb2

from pb.merchant_document import (
    merchant_document_command_pb2,
    merchant_document_command_pb2_grpc,
    merchant_document_query_pb2,
    merchant_document_query_pb2_grpc,
)
from pkg.upload_image import ImageUpload
from service.apigateway.app.client import ServiceConnections
from shared.errors import new_bad_request_error, parse_grpc_error
from shared.mapper.merchant import (
    to_api_response_merchant_document,
    to_api_response_merchant_document_all,
    to_api_response_merchant_document_delete,
    to_api_response_pagination_merchant_document,
    to_api_response_pagination_merchant_document_delete_at,
)

RPC_TIMEOUT = 30.0

_CREATE_UPLOAD_DIR = "uploads/merchant_document"
_UPDATE_UPLOAD_DIR = "uploads/merchant_document/files"


def require_positive_id(document_id: int) -> None:
    """Gateway guard for document routes: `id <= 0` -> 400 "Invalid ID". Unlike the merchant handler, the document gateway guards `id <= 0` on *both* the query `find_by_id` and every command route, so does too."""
    if document_id <= 0:
        raise new_bad_request_error("Invalid ID")


def parse_merchant_id(raw: Any) -> int:
    """Atoi(r.FormValue("merchant_id")` + `<= 0` guard."""
    try:
        merchant_id = int(raw)
    except (TypeError, ValueError):
        raise new_bad_request_error("Invalid merchant ID") from None
    if merchant_id <= 0:
        raise new_bad_request_error("Invalid merchant ID")
    return merchant_id


class MerchantDocumentHandler:
    def __init__(self, connections: ServiceConnections, upload: ImageUpload) -> None:
        channel = connections.channel("merchant")
        self._query = merchant_document_query_pb2_grpc.MerchantDocumentQueryServiceStub(
            channel
        )
        self._command = (
            merchant_document_command_pb2_grpc.MerchantDocumentCommandServiceStub(
                channel
            )
        )
        self._upload = upload

    # ---- query ----

    async def find_all(self, page: int, page_size: int, search: str):
        request = merchant_document_query_pb2.FindAllMerchantDocumentsRequest(
            page=page, page_size=page_size, search=search or ""
        )
        try:
            response = await self._query.FindAll(request, timeout=RPC_TIMEOUT)
        except grpc.aio.AioRpcError as exc:
            raise parse_grpc_error(exc) from exc
        return to_api_response_pagination_merchant_document(response)

    async def find_by_id(self, document_id: int):
        require_positive_id(document_id)
        request = merchant_document_query_pb2.FindMerchantDocumentByIdRequest(
            document_id=document_id
        )
        try:
            response = await self._query.FindById(request, timeout=RPC_TIMEOUT)
        except grpc.aio.AioRpcError as exc:
            raise parse_grpc_error(exc) from exc
        return to_api_response_merchant_document(response)

    async def find_all_active(self, page: int, page_size: int, search: str):
        request = merchant_document_query_pb2.FindAllMerchantDocumentsRequest(
            page=page, page_size=page_size, search=search or ""
        )
        try:
            response = await self._query.FindAllActive(request, timeout=RPC_TIMEOUT)
        except grpc.aio.AioRpcError as exc:
            raise parse_grpc_error(exc) from exc
        return to_api_response_pagination_merchant_document(response)

    async def find_all_trashed(self, page: int, page_size: int, search: str):
        request = merchant_document_query_pb2.FindAllMerchantDocumentsRequest(
            page=page, page_size=page_size, search=search or ""
        )
        try:
            response = await self._query.FindAllTrashed(request, timeout=RPC_TIMEOUT)
        except grpc.aio.AioRpcError as exc:
            raise parse_grpc_error(exc) from exc
        return to_api_response_pagination_merchant_document_delete_at(response)

    # ---- command ----

    async def create(
        self,
        merchant_id_raw: Any,
        document_type_raw: str,
        file: Any,
    ):
        merchant_id = parse_merchant_id(merchant_id_raw)
        document_type = (document_type_raw or "").strip()
        if not document_type:
            raise new_bad_request_error("Document type is required")
        if file is None:
            raise new_bad_request_error("Document file is required")

        document_url = await self._upload.process_image_upload(
            _CREATE_UPLOAD_DIR, file, True
        )
        request = merchant_document_command_pb2.CreateMerchantDocumentRequest(
            merchant_id=merchant_id,
            document_type=document_type,
            document_url=document_url,
        )
        try:
            response = await self._command.Create(request, timeout=RPC_TIMEOUT)
        except grpc.aio.AioRpcError as exc:
            raise parse_grpc_error(exc) from exc
        return to_api_response_merchant_document(response)

    async def update(
        self,
        document_id: int,
        merchant_id_raw: Any,
        document_type_raw: str,
        file: Any,
        document_url_old: str,
        status: str,
        note: str,
    ):
        require_positive_id(document_id)
        merchant_id = parse_merchant_id(merchant_id_raw)
        document_type = (document_type_raw or "").strip()
        if not document_type:
            raise new_bad_request_error("Document type is required")

        if file is not None:
            document_url = await self._upload.process_image_upload(
                _UPDATE_UPLOAD_DIR, file, True
            )
        else:
            document_url = document_url_old or ""

        request = merchant_document_command_pb2.UpdateMerchantDocumentRequest(
            document_id=document_id,
            merchant_id=merchant_id,
            document_type=document_type,
            document_url=document_url,
            status=status or "",
            note=note or "",
        )
        try:
            response = await self._command.Update(request, timeout=RPC_TIMEOUT)
        except grpc.aio.AioRpcError as exc:
            raise parse_grpc_error(exc) from exc
        return to_api_response_merchant_document(response)

    async def update_status(
        self,
        document_id: int,
        merchant_id: int,
        status: str,
        note: str,
    ):
        require_positive_id(document_id)
        request = merchant_document_command_pb2.UpdateMerchantDocumentStatusRequest(
            document_id=document_id,
            merchant_id=merchant_id,
            status=status,
            note=note,
        )
        try:
            response = await self._command.UpdateStatus(request, timeout=RPC_TIMEOUT)
        except grpc.aio.AioRpcError as exc:
            raise parse_grpc_error(exc) from exc
        return to_api_response_merchant_document(response)

    async def trash(self, document_id: int):
        require_positive_id(document_id)
        request = merchant_document_command_pb2.TrashedMerchantDocumentRequest(
            document_id=document_id
        )
        try:
            response = await self._command.Trashed(request, timeout=RPC_TIMEOUT)
        except grpc.aio.AioRpcError as exc:
            raise parse_grpc_error(exc) from exc
        return to_api_response_merchant_document(response)

    async def restore(self, document_id: int):
        require_positive_id(document_id)
        request = merchant_document_command_pb2.RestoreMerchantDocumentRequest(
            document_id=document_id
        )
        try:
            response = await self._command.Restore(request, timeout=RPC_TIMEOUT)
        except grpc.aio.AioRpcError as exc:
            raise parse_grpc_error(exc) from exc
        return to_api_response_merchant_document(response)

    async def delete_permanent(self, document_id: int):
        require_positive_id(document_id)
        request = (
            merchant_document_command_pb2.DeleteMerchantDocumentPermanentRequest(
                document_id=document_id
            )
        )
        try:
            response = await self._command.DeletePermanent(
                request, timeout=RPC_TIMEOUT
            )
        except grpc.aio.AioRpcError as exc:
            raise parse_grpc_error(exc) from exc
        return to_api_response_merchant_document_delete(response)

    async def restore_all(self):
        try:
            response = await self._command.RestoreAll(
                empty_pb2.Empty(), timeout=RPC_TIMEOUT
            )
        except grpc.aio.AioRpcError as exc:
            raise parse_grpc_error(exc) from exc
        return to_api_response_merchant_document_all(response)

    async def delete_all_permanent(self):
        try:
            response = await self._command.DeleteAllPermanent(
                empty_pb2.Empty(), timeout=RPC_TIMEOUT
            )
        except grpc.aio.AioRpcError as exc:
            raise parse_grpc_error(exc) from exc
        return to_api_response_merchant_document_all(response)


__all__ = [
    "MerchantDocumentHandler",
    "parse_merchant_id",
    "require_positive_id",
]

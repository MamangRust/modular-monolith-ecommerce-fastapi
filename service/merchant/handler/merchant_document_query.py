"""Merchant document query gRPC handler.

`FindById` guards `document_id == 0` with `err_grpc_merchant_invalid_id` (400,
"invalid ID provided"). `FindAll`/`FindAllActive` return
`ApiResponsePaginationMerchantDocument`; `FindAllTrashed` returns
`ApiResponsePaginationMerchantDocumentAt` (delete-at rows)."""

from __future__ import annotations

from typing import Any

from pb.merchant_document import (
    merchant_document_common_pb2,
    merchant_document_query_pb2_grpc,
)
from pkg.logger.logger import Logger
from pkg.middleware import grpc_method
from service.merchant.handler.mapping import (
    fill_merchant_document,
    fill_merchant_document_delete_at,
    normalize_page,
    pagination_meta,
)
from service.merchant.service.interfaces import MerchantDocumentQueryService
from service.merchant.service.service import SERVICE_NAME
from shared.errors.merchant_errors import err_grpc_merchant_invalid_id


class MerchantDocumentQueryHandler(
    merchant_document_query_pb2_grpc.MerchantDocumentQueryServiceServicer
):
    def __init__(self, service: MerchantDocumentQueryService, logger: Logger) -> None:
        self._service = service
        self.logger = logger

    @grpc_method("MerchantDocumentQueryService.FindAll", SERVICE_NAME)
    async def FindAll(self, request: Any, context: Any) -> Any:
        page, page_size = normalize_page(request.page, request.page_size)
        rows, total = await self._service.find_all(request.search, page, page_size)
        response = merchant_document_common_pb2.ApiResponsePaginationMerchantDocument(
            status="success", message="Successfully fetched merchant documents"
        )
        for row in rows:
            fill_merchant_document(response.data.add(), row)
        response.pagination.CopyFrom(pagination_meta(page, page_size, total))
        return response

    @grpc_method("MerchantDocumentQueryService.FindById", SERVICE_NAME)
    async def FindById(self, request: Any, context: Any) -> Any:
        if request.document_id == 0:
            raise err_grpc_merchant_invalid_id
        document = await self._service.find_by_id(request.document_id)
        response = merchant_document_common_pb2.ApiResponseMerchantDocument(
            status="success", message="Successfully fetched merchant document"
        )
        fill_merchant_document(response.data, document)
        return response

    @grpc_method("MerchantDocumentQueryService.FindAllActive", SERVICE_NAME)
    async def FindAllActive(self, request: Any, context: Any) -> Any:
        page, page_size = normalize_page(request.page, request.page_size)
        rows, total = await self._service.find_active(request.search, page, page_size)
        response = merchant_document_common_pb2.ApiResponsePaginationMerchantDocument(
            status="success", message="Successfully fetched active merchant documents"
        )
        for row in rows:
            fill_merchant_document(response.data.add(), row)
        response.pagination.CopyFrom(pagination_meta(page, page_size, total))
        return response

    @grpc_method("MerchantDocumentQueryService.FindAllTrashed", SERVICE_NAME)
    async def FindAllTrashed(self, request: Any, context: Any) -> Any:
        page, page_size = normalize_page(request.page, request.page_size)
        rows, total = await self._service.find_trashed(request.search, page, page_size)
        response = merchant_document_common_pb2.ApiResponsePaginationMerchantDocumentAt(
            status="success", message="Successfully fetched trashed merchant documents"
        )
        for row in rows:
            fill_merchant_document_delete_at(response.data.add(), row)
        response.pagination.CopyFrom(pagination_meta(page, page_size, total))
        return response


__all__ = ["MerchantDocumentQueryHandler"]

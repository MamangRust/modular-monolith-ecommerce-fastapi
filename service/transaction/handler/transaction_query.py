"""transaction query gRPC handler."""

from __future__ import annotations

from typing import Any

from pb.transaction import transaction_common_pb2, transaction_query_pb2_grpc
from pkg.logger.logger import Logger
from pkg.middleware import grpc_method
from service.transaction.handler.mapping import (
    fill_transaction_response,
    fill_transaction_response_delete_at,
    normalize_page,
    pagination_meta,
)
from service.transaction.service.interfaces import TransactionQueryService
from service.transaction.service.service import SERVICE_NAME
from shared.domain.requests.transaction import (
    FindAllTransaction,
    FindAllTransactionByMerchant,
)


class TransactionQueryHandler(transaction_query_pb2_grpc.TransactionQueryServiceServicer):
    def __init__(self, service: TransactionQueryService, logger: Logger) -> None:
        self._service = service
        self.logger = logger

    @grpc_method("TransactionQueryService.FindAllTransactions", SERVICE_NAME)
    async def FindAllTransactions(self, request: Any, context: Any) -> Any:
        page, page_size = normalize_page(request.page, request.page_size)
        rows, total = await self._service.find_all(
            FindAllTransaction(search=request.search, page=page, page_size=page_size)
        )
        response = transaction_common_pb2.ApiResponsePaginationTransaction(
            status="success", message="Successfully fetched transactions"
        )
        for row in rows:
            fill_transaction_response(response.data.add(), row)
        response.pagination.CopyFrom(pagination_meta(page, page_size, total))
        return response

    @grpc_method("TransactionQueryService.FindByMerchant", SERVICE_NAME)
    async def FindByMerchant(self, request: Any, context: Any) -> Any:
        page, page_size = normalize_page(request.page, request.page_size)
        rows, total = await self._service.find_by_merchant(
            FindAllTransactionByMerchant(
                merchant_id=request.merchant_id,
                search=request.search,
                page=page,
                page_size=page_size,
            )
        )
        response = transaction_common_pb2.ApiResponsePaginationTransaction(
            status="success", message="Successfully fetched transactions by merchant"
        )
        for row in rows:
            fill_transaction_response(response.data.add(), row)
        response.pagination.CopyFrom(pagination_meta(page, page_size, total))
        return response

    @grpc_method("TransactionQueryService.FindById", SERVICE_NAME)
    async def FindById(self, request: Any, context: Any) -> Any:
        row = await self._service.find_by_id(int(request.id))
        response = transaction_common_pb2.ApiResponseTransaction(
            status="success", message="Successfully fetched transaction"
        )
        fill_transaction_response(response.data, row)
        return response

    @grpc_method("TransactionQueryService.FindByOrderId", SERVICE_NAME)
    async def FindByOrderId(self, request: Any, context: Any) -> Any:
        row = await self._service.find_by_order_id(int(request.order_id))
        response = transaction_common_pb2.ApiResponseTransaction(
            status="success", message="Successfully fetched transaction by order id"
        )
        fill_transaction_response(response.data, row)
        return response

    @grpc_method("TransactionQueryService.FindByActive", SERVICE_NAME)
    async def FindByActive(self, request: Any, context: Any) -> Any:
        page, page_size = normalize_page(request.page, request.page_size)
        rows, total = await self._service.find_active(
            FindAllTransaction(search=request.search, page=page, page_size=page_size)
        )
        response = transaction_common_pb2.ApiResponsePaginationTransaction(
            status="success", message="Successfully fetched active transactions"
        )
        for row in rows:
            fill_transaction_response(response.data.add(), row)
        response.pagination.CopyFrom(pagination_meta(page, page_size, total))
        return response

    @grpc_method("TransactionQueryService.FindByTrashed", SERVICE_NAME)
    async def FindByTrashed(self, request: Any, context: Any) -> Any:
        page, page_size = normalize_page(request.page, request.page_size)
        rows, total = await self._service.find_trashed(
            FindAllTransaction(search=request.search, page=page, page_size=page_size)
        )
        response = transaction_common_pb2.ApiResponsePaginationTransactionDeleteAt(
            status="success", message="Successfully fetched trashed transactions"
        )
        for row in rows:
            fill_transaction_response_delete_at(response.data.add(), row)
        response.pagination.CopyFrom(pagination_meta(page, page_size, total))
        return response


__all__ = ["TransactionQueryHandler"]

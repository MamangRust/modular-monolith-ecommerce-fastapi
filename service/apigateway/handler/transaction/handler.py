"""Gateway transaction handler: REST <-> transaction gRPC. Only transport concerns live here: build the proto request, call the domain over gRPC, convert a gRPC failure back to its original AppError, and map the proto response to the shared response envelope. No SQL, no business rules. Like the other domains, deliberately does not cache in the gateway. gateway transaction handlers cache under their own `transaction:` namespace and invalidate on every mutation; drops that layer, so every request goes straight to the transaction service, which serves/invalidates its own cache. `Create` decodes the **JSON body** (`httpx.Bind` is a JSON decoder — the swagger `mpfd` annotation is stale) and returns **201** (`http.StatusCreated`). `Update` reads `payment_status` from `FormValue("status")` — the URL query first, then an urlencoded/multipart form field — and sends only the id + status. Path-id guards reproduce verbatim: query `FindById` → 400 "Invalid Transaction ID", `FindByMerchant` → 400 "Invalid Merchant ID", command routes → 400 "Invalid ID"."""

from __future__ import annotations

import grpc
from google.protobuf import empty_pb2

from pb.transaction import (
    transaction_command_pb2,
    transaction_command_pb2_grpc,
    transaction_common_pb2,
    transaction_query_pb2,
    transaction_query_pb2_grpc,
)
from pb.transaction.stats import (
    transaction_stats_bymerchant_pb2,
    transaction_stats_bymerchant_pb2_grpc,
    transaction_stats_pb2,
    transaction_stats_pb2_grpc,
)
from service.apigateway.app.client import ServiceConnections
from shared.domain.requests.transaction import CreateTransactionRequest
from shared.domain.response.transaction import (
    TransactionMonthlyAmountFailedApi,
    TransactionMonthlyAmountSuccessApi,
    TransactionMonthlyMethodApi,
    TransactionResponseAll,
    TransactionResponseApi,
    TransactionResponseDelete,
    TransactionResponseDeleteAtApi,
    TransactionResponsePagination,
    TransactionResponsePaginationDeleteAt,
    TransactionYearlyAmountFailedApi,
    TransactionYearlyAmountSuccessApi,
    TransactionYearlyMethodApi,
)
from shared.errors import parse_grpc_error
from shared.mapper.transaction import (
    to_api_response_monthly_amount_failed,
    to_api_response_monthly_amount_success,
    to_api_response_monthly_method,
    to_api_response_pagination_transaction,
    to_api_response_pagination_transaction_delete_at,
    to_api_response_transaction,
    to_api_response_transaction_all,
    to_api_response_transaction_delete,
    to_api_response_transaction_delete_at,
    to_api_response_yearly_amount_failed,
    to_api_response_yearly_amount_success,
    to_api_response_yearly_method,
)

RPC_TIMEOUT = 30.0


def normalize_pagination(page: int, page_size: int) -> tuple[int, int]:
    """Gateway-side clamping."""
    if page <= 0:
        page = 1
    if page_size <= 0:
        page_size = 10
    return page, page_size


class TransactionHandler:
    def __init__(self, connections: ServiceConnections) -> None:
        channel = connections.channel("transaction")
        self._query = transaction_query_pb2_grpc.TransactionQueryServiceStub(channel)
        self._command = (
            transaction_command_pb2_grpc.TransactionCommandServiceStub(channel)
        )
        self._stats = transaction_stats_pb2_grpc.TransactionStatsServiceStub(channel)
        self._stats_by_merchant = (
            transaction_stats_bymerchant_pb2_grpc.TransactionStatsByMerchantServiceStub(
                channel
            )
        )

    # ---- query ----

    async def find_all(
        self, page: int, page_size: int, search: str
    ) -> TransactionResponsePagination:
        page, page_size = normalize_pagination(page, page_size)
        request = transaction_query_pb2.FindAllTransactionRequest(
            page=page, page_size=page_size, search=search or ""
        )
        try:
            response = await self._query.FindAllTransactions(
                request, timeout=RPC_TIMEOUT
            )
        except grpc.aio.AioRpcError as exc:
            raise parse_grpc_error(exc) from exc
        return to_api_response_pagination_transaction(response)

    async def find_by_id(self, transaction_id: int) -> TransactionResponseApi:
        request = transaction_common_pb2.FindByIdTransactionRequest(
            id=transaction_id
        )
        try:
            response = await self._query.FindById(request, timeout=RPC_TIMEOUT)
        except grpc.aio.AioRpcError as exc:
            raise parse_grpc_error(exc) from exc
        return to_api_response_transaction(response)

    async def find_by_merchant(
        self, merchant_id: int, page: int, page_size: int, search: str
    ) -> TransactionResponsePagination:
        page, page_size = normalize_pagination(page, page_size)
        request = transaction_query_pb2.FindAllTransactionByMerchantRequest(
            merchant_id=merchant_id,
            page=page,
            page_size=page_size,
            search=search or "",
        )
        try:
            response = await self._query.FindByMerchant(
                request, timeout=RPC_TIMEOUT
            )
        except grpc.aio.AioRpcError as exc:
            raise parse_grpc_error(exc) from exc
        return to_api_response_pagination_transaction(response)

    async def find_by_active(
        self, page: int, page_size: int, search: str
    ) -> TransactionResponsePagination:
        page, page_size = normalize_pagination(page, page_size)
        request = transaction_query_pb2.FindAllTransactionRequest(
            page=page, page_size=page_size, search=search or ""
        )
        try:
            response = await self._query.FindByActive(request, timeout=RPC_TIMEOUT)
        except grpc.aio.AioRpcError as exc:
            raise parse_grpc_error(exc) from exc
        return to_api_response_pagination_transaction(response)

    async def find_by_trashed(
        self, page: int, page_size: int, search: str
    ) -> TransactionResponsePaginationDeleteAt:
        page, page_size = normalize_pagination(page, page_size)
        request = transaction_query_pb2.FindAllTransactionRequest(
            page=page, page_size=page_size, search=search or ""
        )
        try:
            response = await self._query.FindByTrashed(
                request, timeout=RPC_TIMEOUT
            )
        except grpc.aio.AioRpcError as exc:
            raise parse_grpc_error(exc) from exc
        return to_api_response_pagination_transaction_delete_at(response)

    # ---- command ----

    async def create(self, body: CreateTransactionRequest) -> TransactionResponseApi:
        request = transaction_command_pb2.CreateTransactionRequest(
            order_id=body.order_id,
            merchant_id=body.merchant_id,
            payment_method=body.payment_method,
            amount=body.amount,
            user_id=body.user_id,
            payment_status=body.payment_status or "",
        )
        try:
            response = await self._command.Create(request, timeout=RPC_TIMEOUT)
        except grpc.aio.AioRpcError as exc:
            raise parse_grpc_error(exc) from exc
        return to_api_response_transaction(response)

    async def update(
        self, transaction_id: int, payment_status: str
    ) -> TransactionResponseApi:
        request = transaction_command_pb2.UpdateTransactionRequest(
            transaction_id=transaction_id,
            payment_status=payment_status or "",
        )
        try:
            response = await self._command.Update(request, timeout=RPC_TIMEOUT)
        except grpc.aio.AioRpcError as exc:
            raise parse_grpc_error(exc) from exc
        return to_api_response_transaction(response)

    async def trash(self, transaction_id: int) -> TransactionResponseDeleteAtApi:
        request = transaction_common_pb2.FindByIdTransactionRequest(
            id=transaction_id
        )
        try:
            response = await self._command.TrashedTransaction(
                request, timeout=RPC_TIMEOUT
            )
        except grpc.aio.AioRpcError as exc:
            raise parse_grpc_error(exc) from exc
        return to_api_response_transaction_delete_at(response)

    async def restore(self, transaction_id: int) -> TransactionResponseDeleteAtApi:
        request = transaction_common_pb2.FindByIdTransactionRequest(
            id=transaction_id
        )
        try:
            response = await self._command.RestoreTransaction(
                request, timeout=RPC_TIMEOUT
            )
        except grpc.aio.AioRpcError as exc:
            raise parse_grpc_error(exc) from exc
        return to_api_response_transaction_delete_at(response)

    async def delete_permanent(self, transaction_id: int) -> TransactionResponseDelete:
        request = transaction_common_pb2.FindByIdTransactionRequest(
            id=transaction_id
        )
        try:
            response = await self._command.DeleteTransactionPermanent(
                request, timeout=RPC_TIMEOUT
            )
        except grpc.aio.AioRpcError as exc:
            raise parse_grpc_error(exc) from exc
        return to_api_response_transaction_delete(response)

    async def restore_all(self) -> TransactionResponseAll:
        try:
            response = await self._command.RestoreAllTransaction(
                empty_pb2.Empty(), timeout=RPC_TIMEOUT
            )
        except grpc.aio.AioRpcError as exc:
            raise parse_grpc_error(exc) from exc
        return to_api_response_transaction_all(response)

    async def delete_by_order_permanent(
        self, order_id: int
    ) -> TransactionResponseDelete:
        request = transaction_common_pb2.FindByIdTransactionRequest(id=order_id)
        try:
            response = await self._command.DeleteTransactionByOrderPermanent(
                request, timeout=RPC_TIMEOUT
            )
        except grpc.aio.AioRpcError as exc:
            raise parse_grpc_error(exc) from exc
        return to_api_response_transaction_delete(response)

    async def delete_all_permanent(self) -> TransactionResponseAll:
        try:
            response = await self._command.DeleteAllTransactionPermanent(
                empty_pb2.Empty(), timeout=RPC_TIMEOUT
            )
        except grpc.aio.AioRpcError as exc:
            raise parse_grpc_error(exc) from exc
        return to_api_response_transaction_all(response)

    # ---- stats (global) ----

    async def find_monthly_amount_success(
        self, year: int, month: int
    ) -> TransactionMonthlyAmountSuccessApi:
        request = transaction_stats_pb2.MonthAmountTransactionRequest(
            year=year, month=month
        )
        try:
            response = await self._stats.GetMonthlyAmountSuccess(
                request, timeout=RPC_TIMEOUT
            )
        except grpc.aio.AioRpcError as exc:
            raise parse_grpc_error(exc) from exc
        return to_api_response_monthly_amount_success(response)

    async def find_yearly_amount_success(
        self, year: int
    ) -> TransactionYearlyAmountSuccessApi:
        request = transaction_stats_pb2.YearAmountTransactionRequest(year=year)
        try:
            response = await self._stats.GetYearlyAmountSuccess(
                request, timeout=RPC_TIMEOUT
            )
        except grpc.aio.AioRpcError as exc:
            raise parse_grpc_error(exc) from exc
        return to_api_response_yearly_amount_success(response)

    async def find_monthly_amount_failed(
        self, year: int, month: int
    ) -> TransactionMonthlyAmountFailedApi:
        request = transaction_stats_pb2.MonthAmountTransactionRequest(
            year=year, month=month
        )
        try:
            response = await self._stats.GetMonthlyAmountFailed(
                request, timeout=RPC_TIMEOUT
            )
        except grpc.aio.AioRpcError as exc:
            raise parse_grpc_error(exc) from exc
        return to_api_response_monthly_amount_failed(response)

    async def find_yearly_amount_failed(
        self, year: int
    ) -> TransactionYearlyAmountFailedApi:
        request = transaction_stats_pb2.YearAmountTransactionRequest(year=year)
        try:
            response = await self._stats.GetYearlyAmountFailed(
                request, timeout=RPC_TIMEOUT
            )
        except grpc.aio.AioRpcError as exc:
            raise parse_grpc_error(exc) from exc
        return to_api_response_yearly_amount_failed(response)

    async def find_monthly_method_success(
        self, year: int, month: int
    ) -> TransactionMonthlyMethodApi:
        request = transaction_stats_pb2.MonthMethodTransactionRequest(
            year=year, month=month
        )
        try:
            response = await self._stats.GetMonthlyTransactionMethodSuccess(
                request, timeout=RPC_TIMEOUT
            )
        except grpc.aio.AioRpcError as exc:
            raise parse_grpc_error(exc) from exc
        return to_api_response_monthly_method(response)

    async def find_yearly_method_success(
        self, year: int
    ) -> TransactionYearlyMethodApi:
        request = transaction_stats_pb2.YearMethodTransactionRequest(year=year)
        try:
            response = await self._stats.GetYearlyTransactionMethodSuccess(
                request, timeout=RPC_TIMEOUT
            )
        except grpc.aio.AioRpcError as exc:
            raise parse_grpc_error(exc) from exc
        return to_api_response_yearly_method(response)

    async def find_monthly_method_failed(
        self, year: int, month: int
    ) -> TransactionMonthlyMethodApi:
        request = transaction_stats_pb2.MonthMethodTransactionRequest(
            year=year, month=month
        )
        try:
            response = await self._stats.GetMonthlyTransactionMethodFailed(
                request, timeout=RPC_TIMEOUT
            )
        except grpc.aio.AioRpcError as exc:
            raise parse_grpc_error(exc) from exc
        return to_api_response_monthly_method(response)

    async def find_yearly_method_failed(
        self, year: int
    ) -> TransactionYearlyMethodApi:
        request = transaction_stats_pb2.YearMethodTransactionRequest(year=year)
        try:
            response = await self._stats.GetYearlyTransactionMethodFailed(
                request, timeout=RPC_TIMEOUT
            )
        except grpc.aio.AioRpcError as exc:
            raise parse_grpc_error(exc) from exc
        return to_api_response_yearly_method(response)

    # ---- stats (by merchant) ----

    async def find_monthly_amount_success_by_merchant(
        self, merchant_id: int, year: int, month: int
    ) -> TransactionMonthlyAmountSuccessApi:
        request = transaction_stats_bymerchant_pb2.MonthAmountTransactionMerchantRequest(
            merchant_id=merchant_id, year=year, month=month
        )
        try:
            response = (
                await self._stats_by_merchant.GetMonthlyAmountSuccessByMerchant(
                    request, timeout=RPC_TIMEOUT
                )
            )
        except grpc.aio.AioRpcError as exc:
            raise parse_grpc_error(exc) from exc
        return to_api_response_monthly_amount_success(response)

    async def find_yearly_amount_success_by_merchant(
        self, merchant_id: int, year: int
    ) -> TransactionYearlyAmountSuccessApi:
        request = transaction_stats_bymerchant_pb2.YearAmountTransactionMerchantRequest(
            merchant_id=merchant_id, year=year
        )
        try:
            response = (
                await self._stats_by_merchant.GetYearlyAmountSuccessByMerchant(
                    request, timeout=RPC_TIMEOUT
                )
            )
        except grpc.aio.AioRpcError as exc:
            raise parse_grpc_error(exc) from exc
        return to_api_response_yearly_amount_success(response)

    async def find_monthly_amount_failed_by_merchant(
        self, merchant_id: int, year: int, month: int
    ) -> TransactionMonthlyAmountFailedApi:
        request = transaction_stats_bymerchant_pb2.MonthAmountTransactionMerchantRequest(
            merchant_id=merchant_id, year=year, month=month
        )
        try:
            response = (
                await self._stats_by_merchant.GetMonthlyAmountFailedByMerchant(
                    request, timeout=RPC_TIMEOUT
                )
            )
        except grpc.aio.AioRpcError as exc:
            raise parse_grpc_error(exc) from exc
        return to_api_response_monthly_amount_failed(response)

    async def find_yearly_amount_failed_by_merchant(
        self, merchant_id: int, year: int
    ) -> TransactionYearlyAmountFailedApi:
        request = transaction_stats_bymerchant_pb2.YearAmountTransactionMerchantRequest(
            merchant_id=merchant_id, year=year
        )
        try:
            response = (
                await self._stats_by_merchant.GetYearlyAmountFailedByMerchant(
                    request, timeout=RPC_TIMEOUT
                )
            )
        except grpc.aio.AioRpcError as exc:
            raise parse_grpc_error(exc) from exc
        return to_api_response_yearly_amount_failed(response)

    async def find_monthly_method_success_by_merchant(
        self, merchant_id: int, year: int, month: int
    ) -> TransactionMonthlyMethodApi:
        request = transaction_stats_bymerchant_pb2.MonthMethodTransactionMerchantRequest(
            merchant_id=merchant_id, year=year, month=month
        )
        try:
            response = await self._stats_by_merchant.GetMonthlyTransactionMethodByMerchantSuccess(
                request, timeout=RPC_TIMEOUT
            )
        except grpc.aio.AioRpcError as exc:
            raise parse_grpc_error(exc) from exc
        return to_api_response_monthly_method(response)

    async def find_yearly_method_success_by_merchant(
        self, merchant_id: int, year: int
    ) -> TransactionYearlyMethodApi:
        request = transaction_stats_bymerchant_pb2.YearMethodTransactionMerchantRequest(
            merchant_id=merchant_id, year=year
        )
        try:
            response = await self._stats_by_merchant.GetYearlyTransactionMethodByMerchantSuccess(
                request, timeout=RPC_TIMEOUT
            )
        except grpc.aio.AioRpcError as exc:
            raise parse_grpc_error(exc) from exc
        return to_api_response_yearly_method(response)

    async def find_monthly_method_failed_by_merchant(
        self, merchant_id: int, year: int, month: int
    ) -> TransactionMonthlyMethodApi:
        request = transaction_stats_bymerchant_pb2.MonthMethodTransactionMerchantRequest(
            merchant_id=merchant_id, year=year, month=month
        )
        try:
            response = await self._stats_by_merchant.GetMonthlyTransactionMethodByMerchantFailed(
                request, timeout=RPC_TIMEOUT
            )
        except grpc.aio.AioRpcError as exc:
            raise parse_grpc_error(exc) from exc
        return to_api_response_monthly_method(response)

    async def find_yearly_method_failed_by_merchant(
        self, merchant_id: int, year: int
    ) -> TransactionYearlyMethodApi:
        request = transaction_stats_bymerchant_pb2.YearMethodTransactionMerchantRequest(
            merchant_id=merchant_id, year=year
        )
        try:
            response = await self._stats_by_merchant.GetYearlyTransactionMethodByMerchantFailed(
                request, timeout=RPC_TIMEOUT
            )
        except grpc.aio.AioRpcError as exc:
            raise parse_grpc_error(exc) from exc
        return to_api_response_yearly_method(response)


__all__ = ["TransactionHandler", "normalize_pagination"]

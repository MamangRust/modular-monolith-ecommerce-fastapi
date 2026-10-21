"""transaction command gRPC handler. `Create` always passes `payment_status` as a plain (possibly empty) string —.GetPaymentStatus}[0]`, a non-nil pointer the service treats as absent when empty."""

from __future__ import annotations

from typing import Any

from pb.transaction import (
    transaction_command_pb2_grpc,
    transaction_common_pb2,
)
from pkg.logger.logger import Logger
from pkg.middleware import grpc_method
from service.transaction.handler.mapping import (
    fill_transaction_response,
    fill_transaction_response_delete_at,
)
from service.transaction.service.interfaces import TransactionCommandService
from service.transaction.service.service import SERVICE_NAME
from shared.domain.requests.transaction import (
    CreateTransactionRequest,
    UpdateTransactionRequest,
)


class TransactionCommandHandler(
    transaction_command_pb2_grpc.TransactionCommandServiceServicer
):
    def __init__(self, service: TransactionCommandService, logger: Logger) -> None:
        self._service = service
        self.logger = logger

    @grpc_method("TransactionCommandService.Create", SERVICE_NAME)
    async def Create(self, request: Any, context: Any) -> Any:
        data = await self._service.create(
            CreateTransactionRequest(
                user_id=int(request.user_id),
                order_id=int(request.order_id),
                merchant_id=int(request.merchant_id),
                payment_method=request.payment_method,
                amount=int(request.amount),
                payment_status=request.payment_status,
            )
        )
        response = transaction_common_pb2.ApiResponseTransaction(
            status="success", message="Successfully created transaction"
        )
        fill_transaction_response(response.data, data)
        return response

    @grpc_method("TransactionCommandService.Update", SERVICE_NAME)
    async def Update(self, request: Any, context: Any) -> Any:
        data = await self._service.update(
            UpdateTransactionRequest(
                transaction_id=int(request.transaction_id),
                order_id=int(request.order_id),
                merchant_id=int(request.merchant_id),
                payment_method=request.payment_method,
                amount=int(request.amount),
                payment_status=request.payment_status,
            )
        )
        response = transaction_common_pb2.ApiResponseTransaction(
            status="success", message="Successfully updated transaction"
        )
        fill_transaction_response(response.data, data)
        return response

    @grpc_method("TransactionCommandService.TrashedTransaction", SERVICE_NAME)
    async def TrashedTransaction(self, request: Any, context: Any) -> Any:
        data = await self._service.trash(int(request.id))
        response = transaction_common_pb2.ApiResponseTransactionDeleteAt(
            status="success", message="Successfully trashed transaction"
        )
        fill_transaction_response_delete_at(response.data, data)
        return response

    @grpc_method("TransactionCommandService.RestoreTransaction", SERVICE_NAME)
    async def RestoreTransaction(self, request: Any, context: Any) -> Any:
        data = await self._service.restore(int(request.id))
        response = transaction_common_pb2.ApiResponseTransactionDeleteAt(
            status="success", message="Successfully restored transaction"
        )
        fill_transaction_response_delete_at(response.data, data)
        return response

    @grpc_method("TransactionCommandService.DeleteTransactionPermanent", SERVICE_NAME)
    async def DeleteTransactionPermanent(self, request: Any, context: Any) -> Any:
        await self._service.delete_permanent(int(request.id))
        return transaction_common_pb2.ApiResponseTransactionDelete(
            status="success",
            message="Successfully deleted transaction permanently",
        )

    @grpc_method("TransactionCommandService.RestoreAllTransaction", SERVICE_NAME)
    async def RestoreAllTransaction(self, request: Any, context: Any) -> Any:
        await self._service.restore_all()
        return transaction_common_pb2.ApiResponseTransactionAll(
            status="success",
            message="Successfully restored all transactions",
        )

    @grpc_method(
        "TransactionCommandService.DeleteTransactionByOrderPermanent", SERVICE_NAME
    )
    async def DeleteTransactionByOrderPermanent(
        self, request: Any, context: Any
    ) -> Any:
        await self._service.delete_by_order_id_permanent(int(request.id))
        return transaction_common_pb2.ApiResponseTransactionDelete(
            status="success",
            message="Successfully deleted transactions by order permanently",
        )

    @grpc_method(
        "TransactionCommandService.DeleteAllTransactionPermanent", SERVICE_NAME
    )
    async def DeleteAllTransactionPermanent(
        self, request: Any, context: Any
    ) -> Any:
        await self._service.delete_all()
        return transaction_common_pb2.ApiResponseTransactionAll(
            status="success",
            message="Successfully deleted all transactions permanently",
        )


__all__ = ["TransactionCommandHandler"]

"""Unit tests for the gateway transaction transport handler. `normalize_pagination` Matches the expected gateway clamp. keeps no gateway-level cache. `Update` reads the payment status via `_form_value` (query first, then form body — `FormValue`), and `create` builds the full body request."""

from __future__ import annotations

from typing import Any

import grpc
import pytest

from pb.transaction import (
    transaction_command_pb2,
    transaction_common_pb2,
    transaction_query_pb2,
)
from pb.transaction.stats import (
    transaction_stats_bymerchant_pb2,
    transaction_stats_pb2,
)
from service.apigateway.app.client import ServiceConnections
from service.apigateway.handler.transaction.handler import (
    TransactionHandler,
    normalize_pagination,
)
from shared.domain.requests.transaction import CreateTransactionRequest
from shared.errors import AppError


def _rpc_error(code: grpc.StatusCode, details: str) -> grpc.aio.AioRpcError:
    return grpc.aio.AioRpcError(
        code, grpc.aio.Metadata(), grpc.aio.Metadata(), details=details
    )


class FakeQuery:
    def __init__(self) -> None:
        self.last: Any = None
        self.fail = False

    async def FindAllTransactions(
        self, request: Any, timeout: float | None = None
    ) -> Any:
        self.last = request
        message = transaction_common_pb2.ApiResponsePaginationTransaction(
            status="success", message="Successfully fetched transactions"
        )
        message.data.add(
            id=1,
            order_id=42,
            merchant_id=3,
            payment_method="credit_card",
            amount=120000,
            payment_status="success",
            created_at="2026-01-02 03:04:05",
            updated_at="2026-01-03 04:05:06",
        )
        message.pagination.total_records = 1
        return message

    async def FindById(self, request: Any, timeout: float | None = None) -> Any:
        self.last = request
        if self.fail:
            raise _rpc_error(grpc.StatusCode.NOT_FOUND, "transaction not found")
        message = transaction_common_pb2.ApiResponseTransaction(
            status="success", message="Successfully fetched transaction"
        )
        message.data.id = request.id
        return message

    async def FindByMerchant(
        self, request: Any, timeout: float | None = None
    ) -> Any:
        self.last = request
        message = transaction_common_pb2.ApiResponsePaginationTransaction(
            status="success", message="Successfully fetched transactions by merchant"
        )
        message.data.add(id=2, merchant_id=request.merchant_id)
        return message

    async def FindByActive(
        self, request: Any, timeout: float | None = None
    ) -> Any:
        self.last = request
        message = transaction_common_pb2.ApiResponsePaginationTransaction(
            status="success", message="Successfully fetched active transactions"
        )
        return message

    async def FindByTrashed(
        self, request: Any, timeout: float | None = None
    ) -> Any:
        self.last = request
        message = transaction_common_pb2.ApiResponsePaginationTransactionDeleteAt(
            status="success", message="Successfully fetched trashed transactions"
        )
        message.data.add(
            id=3, deleted_at={"value": "2026-02-01 06:07:08"}
        )
        return message


class FakeCommand:
    def __init__(self) -> None:
        self.last: Any = None

    async def Create(self, request: Any, timeout: float | None = None) -> Any:
        self.last = request
        message = transaction_common_pb2.ApiResponseTransaction(
            status="success", message="Successfully created transaction"
        )
        message.data.id = 77
        return message

    async def Update(self, request: Any, timeout: float | None = None) -> Any:
        self.last = request
        message = transaction_common_pb2.ApiResponseTransaction(
            status="success", message="Successfully updated transaction"
        )
        message.data.id = request.transaction_id
        return message

    async def TrashedTransaction(
        self, request: Any, timeout: float | None = None
    ) -> Any:
        self.last = request
        message = transaction_common_pb2.ApiResponseTransactionDeleteAt(
            status="success", message="Successfully trashed transaction"
        )
        message.data.id = request.id
        message.data.deleted_at.value = "2026-02-01 06:07:08"
        return message

    async def RestoreTransaction(
        self, request: Any, timeout: float | None = None
    ) -> Any:
        self.last = request
        message = transaction_common_pb2.ApiResponseTransactionDeleteAt(
            status="success", message="Successfully restored transaction"
        )
        message.data.id = request.id
        return message

    async def DeleteTransactionPermanent(
        self, request: Any, timeout: float | None = None
    ) -> Any:
        self.last = request
        return transaction_common_pb2.ApiResponseTransactionDelete(
            status="success",
            message="Successfully deleted transaction permanently",
        )

    async def RestoreAllTransaction(
        self, request: Any, timeout: float | None = None
    ) -> Any:
        self.last = request
        return transaction_common_pb2.ApiResponseTransactionAll(
            status="success", message="Successfully restored all transactions"
        )

    async def DeleteTransactionByOrderPermanent(
        self, request: Any, timeout: float | None = None
    ) -> Any:
        self.last = request
        return transaction_common_pb2.ApiResponseTransactionDelete(
            status="success",
            message="Successfully deleted transactions by order permanently",
        )

    async def DeleteAllTransactionPermanent(
        self, request: Any, timeout: float | None = None
    ) -> Any:
        self.last = request
        return transaction_common_pb2.ApiResponseTransactionAll(
            status="success",
            message="Successfully deleted all transactions permanently",
        )


class FakeStats:
    def __init__(self) -> None:
        self.last: Any = None

    def _envelope(self, message: str) -> Any:
        return transaction_common_pb2.ApiResponseTransactionMonthAmountSuccess(
            status="success", message=message
        )

    async def GetMonthlyAmountSuccess(
        self, request: Any, timeout: float | None = None
    ) -> Any:
        self.last = request
        response = self._envelope("Successfully fetched monthly amount success stats")
        response.data.add(year="2026", month="Jan", total_success=4, total_amount=480)
        return response


class FakeStatsByMerchant:
    def __init__(self) -> None:
        self.last: Any = None

    async def GetMonthlyAmountSuccessByMerchant(
        self, request: Any, timeout: float | None = None
    ) -> Any:
        self.last = request
        response = transaction_common_pb2.ApiResponseTransactionMonthAmountSuccess(
            status="success",
            message="Successfully fetched monthly amount success stats by merchant",
        )
        response.data.add(year="2026", month="Jan", total_success=2, total_amount=90)
        return response


def _handler() -> tuple[TransactionHandler, grpc.aio.Channel]:
    channel = grpc.aio.insecure_channel("127.0.0.1:1")
    connections = ServiceConnections(
        channels={"transaction": channel},
        addresses={"transaction": "127.0.0.1:1"},
    )
    return TransactionHandler(connections), channel


@pytest.mark.parametrize(
    ("page", "page_size", "expected"),
    [
        (1, 10, (1, 10)),
        (0, 0, (1, 10)),
        (-3, 25, (1, 25)),
    ],
)
def test_normalize_pagination(
    page: int, page_size: int, expected: tuple[int, int]
) -> None:
    assert normalize_pagination(page, page_size) == expected


async def test_query_methods_build_requests_and_map() -> None:
    handler, channel = _handler()
    fake = FakeQuery()
    handler._query = fake
    try:
        response = await handler.find_all(0, 0, "x")
        assert isinstance(fake.last, transaction_query_pb2.FindAllTransactionRequest)
        assert fake.last.page == 1 and fake.last.page_size == 10
        assert fake.last.search == "x"
        assert response.message == "Successfully fetched transactions"
        assert response.data is not None
        assert response.data[0].id == 1
        # Seconds layout passes through unchanged (no `.mmm`).
        assert response.data[0].created_at == "2026-01-02 03:04:05"
        assert response.pagination.total_records == 1

        by_id = await handler.find_by_id(7)
        assert isinstance(fake.last, transaction_common_pb2.FindByIdTransactionRequest)
        assert fake.last.id == 7
        assert by_id.data is not None and by_id.data.id == 7

        by_merchant = await handler.find_by_merchant(5, 2, 3, "")
        assert isinstance(
            fake.last, transaction_query_pb2.FindAllTransactionByMerchantRequest
        )
        assert fake.last.merchant_id == 5
        assert by_merchant.data is not None and by_merchant.data[0].merchant_id == 5

        await handler.find_by_active(1, 10, "")
        await handler.find_by_trashed(1, 10, "")
        assert fake.last.page == 1
    finally:
        await channel.close()


async def test_find_by_id_maps_grpc_not_found() -> None:
    handler, channel = _handler()
    fake = FakeQuery()
    fake.fail = True
    handler._query = fake
    try:
        with pytest.raises(AppError) as excinfo:
            await handler.find_by_id(99)
        assert excinfo.value.code == 404
        assert excinfo.value.message == "transaction not found"
    finally:
        await channel.close()


async def test_command_methods_build_requests_and_map() -> None:
    handler, channel = _handler()
    fake = FakeCommand()
    handler._command = fake
    try:
        created = await handler.create(
            CreateTransactionRequest(
                order_id=42,
                merchant_id=3,
                payment_method="credit_card",
                amount=120000,
                user_id=7,
                payment_status="success",
            )
        )
        assert isinstance(fake.last, transaction_command_pb2.CreateTransactionRequest)
        assert fake.last.order_id == 42
        assert fake.last.user_id == 7
        assert created.data is not None and created.data.id == 77

        updated = await handler.update(9, "refunded")
        assert isinstance(fake.last, transaction_command_pb2.UpdateTransactionRequest)
        assert fake.last.transaction_id == 9
        assert fake.last.payment_status == "refunded"
        assert updated.data is not None and updated.data.id == 9

        trashed = await handler.trash(5)
        assert isinstance(
            fake.last, transaction_common_pb2.FindByIdTransactionRequest
        )
        assert trashed.data is not None
        assert trashed.data.deleted_at == "2026-02-01 06:07:08"

        restored = await handler.restore(5)
        assert restored.data is not None and restored.data.id == 5

        deleted = await handler.delete_permanent(5)
        assert deleted.message == "Successfully deleted transaction permanently"

        await handler.restore_all()
        await handler.delete_by_order_permanent(42)
        await handler.delete_all_permanent()
        assert fake.last is not None
    finally:
        await channel.close()


async def test_stats_methods_delegate_to_both_stubs() -> None:
    handler, channel = _handler()
    stats = FakeStats()
    by_merchant = FakeStatsByMerchant()
    handler._stats = stats
    handler._stats_by_merchant = by_merchant
    try:
        response = await handler.find_monthly_amount_success(2026, 1)
        assert isinstance(
            stats.last, transaction_stats_pb2.MonthAmountTransactionRequest
        )
        assert response.data is not None
        assert response.data[0].total_success == 4

        response = await handler.find_monthly_amount_success_by_merchant(9, 2026, 1)
        assert isinstance(
            by_merchant.last,
            transaction_stats_bymerchant_pb2.MonthAmountTransactionMerchantRequest,
        )
        assert by_merchant.last.merchant_id == 9
        assert response.data is not None
        assert response.data[0].total_amount == 90
    finally:
        await channel.close()

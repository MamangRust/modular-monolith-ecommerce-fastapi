"""Unit tests for the transaction gRPC handlers (no DB/Redis). with id 0 fall through to the service (transaction handlers never raise `ErrGrpcInvalidID`/`ErrGrpcInvalidYear`/...) — unlike order, whose stats handlers guard year/month/merchant."""

from __future__ import annotations

from datetime import datetime
from typing import Any

from pb.transaction import (
    transaction_command_pb2,
    transaction_common_pb2,
    transaction_query_pb2,
)
from pb.transaction.stats import (
    transaction_stats_bymerchant_pb2,
    transaction_stats_pb2,
)
from pkg.database.schema.transaction import (
    GetMonthlyAmountTransactionSuccessRow,
    GetMonthlyTransactionMethodsRow,
    TransactionRow,
)
from pkg.logger.logger import Logger
from service.transaction.handler.transaction_command import TransactionCommandHandler
from service.transaction.handler.transaction_query import TransactionQueryHandler
from service.transaction.handler.transaction_stats import TransactionStatsHandler
from shared.domain.requests.transaction import (
    CreateTransactionRequest,
    MonthAmountTransaction,
    MonthAmountTransactionMerchant,
    YearAmountTransactionMerchant,
)

CREATED = datetime(2026, 1, 2, 3, 4, 5)
UPDATED = datetime(2026, 1, 3, 4, 5, 6)
TRASHED = datetime(2026, 2, 1, 6, 7, 8)


class FakeAbort(Exception):
    def __init__(self, code: Any, message: str) -> None:
        self.code = code
        self.message = message
        super().__init__(message)


class FakeContext:
    def __init__(self) -> None:
        self.metadata: tuple[Any, ...] = ()
        self.aborted: FakeAbort | None = None

    def set_trailing_metadata(self, metadata: tuple[Any, ...]) -> None:
        self.metadata = metadata

    async def abort(self, code: Any, message: str) -> None:
        self.aborted = FakeAbort(code, message)
        raise self.aborted


def _logger() -> Logger:
    return Logger("test", "error")


# ---- query handler ----


class FakeQueryService:
    def __init__(self) -> None:
        self.last: Any = None

    async def find_all(self, request):
        self.last = request
        return [_list_row()], 11

    async def find_by_merchant(self, request):
        self.last = request
        return [_list_row(merchant_id=request.merchant_id)], 11

    async def find_by_id(self, transaction_id):
        self.last = transaction_id
        return _by_id_row(transaction_id)

    async def find_by_order_id(self, order_id):
        self.last = order_id
        return _by_id_row(order_id)

    async def find_active(self, request):
        self.last = request
        return [_list_row()], 11

    async def find_trashed(self, request):
        self.last = request
        return [_trashed_row()], 11


def _list_row(
    transaction_id: int = 1,
    merchant_id: int = 3,
    total: int = 11,
    deleted_at: datetime | None = None,
) -> Any:
    from pkg.database.schema.transaction import GetTransactionsRow

    return GetTransactionsRow(
        transaction_id=transaction_id,
        order_id=42,
        merchant_id=merchant_id,
        payment_method="credit_card",
        amount=120000,
        payment_status="success",
        created_at=CREATED,
        updated_at=UPDATED,
        deleted_at=deleted_at,
        total_count=total,
    )


def _trashed_row() -> Any:
    return _list_row(deleted_at=TRASHED)


def _by_id_row(transaction_id: int = 7) -> TransactionRow:
    return TransactionRow(
        transaction_id=transaction_id,
        order_id=42,
        merchant_id=3,
        payment_method="credit_card",
        amount=120000,
        payment_status="success",
        created_at=CREATED,
        updated_at=UPDATED,
    )


def _query_handler(service: FakeQueryService | None = None) -> TransactionQueryHandler:
    return TransactionQueryHandler(service or FakeQueryService(), _logger())


async def test_query_find_all_seconds_layout_and_clamps() -> None:
    service = FakeQueryService()
    response = await _query_handler(service).FindAllTransactions(
        transaction_query_pb2.FindAllTransactionRequest(page=0, page_size=0, search="x"),
        FakeContext(),
    )
    assert response.message == "Successfully fetched transactions"
    assert response.pagination.current_page == 1
    assert response.pagination.page_size == 10
    assert response.pagination.total_records == 11
    assert response.data[0].id == 1
    assert response.data[0].order_id == 42
    assert response.data[0].amount == 120000
    # Seconds layout — 19 characters, no `.mmm` suffix.
    assert response.data[0].created_at == "2026-01-02 03:04:05"
    assert response.data[0].updated_at == "2026-01-03 04:05:06"
    assert service.last.page == 1 and service.last.page_size == 10


async def test_query_find_by_id_has_no_guard() -> None:
    service = FakeQueryService()
    response = await _query_handler(service).FindById(
        transaction_common_pb2.FindByIdTransactionRequest(id=7), FakeContext()
    )
    assert response.message == "Successfully fetched transaction"
    assert response.data.id == 7
    assert service.last == 7

    await _query_handler(service).FindById(
        transaction_common_pb2.FindByIdTransactionRequest(id=0), FakeContext()
    )
    assert service.last == 0


async def test_query_find_by_merchant_and_order_id() -> None:
    service = FakeQueryService()
    response = await _query_handler(service).FindByMerchant(
        transaction_query_pb2.FindAllTransactionByMerchantRequest(
            merchant_id=5, page=2, page_size=3
        ),
        FakeContext(),
    )
    assert response.message == "Successfully fetched transactions by merchant"
    assert response.data[0].merchant_id == 5
    assert service.last.merchant_id == 5
    assert service.last.page == 2 and service.last.page_size == 3

    response = await _query_handler(service).FindByOrderId(
        transaction_query_pb2.FindByOrderIdTransactionRequest(order_id=42),
        FakeContext(),
    )
    assert response.message == "Successfully fetched transaction by order id"
    assert response.data.order_id == 42


async def test_query_find_by_trashed_sets_deleted_at() -> None:
    response = await _query_handler().FindByTrashed(
        transaction_query_pb2.FindAllTransactionRequest(), FakeContext()
    )
    assert response.message == "Successfully fetched trashed transactions"
    assert response.data[0].deleted_at.value == "2026-02-01 06:07:08"

    # The plain pagination response carries TransactionResponse, which has no
    # deleted_at field at all (proto).
    response = await _query_handler().FindByActive(
        transaction_query_pb2.FindAllTransactionRequest(), FakeContext()
    )
    assert response.message == "Successfully fetched active transactions"
    assert response.data[0].created_at == "2026-01-02 03:04:05"


# ---- command handler ----


class FakeCommandService:
    def __init__(self) -> None:
        self.last: Any = None

    async def create(self, request):
        self.last = request
        return _by_id_row(77)

    async def update(self, request):
        self.last = request
        return _by_id_row(request.transaction_id)

    async def trash(self, transaction_id):
        self.last = transaction_id

        return _trashed_model(transaction_id)

    async def restore(self, transaction_id):
        self.last = transaction_id
        return _trashed_model(transaction_id, deleted_at=None)

    async def delete_permanent(self, transaction_id):
        self.last = transaction_id
        return True

    async def delete_by_order_id_permanent(self, order_id):
        self.last = order_id
        return True

    async def restore_all(self):
        self.last = "restore_all"
        return True

    async def delete_all(self):
        self.last = "delete_all"
        return True


def _trashed_model(
    transaction_id: int, deleted_at: datetime | None = TRASHED
) -> Any:
    from pkg.database.schema.transaction import Transaction

    return Transaction(
        transaction_id=transaction_id,
        order_id=42,
        merchant_id=3,
        payment_method="credit_card",
        amount=120000,
        payment_status="success",
        created_at=CREATED,
        updated_at=UPDATED,
        deleted_at=deleted_at,
    )


def _command_handler(
    service: FakeCommandService | None = None,
) -> TransactionCommandHandler:
    return TransactionCommandHandler(service or FakeCommandService(), _logger())


async def test_command_create_passes_status_through() -> None:
    service = FakeCommandService()
    response = await _command_handler(service).Create(
        transaction_command_pb2.CreateTransactionRequest(
            order_id=42,
            merchant_id=3,
            payment_method="credit_card",
            amount=100,
            user_id=7,
            payment_status="",
        ),
        FakeContext(),
    )
    assert response.message == "Successfully created transaction"
    assert response.data.id == 77
    assert service.last == CreateTransactionRequest(
        user_id=7,
        order_id=42,
        merchant_id=3,
        payment_method="credit_card",
        amount=100,
        payment_status="",
    )


async def test_command_update_carries_transaction_id() -> None:
    service = FakeCommandService()
    response = await _command_handler(service).Update(
        transaction_command_pb2.UpdateTransactionRequest(
            transaction_id=9,
            payment_status="refunded",
        ),
        FakeContext(),
    )
    assert response.message == "Successfully updated transaction"
    assert response.data.id == 9
    assert service.last.transaction_id == 9
    assert service.last.payment_status == "refunded"


async def test_command_trash_restore_delete_have_no_guards() -> None:
    service = FakeCommandService()
    handler = _command_handler(service)

    response = await handler.TrashedTransaction(
        transaction_common_pb2.FindByIdTransactionRequest(id=5), FakeContext()
    )
    assert response.message == "Successfully trashed transaction"
    assert response.data.deleted_at.value == "2026-02-01 06:07:08"
    assert service.last == 5

    response = await handler.RestoreTransaction(
        transaction_common_pb2.FindByIdTransactionRequest(id=5), FakeContext()
    )
    assert response.message == "Successfully restored transaction"
    # Restored row (deleted_at=None) -> wrapper NOT attached.
    assert not response.data.HasField("deleted_at")

    response = await handler.DeleteTransactionPermanent(
        transaction_common_pb2.FindByIdTransactionRequest(id=5), FakeContext()
    )
    assert response.message == "Successfully deleted transaction permanently"

    await handler.TrashedTransaction(
        transaction_common_pb2.FindByIdTransactionRequest(id=0), FakeContext()
    )
    assert service.last == 0


async def test_command_bulk_endpoints() -> None:
    service = FakeCommandService()
    handler = _command_handler(service)

    response = await handler.RestoreAllTransaction(None, FakeContext())
    assert response.message == "Successfully restored all transactions"
    assert service.last == "restore_all"

    response = await handler.DeleteTransactionByOrderPermanent(
        transaction_common_pb2.FindByIdTransactionRequest(id=42), FakeContext()
    )
    assert (
        response.message
        == "Successfully deleted transactions by order permanently"
    )
    assert service.last == 42

    response = await handler.DeleteAllTransactionPermanent(None, FakeContext())
    assert response.message == "Successfully deleted all transactions permanently"
    assert service.last == "delete_all"


# ---- stats handler ----


class FakeStatsService:
    def __init__(self) -> None:
        self.last: Any = None

    async def find_monthly_amount_success(self, request):
        self.last = request
        return [
            GetMonthlyAmountTransactionSuccessRow(
                year="2026", month="Jan", total_success=4, total_amount=480000
            )
        ]

    def __getattr__(self, name):
        async def _other(request):
            self.last = request
            if "method" in name:
                return [
                    GetMonthlyTransactionMethodsRow(
                        month="Jan",
                        payment_method="credit_card",
                        total_transactions=2,
                        total_amount=240000,
                    )
                ]
            return [
                GetMonthlyAmountTransactionSuccessRow(
                    year="2026", month="Jan", total_success=4, total_amount=480000
                )
            ]

        return _other


def _stats_handler(
    stats: FakeStatsService | None = None,
) -> TransactionStatsHandler:
    svc = stats or FakeStatsService()
    return TransactionStatsHandler(svc, svc, _logger())


async def test_stats_monthly_amount_success_has_no_guards() -> None:
    service = FakeStatsService()
    response = await _stats_handler(service).GetMonthlyAmountSuccess(
        transaction_stats_pb2.MonthAmountTransactionRequest(year=0, month=0),
        FakeContext(),
    )
    assert (
        response.message == "Successfully fetched monthly amount success stats"
    )
    assert response.data[0].year == "2026"
    assert response.data[0].total_success == 4
    assert response.data[0].total_amount == 480000
    assert service.last == MonthAmountTransaction(year=0, month=0)


async def test_stats_by_merchant_reads_merchant_id() -> None:
    service = FakeStatsService()
    response = await _stats_handler(service).GetMonthlyAmountSuccessByMerchant(
        transaction_stats_bymerchant_pb2.MonthAmountTransactionMerchantRequest(
            merchant_id=9, year=2026, month=1
        ),
        FakeContext(),
    )
    assert (
        response.message
        == "Successfully fetched monthly amount success stats by merchant"
    )
    assert response.data[0].total_success == 4
    assert service.last == MonthAmountTransactionMerchant(
        merchant_id=9, year=2026, month=1
    )


async def test_stats_by_merchant_yearly_reads_merchant_id() -> None:
    service = FakeStatsService()
    await _stats_handler(service).GetYearlyAmountSuccessByMerchant(
        transaction_stats_bymerchant_pb2.YearAmountTransactionMerchantRequest(
            merchant_id=4, year=2026
        ),
        FakeContext(),
    )
    assert service.last == YearAmountTransactionMerchant(merchant_id=4, year=2026)

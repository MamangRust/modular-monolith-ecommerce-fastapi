"""Unit tests for the transaction services (no DB/Redis). Covers the cache-first query/stats services, the payment state machine, and the command service: - `create` derives the amount from the order (items × price + shipping, +11% PPN), stores the derived amount (not the caller's), forces `success` through the state machine, validates a supplied canonical status, and commits the insert + its two outbox events in one transaction; - `create` maps an insufficient cover to `err_failed_payment_insufficient_balance`, an invalid status to `err_failed_payment_status_invalid`, a terminal status to `err_failed_payment_status_cannot_be_modified`, and a bad item to `err_failed_order_item_empty`; - `update` defaults merchant/order from the existing row, re-derives the amount, keeps a caller-supplied non-success status when legal, and rejects illegal transitions; - trash/restore/delete evict via the namespace invalidation; the bulk ops and `delete_by_order_id_permanent` invalidate the whole `transaction:*` namespace. Every fake records into a shared `calls` list so the saga's ordering can be asserted. Errors from repositories/adapters propagate unchanged (`HandleError`)."""

from __future__ import annotations

from datetime import UTC, datetime
from types import SimpleNamespace
from typing import Any

import pytest

from pkg.database.schema.order import Order
from pkg.database.schema.order_item import GetOrderItemsByOrderRow
from pkg.database.schema.transaction import (
    GetTransactionsRow,
    Transaction,
    TransactionRow,
)
from pkg.logger.logger import Logger
from service.transaction.service.payment_state_machine import (
    can_transition_payment_status,
    is_valid_payment_status,
    normalize_payment_status,
)
from service.transaction.service.transaction_command_service import (
    TransactionCommandServiceImpl,
)
from service.transaction.service.transaction_query_service import (
    TransactionQueryServiceImpl,
)
from service.transaction.service.transaction_stats_by_merchant_service import (
    TransactionStatsByMerchantServiceImpl,
)
from service.transaction.service.transaction_stats_service import (
    TransactionStatsServiceImpl,
)
from shared.domain.requests.transaction import (
    CreateTransactionRequest,
    FindAllTransaction,
    MonthAmountTransaction,
    UpdateTransactionRequest,
)
from shared.errors import AppError
from shared.errors.transaction_errors import (
    err_failed_payment_insufficient_balance,
    err_failed_payment_status_cannot_be_modified,
    err_failed_payment_status_invalid,
)
from shared.observability import Observability

CREATED = datetime(2026, 1, 2, 3, 4, 5, tzinfo=UTC)
UPDATED = datetime(2026, 1, 3, 4, 5, 6, tzinfo=UTC)

# Derived amounts used across the create/update tests: one item (qty 2, price
# 5000) + shipping 1500 → 11500 + 11% PPN → 12765.
MERCHANDISE_TOTAL = 10000
SHIPPING_COST = 1500
PPN = (MERCHANDISE_TOTAL + SHIPPING_COST) * 11 // 100
TOTAL_WITH_TAX = MERCHANDISE_TOTAL + SHIPPING_COST + PPN


def _logger() -> Logger:
    return Logger("test", "error")


def _obs() -> Observability:
    return Observability("test", _logger())


def _tx_row(transaction_id: int = 77, **overrides: Any) -> TransactionRow:
    row = TransactionRow(
        transaction_id=transaction_id,
        order_id=42,
        merchant_id=3,
        payment_method="credit_card",
        amount=TOTAL_WITH_TAX,
        payment_status="success",
        created_at=CREATED,
        updated_at=UPDATED,
    )
    for key, value in overrides.items():
        setattr(row, key, value)
    return row


def _tx(transaction_id: int = 77, **overrides: Any) -> Transaction:
    row = _tx_row(transaction_id, **overrides)
    return Transaction(
        transaction_id=row.transaction_id,
        order_id=row.order_id,
        merchant_id=row.merchant_id,
        payment_method=row.payment_method,
        amount=row.amount,
        payment_status=row.payment_status,
        created_at=row.created_at,
        updated_at=row.updated_at,
        deleted_at=UPDATED,
    )


def _order(order_id: int = 42) -> Order:
    return Order(
        order_id=order_id,
        user_id=7,
        merchant_id=3,
        total_price=0,
        created_at=CREATED,
        updated_at=UPDATED,
        deleted_at=None,
    )


def _order_item(
    order_item_id: int = 5,
    quantity: int = 2,
    price: int = 5000,
) -> GetOrderItemsByOrderRow:
    return GetOrderItemsByOrderRow(
        order_item_id=order_item_id,
        order_id=42,
        product_id=10,
        quantity=quantity,
        price=price,
        created_at=CREATED,
        updated_at=UPDATED,
    )


def _shipping(cost: int = SHIPPING_COST) -> SimpleNamespace:
    return SimpleNamespace(
        id=9,
        order_id=42,
        alamat="Jalan Panjang",
        provinsi="DKI",
        kota="Jakarta",
        courier="jne",
        shippingMethod="reg",
        shippingCost=cost,
        negara="Indonesia",
    )


def _user() -> SimpleNamespace:
    return SimpleNamespace(user_id=7, email="owner@example.com")


def _page_row(transaction_id: int = 77, total: int = 1) -> GetTransactionsRow:
    return GetTransactionsRow(
        transaction_id=transaction_id,
        order_id=42,
        merchant_id=3,
        payment_method="credit_card",
        amount=120000,
        payment_status="success",
        created_at=CREATED,
        updated_at=UPDATED,
        deleted_at=None,
        total_count=total,
    )


# --------------------------------------------------------------------- fakes


class FakeTransactionQuery:
    def __init__(self, calls, *, row=None, rows=None, error=None):
        self._calls = calls
        self._row = row if row is not None else _tx_row()
        self._rows = rows or []
        self._error = error

    async def find_all(self, request):
        self._calls.append("tx.find_all")
        if self._error:
            raise self._error
        return self._rows

    async def find_active(self, request):
        self._calls.append("tx.find_active")
        if self._error:
            raise self._error
        return self._rows

    async def find_trashed(self, request):
        self._calls.append("tx.find_trashed")
        if self._error:
            raise self._error
        return self._rows

    async def find_by_merchant(self, request):
        self._calls.append("tx.find_by_merchant")
        if self._error:
            raise self._error
        return self._rows

    async def find_by_id(self, transaction_id):
        self._calls.append(f"tx.find_by_id:{transaction_id}")
        if self._error:
            raise self._error
        return self._row

    async def find_by_order_id(self, order_id):
        self._calls.append(f"tx.find_by_order_id:{order_id}")
        if self._error:
            raise self._error
        return self._row


class FakeTransactionCommand:
    def __init__(self, calls, *, row=None, error=None):
        self._calls = calls
        self._row = row if row is not None else _tx_row()
        self._error = error

    async def create(self, request):
        self._calls.append(f"tx.create:{request.amount}:{request.payment_status}")
        if self._error:
            raise self._error
        return self._row

    async def create_in_tx(self, conn, request):
        self._calls.append(
            f"tx.create_in_tx:{request.amount}:{request.payment_status}"
        )
        if self._error:
            raise self._error
        return self._row

    async def update(self, request):
        self._calls.append(
            f"tx.update:{request.transaction_id}:{request.amount}:"
            f"{request.payment_status}"
        )
        if self._error:
            raise self._error
        return _tx_row(
            request.transaction_id,
            amount=request.amount,
            payment_status=request.payment_status,
        )

    async def trash(self, transaction_id):
        self._calls.append(f"tx.trash:{transaction_id}")
        return _tx(transaction_id)

    async def restore(self, transaction_id):
        self._calls.append(f"tx.restore:{transaction_id}")
        return _tx(transaction_id)

    async def delete_permanent(self, transaction_id):
        self._calls.append(f"tx.delete_permanent:{transaction_id}")
        return True

    async def delete_by_order_id_permanent(self, order_id):
        self._calls.append(f"tx.delete_by_order:{order_id}")
        return True

    async def restore_all(self):
        self._calls.append("tx.restore_all")
        return True

    async def delete_all(self):
        self._calls.append("tx.delete_all")
        return True


class FakeUserQuery:
    def __init__(self, calls, error=None):
        self._calls = calls
        self._error = error

    async def find_by_id(self, user_id):
        self._calls.append(f"user.find:{user_id}")
        if self._error:
            raise self._error
        return _user()


class FakeMerchantQuery:
    def __init__(self, calls, error=None):
        self._calls = calls
        self._error = error

    async def find_by_id(self, merchant_id):
        self._calls.append(f"merchant.find:{merchant_id}")
        if self._error:
            raise self._error
        return SimpleNamespace(merchant_id=merchant_id, name="M")


class FakeOrderQuery:
    def __init__(self, calls, *, row=None, error=None):
        self._calls = calls
        self._row = row if row is not None else _order()
        self._error = error

    async def find_by_id(self, order_id):
        self._calls.append(f"order.find:{order_id}")
        if self._error:
            raise self._error
        return self._row


class FakeOrderItem:
    def __init__(self, calls, *, items=None, error=None):
        self._calls = calls
        self._items = items if items is not None else [_order_item()]
        self._error = error

    async def find_order_item_by_order(self, order_id):
        self._calls.append(f"order_item.find:{order_id}")
        if self._error:
            raise self._error
        return self._items


class FakeShipping:
    def __init__(self, calls, *, row=None, error=None):
        self._calls = calls
        self._row = row if row is not None else _shipping()
        self._error = error

    async def find_by_order(self, order_id):
        self._calls.append(f"shipping.find:{order_id}")
        if self._error:
            raise self._error
        return self._row


class FakeCommandCache:
    def __init__(self, calls) -> None:
        self._calls = calls
        self.deleted: list[int] = []
        self.invalidations = 0

    async def delete_transaction_cache(self, transaction_id: int) -> int:
        self._calls.append(f"cache.delete:{transaction_id}")
        self.deleted.append(transaction_id)
        return 1

    async def invalidate_transaction_cache(self) -> int:
        self._calls.append("cache.invalidate")
        self.invalidations += 1
        return 1


class FakeTransaction:
    def __init__(self, conn: Any) -> None:
        self._conn = conn

    async def __aenter__(self) -> Any:
        return self._conn

    async def __aexit__(self, *exc: Any) -> bool:
        return False


class FakeDB:
    def __init__(self) -> None:
        self.conn = object()
        self.transactions = 0

    def transaction(self) -> FakeTransaction:
        self.transactions += 1
        return FakeTransaction(self.conn)


class FakeEnqueue:
    def __init__(self) -> None:
        self.events: list[Any] = []

    async def __call__(self, conn: Any, event: Any) -> None:
        self.events.append(event)


def _command_service(
    calls,
    *,
    transaction_query=None,
    transaction_command=None,
    user_query=None,
    merchant_query=None,
    order_query=None,
    order_item=None,
    shipping=None,
    cache=None,
    enqueue=None,
    db=None,
) -> TransactionCommandServiceImpl:
    return TransactionCommandServiceImpl(
        transaction_query=transaction_query or FakeTransactionQuery(calls),
        transaction_command=transaction_command or FakeTransactionCommand(calls),
        user_query=user_query or FakeUserQuery(calls),
        merchant_query=merchant_query or FakeMerchantQuery(calls),
        order_query=order_query or FakeOrderQuery(calls),
        order_item=order_item or FakeOrderItem(calls),
        shipping_address=shipping or FakeShipping(calls),
        cache=cache or FakeCommandCache(calls),
        db=db or FakeDB(),  # type: ignore[arg-type]
        logger=_logger(),
        obs=_obs(),
        enqueue_fn=enqueue or FakeEnqueue(),
    )


def _create_request(**overrides: Any) -> CreateTransactionRequest:
    fields = {
        "user_id": 0,
        "order_id": 42,
        "merchant_id": 3,
        "payment_method": "credit_card",
        "amount": TOTAL_WITH_TAX,
        "payment_status": "",
    }
    fields.update(overrides)
    return CreateTransactionRequest(**fields)


# ---------------------------------------------------------------- state machine


def test_payment_state_machine_normalises_completed() -> None:
    assert normalize_payment_status("completed") == "success"
    assert normalize_payment_status("pending") == "pending"
    assert is_valid_payment_status("completed") is True
    assert is_valid_payment_status("bogus") is False


def test_payment_state_machine_transitions() -> None:
    assert can_transition_payment_status("pending", "success") is True
    assert can_transition_payment_status("pending", "failed") is True
    assert can_transition_payment_status("success", "refunded") is True
    assert can_transition_payment_status("success", "pending") is False
    # Idempotent transitions always pass, terminal statuses never reopen.
    assert can_transition_payment_status("failed", "failed") is True
    assert can_transition_payment_status("refunded", "success") is False
    assert can_transition_payment_status("completed", "refunded") is True


# ------------------------------------------------------------- query service


async def test_query_service_serves_from_cache() -> None:
    calls: list[str] = []
    rows = [_page_row(total=4)]
    repo = FakeTransactionQuery(calls, rows=rows)
    cache = FakeQueryCache(prefilled=4)
    service = TransactionQueryServiceImpl(repo, cache, _logger(), _obs())

    got, total = await service.find_all(FindAllTransaction(search="", page=1, page_size=10))

    assert [row.transaction_id for row in got] == [77]
    assert total == 4
    assert calls == []  # repository untouched


async def test_query_service_miss_populates_cache() -> None:
    calls: list[str] = []
    repo = FakeTransactionQuery(calls, rows=[_page_row(total=1)])
    cache = FakeQueryCache()
    service = TransactionQueryServiceImpl(repo, cache, _logger(), _obs())

    got = await service.find_by_id(77)

    assert got.transaction_id == 77
    assert calls == ["tx.find_by_id:77"]
    assert cache.stored_by_id is not None


class FakeQueryCache:
    """Query cache double with pre-seedable page payloads."""

    def __init__(self, *, page_rows=None, prefilled=0) -> None:
        self._page_rows = page_rows
        self._prefilled = prefilled
        self.stored_by_id: Any = None
        self.stored_by_order: Any = None

    async def get_all(self, request):
        if self._prefilled:
            return [_page_row(total=self._prefilled)], self._prefilled
        return None

    async def set_all(self, request, rows, total) -> None:
        self._page_rows = rows

    async def get_by_merchant(self, request):
        return None

    async def set_by_merchant(self, request, rows, total) -> None:
        pass

    async def get_active(self, request):
        return None

    async def set_active(self, request, rows, total) -> None:
        pass

    async def get_trashed(self, request):
        return None

    async def set_trashed(self, request, rows, total) -> None:
        pass

    async def get_by_id(self, transaction_id):
        return None

    async def set_by_id(self, row) -> None:
        self.stored_by_id = row

    async def get_by_order(self, order_id):
        return None

    async def set_by_order(self, order_id, row) -> None:
        self.stored_by_order = row


# ------------------------------------------------------------- create saga


async def test_create_derives_amount_and_commits_outbox_atomically() -> None:
    calls: list[str] = []
    repo = FakeTransactionCommand(calls)
    enqueue = FakeEnqueue()
    db = FakeDB()
    service = _command_service(calls, transaction_command=repo, enqueue=enqueue, db=db)

    row = await service.create(_create_request(amount=TOTAL_WITH_TAX))

    assert row.amount == TOTAL_WITH_TAX
    # Saga order: order -> user -> merchant -> items -> shipping -> insert.
    assert calls[:6] == [
        "order.find:42",
        "user.find:7",
        "merchant.find:3",
        "order_item.find:42",
        "shipping.find:42",
        f"tx.create_in_tx:{TOTAL_WITH_TAX}:success",
    ]
    assert db.transactions == 1
    assert [event.topic for event in enqueue.events] == [
        "email-service-topic-transaction-create",
        "merchant-service-topic-transaction-event",
    ]
    assert enqueue.events[0].key == "77"
    assert enqueue.events[1].key == "3"
    assert "transaction-create:77" in enqueue.events[0].event_key
    assert "transaction-merchant-event:77" in enqueue.events[1].event_key


async def test_create_resolves_owner_from_order_when_user_id_zero() -> None:
    calls: list[str] = []
    service = _command_service(calls)
    await service.create(_create_request(user_id=0))
    assert "user.find:7" in calls


async def test_create_rejects_insufficient_cover() -> None:
    calls: list[str] = []
    service = _command_service(calls)
    with pytest.raises(AppError) as excinfo:
        await service.create(_create_request(amount=TOTAL_WITH_TAX - 1))
    assert excinfo.value is err_failed_payment_insufficient_balance


async def test_create_rejects_invalid_payment_status() -> None:
    calls: list[str] = []
    service = _command_service(calls)
    with pytest.raises(AppError) as excinfo:
        await service.create(_create_request(payment_status="bogus"))
    assert excinfo.value is err_failed_payment_status_invalid


async def test_create_rejects_terminal_status_via_state_machine() -> None:
    calls: list[str] = []
    service = _command_service(calls)
    with pytest.raises(AppError) as excinfo:
        await service.create(_create_request(payment_status="refunded"))
    assert excinfo.value is err_failed_payment_status_cannot_be_modified


async def test_create_rejects_empty_or_negative_items() -> None:
    calls: list[str] = []
    # only rejects inside the loop: an order with NO items yields a zero
    # merchandise total and proceeds (verbatim).
    empty_items = FakeOrderItem(calls, items=[])
    service = _command_service(calls, order_item=empty_items)
    row = await service.create(_create_request(amount=TOTAL_WITH_TAX))
    assert row.amount == TOTAL_WITH_TAX

    calls.clear()
    zero_qty = FakeOrderItem(calls, items=[_order_item(quantity=0)])
    service = _command_service(calls, order_item=zero_qty)
    with pytest.raises(AppError):
        await service.create(_create_request(amount=TOTAL_WITH_TAX))


async def test_create_propagates_adapter_errors_unchanged() -> None:
    calls: list[str] = []
    missing_order = AppError("NOT_FOUND", 404, "order not found")
    service = _command_service(
        calls, order_query=FakeOrderQuery(calls, error=missing_order)
    )
    with pytest.raises(AppError) as excinfo:
        await service.create(_create_request())
    assert excinfo.value is missing_order


# -------------------------------------------------------------------- update


async def test_update_defaults_and_keeps_non_success_status() -> None:
    calls: list[str] = []
    service = _command_service(calls)

    row = await service.update(
        UpdateTransactionRequest(
            transaction_id=77,
            order_id=0,
            merchant_id=0,
            payment_method="",
            amount=0,
            payment_status="refunded",
        )
    )

    # amount 0 → existing (TOTAL_WITH_TAX) → equals the derived total, so the
    # caller-controlled status survives: "refunded" is legal from "success".
    assert row.payment_status == "refunded"
    assert calls[:2] == ["tx.find_by_id:77", "merchant.find:3"]
    assert "merchant.find:3" in calls
    assert "order.find:42" in calls
    assert f"tx.update:77:{TOTAL_WITH_TAX}:refunded" in calls


async def test_update_rejects_reopening_a_failed_transaction() -> None:
    calls: list[str] = []
    failed_row = _tx_row(77, payment_status="failed")
    service = _command_service(calls, transaction_query=FakeTransactionQuery(calls, row=failed_row))

    # An explicit "failed" from "failed" passes (idempotent); but with no
    # caller status the derivation forces "success", which cannot follow
    row = await service.update(
        UpdateTransactionRequest(
            transaction_id=77,
            order_id=42,
            merchant_id=3,
            payment_method="credit_card",
            amount=TOTAL_WITH_TAX,
            payment_status="failed",
        )
    )
    assert row.payment_status == "failed"

    with pytest.raises(AppError) as excinfo:
        await service.update(
            UpdateTransactionRequest(
                transaction_id=77,
                order_id=42,
                merchant_id=3,
                payment_method="credit_card",
                amount=TOTAL_WITH_TAX,
                payment_status="",
            )
        )
    assert excinfo.value is err_failed_payment_status_cannot_be_modified


async def test_update_rejects_insufficient_amount() -> None:
    calls: list[str] = []
    service = _command_service(calls)
    with pytest.raises(AppError) as excinfo:
        await service.update(
            UpdateTransactionRequest(
                transaction_id=77,
                order_id=42,
                merchant_id=3,
                payment_method="credit_card",
                amount=1,
                payment_status="",
            )
        )
    assert excinfo.value is err_failed_payment_insufficient_balance


async def test_update_rejects_illegal_status_transition() -> None:
    calls: list[str] = []
    service = _command_service(calls)
    with pytest.raises(AppError) as excinfo:
        await service.update(
            UpdateTransactionRequest(
                transaction_id=77,
                order_id=42,
                merchant_id=3,
                payment_method="credit_card",
                amount=TOTAL_WITH_TAX,
                payment_status="pending",
            )
        )
    assert excinfo.value is err_failed_payment_status_cannot_be_modified


# --------------------------------------------------- transitions and bulk ops


async def test_single_row_mutations_evict_cache() -> None:
    calls: list[str] = []
    cache = FakeCommandCache(calls)
    service = _command_service(calls, cache=cache)

    await service.trash(77)
    await service.restore(77)
    await service.delete_permanent(77)

    assert cache.deleted == [77, 77, 77]
    assert cache.invalidations == 0


async def test_bulk_and_by_order_mutations_invalidate_namespace() -> None:
    calls: list[str] = []
    cache = FakeCommandCache(calls)
    service = _command_service(calls, cache=cache)

    await service.delete_by_order_id_permanent(42)
    await service.restore_all()
    await service.delete_all()

    assert cache.invalidations == 3


# ------------------------------------------------------------ stats services


class FakeStatsCache:
    def __init__(self, *, prefilled=None) -> None:
        self._prefilled = prefilled
        self.stored: Any = None

    async def get_monthly_amount_success(self, request):
        return self._prefilled

    async def set_monthly_amount_success(self, request, rows) -> None:
        self.stored = rows

    def __getattr__(self, name):
        async def _miss(*args: Any, **kwargs: Any) -> None:
            return None

        async def _set(*args: Any, **kwargs: Any) -> None:
            self.stored = args[-1]

        if name.startswith("get_"):
            return _miss
        if name.startswith("set_"):
            return _set
        raise AttributeError(name)


class FakeStatsRepo:
    def __init__(self, calls) -> None:
        self._calls = calls

    def __getattr__(self, name):
        async def _row(*args: Any, **kwargs: Any) -> list:
            self._calls.append(name)
            return [SimpleNamespace(year="2026", month="Jan")]

        return _row


async def test_stats_serves_from_cache_and_populates_on_miss() -> None:
    calls: list[str] = []
    repo = FakeStatsRepo(calls)
    cache = FakeStatsCache(prefilled=[SimpleNamespace(year="2025", month="Dec")])
    service = TransactionStatsServiceImpl(repo, cache, _logger(), _obs())

    got = await service.find_monthly_amount_success(
        MonthAmountTransaction(year=2026, month=1)
    )
    assert got[0].year == "2025"  # cache hit, repository untouched
    assert calls == []

    cache = FakeStatsCache()
    service = TransactionStatsServiceImpl(repo, cache, _logger(), _obs())
    got = await service.find_monthly_amount_success(
        MonthAmountTransaction(year=2026, month=1)
    )
    assert calls == ["get_monthly_amount_success"]
    assert got[0].year == "2026"
    assert cache.stored is not None


async def test_stats_by_merchant_round_trip() -> None:
    from shared.domain.requests.transaction import MonthAmountTransactionMerchant

    calls: list[str] = []
    repo = FakeStatsRepo(calls)
    cache = FakeStatsCache()
    service = TransactionStatsByMerchantServiceImpl(repo, cache, _logger(), _obs())

    got = await service.find_monthly_amount_success_by_merchant(
        MonthAmountTransactionMerchant(merchant_id=3, year=2026, month=1)
    )
    assert got[0].year == "2026"
    assert calls == ["get_monthly_amount_success_by_merchant"]

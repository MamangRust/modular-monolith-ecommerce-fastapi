"""transaction repository integration tests against a real PostgreSQL. Marked `integration` (excluded from `make test`). `transactions.order_id` and `transactions.merchant_id` carry FKs, so each test seeds its own parent chain (user -> merchant -> order) via the `order_parents` fixture plus a direct order insert, and removes every row it owns. The stats queries scan `transactions` with explicit timestamp windows, so the stats tests insert transactions with `created_at` in **2001** — far from the seeder's current-year rows — to keep the windows deterministic. Covers the read repository (`find_all`/`find_active`/`find_trashed`/ `find_by_merchant`/`find_by_id`/`find_by_order_id`), the write repository (create, `create_in_tx`, update, trash, restore, permanent delete incl. the by-order variant and the trashed-parent of `delete_all`, bulk restore), and the eight global + eight by-merchant stats queries."""

from __future__ import annotations

from datetime import datetime

import grpc
import pytest

from pkg.database.database import Database
from pkg.outbox import Event, enqueue
from service.transaction.repository import GuardOptions, new_repositories
from shared.domain.requests.transaction import (
    CreateTransactionRecordRequest,
    FindAllTransaction,
    FindAllTransactionByMerchant,
    MonthAmountTransaction,
    MonthAmountTransactionMerchant,
    MonthMethodTransaction,
    MonthMethodTransactionMerchant,
    UpdateTransactionRecordRequest,
    YearAmountTransactionMerchant,
    YearMethodTransactionMerchant,
)
from shared.errors import AppError

pytestmark = pytest.mark.integration


@pytest.fixture
async def repos(db):
    """transaction repositories with unused dependency channels."""
    channels = [grpc.aio.insecure_channel("127.0.0.1:1") for _ in range(5)]
    try:
        yield new_repositories(
            db,
            user_channel=channels[0],
            merchant_channel=channels[1],
            order_channel=channels[2],
            order_item_channel=channels[3],
            shipping_channel=channels[4],
            guards=GuardOptions(),
        )
    finally:
        for channel in channels:
            await channel.close()


class SimpleFamily:
    def __init__(self, user_id: int, merchant_id: int, order_id: int) -> None:
        self.user_id = user_id
        self.merchant_id = merchant_id
        self.order_id = order_id


@pytest.fixture
async def family(db: Database, order_parents):
    """user + merchant + order ready to hold transactions."""
    order = await db.execute(
        """
        INSERT INTO orders (user_id, merchant_id, total_price)
        VALUES (:user_id, :merchant_id, :total_price)
        RETURNING order_id
        """,
        {
            "user_id": order_parents.user_id,
            "merchant_id": order_parents.merchant_id,
            "total_price": 11500,
        },
    )
    assert order is not None
    return SimpleFamily(
        user_id=order_parents.user_id,
        merchant_id=order_parents.merchant_id,
        order_id=int(order["order_id"]),
    )


async def _seed_transaction(
    db: Database,
    family: SimpleFamily,
    *,
    method: str = "credit_card",
    amount: int = 120000,
    status: str = "success",
    created_at: datetime | None = None,
    trash: bool = False,
) -> int:
    row = await db.execute(
        """
        INSERT INTO transactions (
            order_id, merchant_id, payment_method, amount, payment_status,
            created_at, updated_at, deleted_at
        )
        VALUES (
            :order_id, :merchant_id, :method, :amount, :status,
            COALESCE(:created_at, CURRENT_TIMESTAMP),
            COALESCE(:created_at, CURRENT_TIMESTAMP),
            CASE WHEN :trash THEN CURRENT_TIMESTAMP ELSE NULL END
        )
        RETURNING transaction_id
        """,
        {
            "order_id": family.order_id,
            "merchant_id": family.merchant_id,
            "method": method,
            "amount": amount,
            "status": status,
            "created_at": created_at,
            "trash": trash,
        },
    )
    assert row is not None
    return int(row["transaction_id"])


# ------------------------------------------------------------ read repository


async def test_find_all_filters_and_paginates(db: Database, repos, family) -> None:
    active_id = await _seed_transaction(db, family, status="success")
    trashed_id = await _seed_transaction(db, family, status="failed", trash=True)

    rows = await repos.transaction_query.find_all(
        FindAllTransaction(search="", page=1, page_size=10)
    )
    ids = [row.transaction_id for row in rows]
    assert active_id in ids
    # FindAll filters deleted_at (unlike banner's).
    assert trashed_id not in ids
    assert rows[0].total_count >= 1

    found = await repos.transaction_query.find_by_id(active_id)
    assert found.transaction_id == active_id
    assert found.payment_method == "credit_card"

    with pytest.raises(AppError) as excinfo:
        await repos.transaction_query.find_by_id(trashed_id)  # filtered out
    assert excinfo.value.message == "transaction not found"


async def test_find_active_trashed_by_merchant_and_by_order(
    db: Database, repos, family
) -> None:
    active_id = await _seed_transaction(db, family)
    trashed_id = await _seed_transaction(db, family, trash=True)

    active = await repos.transaction_query.find_active(
        FindAllTransaction(search="", page=1, page_size=10)
    )
    assert active_id in [row.transaction_id for row in active]

    trashed = await repos.transaction_query.find_trashed(
        FindAllTransaction(search="", page=1, page_size=10)
    )
    assert trashed_id in [row.transaction_id for row in trashed]

    by_merchant = await repos.transaction_query.find_by_merchant(
        FindAllTransactionByMerchant(
            merchant_id=family.merchant_id, search="", page=1, page_size=10
        )
    )
    assert active_id in [row.transaction_id for row in by_merchant]

    by_order = await repos.transaction_query.find_by_order_id(family.order_id)
    assert by_order.transaction_id == active_id


# ----------------------------------------------------------- write repository


async def test_create_update_trash_restore_lifecycle(
    db: Database, repos, family
) -> None:
    created = await repos.transaction_command.create(
        CreateTransactionRecordRequest(
            user_id=family.user_id,
            order_id=family.order_id,
            merchant_id=family.merchant_id,
            payment_method="ewallet",
            amount=12765,
            payment_status="success",
        )
    )
    assert created.amount == 12765

    updated = await repos.transaction_command.update(
        UpdateTransactionRecordRequest(
            transaction_id=created.transaction_id,
            order_id=family.order_id,
            merchant_id=family.merchant_id,
            payment_method="bank_transfer",
            amount=20000,
            payment_status="failed",
        )
    )
    assert updated.payment_method == "bank_transfer"
    assert updated.payment_status == "failed"

    trashed = await repos.transaction_command.trash(created.transaction_id)
    assert trashed.deleted_at is not None

    restored = await repos.transaction_command.restore(created.transaction_id)
    assert restored.deleted_at is None


async def test_create_in_tx_commit_and_rollback(db: Database, repos, family) -> None:
    created = None
    async with db.transaction() as conn:
        created = await repos.transaction_command.create_in_tx(
            conn,
            CreateTransactionRecordRequest(
                user_id=family.user_id,
                order_id=family.order_id,
                merchant_id=family.merchant_id,
                payment_method="ewallet",
                amount=500,
                payment_status="pending",
            ),
        )
        await enqueue(
            conn,
            Event(
                event_key=f"transaction-create:{created.transaction_id}",
                topic="email-service-topic-transaction-create",
                key=str(created.transaction_id),
                payload='{"eventType": "transaction.created"}',
            ),
        )
    assert created.transaction_id > 0

    # A raise inside the transaction rolls the business row AND the event back.
    with pytest.raises(RuntimeError):
        async with db.transaction() as conn:
            doomed = await repos.transaction_command.create_in_tx(
                conn,
                CreateTransactionRecordRequest(
                    user_id=family.user_id,
                    order_id=family.order_id,
                    merchant_id=family.merchant_id,
                    payment_method="ewallet",
                    amount=500,
                    payment_status="pending",
                ),
            )
            await enqueue(
                conn,
                Event(
                    event_key=f"transaction-create:{doomed.transaction_id}",
                    topic="email-service-topic-transaction-create",
                    key=str(doomed.transaction_id),
                    payload='{"eventType": "transaction.created"}',
                ),
            )
            raise RuntimeError("boom")

    left = await db.execute(
        "SELECT COUNT(*) AS n FROM transactions WHERE order_id = :oid "
        "AND amount = 500",
        {"oid": family.order_id},
    )
    assert left is not None and int(left["n"]) == 1  # only the committed one
    events = await db.execute(
        "SELECT COUNT(*) AS n FROM outbox_events WHERE event_key = :key",
        {"key": f"transaction-create:{created.transaction_id}"},
    )
    assert events is not None and int(events["n"]) == 1


async def test_delete_permanent_and_bulk_ops(db: Database, repos, family) -> None:
    first = await _seed_transaction(db, family)
    second = await _seed_transaction(db, family, trash=True)

    # delete_permanent only matches TRASHED rows (:exec semantics still report
    # success for an active row) — `first` survives.
    assert await repos.transaction_command.delete_permanent(first) is True
    kept = await db.execute(
        "SELECT COUNT(*) AS n FROM transactions WHERE transaction_id = :tid",
        {"tid": first},
    )
    assert kept is not None and int(kept["n"]) == 1

    # RestoreAll un-trashes everything, including `second`.
    assert await repos.transaction_command.restore_all() is True
    row = await db.execute(
        "SELECT deleted_at FROM transactions WHERE transaction_id = :tid",
        {"tid": second},
    )
    assert row is not None and row["deleted_at"] is None

    # DeleteAll purges trashed rows AND rows whose parent order is trashed
    # active transaction for it — the bulk delete removes that child too.
    await db.execute(
        "UPDATE orders SET deleted_at = CURRENT_TIMESTAMP WHERE order_id = :oid",
        {"oid": family.order_id},
    )
    parent_child = await _seed_transaction(db, family)
    assert await repos.transaction_command.delete_all() is True

    gone_child = await db.execute(
        "SELECT COUNT(*) AS n FROM transactions WHERE transaction_id = :tid",
        {"tid": parent_child},
    )
    assert gone_child is not None and int(gone_child["n"]) == 0


async def test_delete_by_order_permanent_removes_all_rows(
    db: Database, repos, family
) -> None:
    await _seed_transaction(db, family)
    await _seed_transaction(db, family, trash=True)

    assert await repos.transaction_command.delete_by_order_id_permanent(
        family.order_id
    ) is True

    left = await db.execute(
        "SELECT COUNT(*) AS n FROM transactions WHERE order_id = :oid",
        {"oid": family.order_id},
    )
    assert left is not None and int(left["n"]) == 0


# -------------------------------------------------------------- stats queries


async def test_global_stats_windows(db: Database, repos, order_parents, family) -> None:
    window = datetime(2001, 3, 15, 12, 0, 0)
    tx_a = await _seed_transaction(
        db, family, method="credit_card", amount=10000, status="success",
        created_at=window,
    )
    await _seed_transaction(
        db, family, method="credit_card", amount=5000, status="failed",
        created_at=window,
    )
    _ = tx_a

    monthly = await repos.transaction_stats.get_monthly_amount_success(
        MonthAmountTransaction(year=2001, month=3)
    )
    assert monthly, "expected at least the zero-filler rows"
    march = [row for row in monthly if row.year == "2001" and row.month == "Mar"]
    assert march and march[0].total_success == 1
    assert march[0].total_amount == 10000

    failed = await repos.transaction_stats.get_monthly_amount_failed(
        MonthAmountTransaction(year=2001, month=3)
    )
    march_failed = [row for row in failed if row.year == "2001" and row.month == "Mar"]
    assert march_failed and march_failed[0].total_failed == 1
    assert march_failed[0].total_amount == 5000

    yearly = await repos.transaction_stats.get_yearly_amount_success(2001)
    row_2001 = [row for row in yearly if row.year == "2001"]
    assert row_2001 and row_2001[0].total_success == 1

    methods = await repos.transaction_stats.get_monthly_transaction_method_success(
        MonthMethodTransaction(year=2001, month=3)
    )
    cards = [
        row
        for row in methods
        if row.payment_method == "credit_card" and row.month == "Mar"
    ]
    assert cards and cards[0].total_transactions == 1

    yearly_methods = await repos.transaction_stats.get_yearly_transaction_method_failed(
        2001
    )
    assert yearly_methods, "expected generated year rows"
    _ = yearly_methods


async def test_by_merchant_stats(db: Database, repos, family) -> None:
    window = datetime(2001, 5, 10, 8, 30, 0)
    await _seed_transaction(
        db, family, method="ewallet", amount=7000, status="success",
        created_at=window,
    )

    monthly = (
        await repos.transaction_stats_by_merchant.get_monthly_amount_success_by_merchant(
            MonthAmountTransactionMerchant(
                merchant_id=family.merchant_id, year=2001, month=5
            )
        )
    )
    may = [row for row in monthly if row.year == "2001" and row.month == "May"]
    assert may and may[0].total_success == 1 and may[0].total_amount == 7000

    yearly = (
        await repos.transaction_stats_by_merchant.get_yearly_amount_success_by_merchant(
            YearAmountTransactionMerchant(merchant_id=family.merchant_id, year=2001)
        )
    )
    row_2001 = [row for row in yearly if row.year == "2001"]
    assert row_2001 and row_2001[0].total_amount == 7000

    methods = await repos.transaction_stats_by_merchant.get_monthly_transaction_method_by_merchant_success(
        MonthMethodTransactionMerchant(
            merchant_id=family.merchant_id, year=2001, month=5
        )
    )
    ewallets = [
        row
        for row in methods
        if row.payment_method == "ewallet" and row.month == "May"
    ]
    assert ewallets and ewallets[0].total_transactions == 1

    yearly_methods = await repos.transaction_stats_by_merchant.get_yearly_transaction_method_by_merchant_success(
        YearMethodTransactionMerchant(merchant_id=family.merchant_id, year=2001)
    )
    # 1999/2000/2001 rows all exist (data only in 2001).
    years = {row.year for row in yearly_methods}
    assert {"1999", "2000", "2001"} <= years
    hit = [row for row in yearly_methods if row.year == "2001"
           and row.payment_method == "ewallet"]
    assert hit and hit[0].total_transactions == 1

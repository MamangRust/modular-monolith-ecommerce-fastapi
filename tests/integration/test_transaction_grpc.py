"""transaction gRPC integration tests against the real handlers + PostgreSQL.

Marked `integration`. The `transaction_grpc_server` fixture runs the real four
servicers with adapters pointed at the real user/merchant/order/order_item/
shipping servers (the order server transitively starts the product server), so
the create/update saga resolves every dependency over gRPC exactly as in
production; the test seeds the real FK parents via `order_parents`.

Covers the create saga (derived amount = items + shipping + 11% PPN, status
forced to `success`, ownership resolved from the order when user_id is 0), the
insufficient-cover 400, update through the state machine, the trash/restore/
permanent-delete surface, the by-order delete, and the read/stats RPCs.
"""

from __future__ import annotations

from typing import Any

import grpc
import pytest

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
from pkg.database.database import Database

pytestmark = pytest.mark.integration

# Derived from the seeded saga data: one item (qty 2, price 5000) + shipping
# 1500 → 11500, + 11% PPN → 12765.
DERIVED_TOTAL = 12765


class Family:
    def __init__(self, user_id: int, merchant_id: int, order_id: int) -> None:
        self.user_id = user_id
        self.merchant_id = merchant_id
        self.order_id = order_id


@pytest.fixture
async def family(db: Database, order_parents):
    """order + item + shipping rows the transaction saga can resolve."""
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
    order_id = int(order["order_id"])
    await db.execute(
        """
        INSERT INTO order_items (order_id, product_id, quantity, price)
        VALUES (:order_id, :product_id, 2, 5000)
        """,
        {"order_id": order_id, "product_id": order_parents.product_id},
    )
    await db.execute(
        """
        INSERT INTO shipping_addresses (
            order_id, alamat, provinsi, kota, courier, shipping_method,
            shipping_cost, negara
        )
        VALUES (:order_id, 'Jalan Panjang', 'DKI', 'Jakarta', 'jne', 'reg',
                1500, 'Indonesia')
        """,
        {"order_id": order_id},
    )
    return Family(order_parents.user_id, order_parents.merchant_id, order_id)


async def _cleanup(db: Database, family: Family) -> None:
    await db.execute(
        "DELETE FROM outbox_events WHERE event_key LIKE 'transaction-create:%' "
        "AND CAST(message_key AS INTEGER) IN ("
        "  SELECT transaction_id FROM transactions WHERE order_id = :oid)",
        {"oid": family.order_id},
    )
    await db.execute(
        "DELETE FROM transactions WHERE order_id = :oid", {"oid": family.order_id}
    )
    await db.execute(
        "DELETE FROM shipping_addresses WHERE order_id = :oid",
        {"oid": family.order_id},
    )
    await db.execute(
        "DELETE FROM order_items WHERE order_id = :oid", {"oid": family.order_id}
    )
    await db.execute(
        "DELETE FROM orders WHERE order_id = :oid", {"oid": family.order_id}
    )


def _stub(server: str) -> tuple[Any, Any]:
    channel = grpc.aio.insecure_channel(server)
    query = transaction_query_pb2_grpc.TransactionQueryServiceStub(channel)
    command = transaction_command_pb2_grpc.TransactionCommandServiceStub(channel)
    return channel, (query, command)


async def test_create_saga_via_grpc(db: Database, family, transaction_grpc_server) -> None:
    channel, (query, command) = _stub(transaction_grpc_server)
    try:
        response = await command.Create(
            transaction_command_pb2.CreateTransactionRequest(
                order_id=family.order_id,
                merchant_id=family.merchant_id,
                payment_method="credit_card",
                amount=DERIVED_TOTAL,
                user_id=0,  # resolved from the order over gRPC
                payment_status="",
            ),
            timeout=30,
        )
        assert response.status == "success"
        assert response.message == "Successfully created transaction"
        assert response.data.order_id == family.order_id
        assert response.data.merchant_id == family.merchant_id
        # Stored amount is the derived total (caller cover == derived here).
        assert response.data.amount == DERIVED_TOTAL
        assert response.data.payment_status == "success"
        assert len(response.data.created_at) == 19  # seconds layout
        transaction_id = response.data.id

        by_id = await query.FindById(
            transaction_common_pb2.FindByIdTransactionRequest(id=transaction_id),
            timeout=30,
        )
        assert by_id.data.id == transaction_id

        by_order = await query.FindByOrderId(
            transaction_query_pb2.FindByOrderIdTransactionRequest(
                order_id=family.order_id
            ),
            timeout=30,
        )
        assert by_order.data.id == transaction_id

        await _cleanup(db, family)
    finally:
        await channel.close()


async def test_create_insufficient_cover_is_400(
    db: Database, family, transaction_grpc_server
) -> None:
    channel, (_, command) = _stub(transaction_grpc_server)
    try:
        with pytest.raises(grpc.aio.AioRpcError) as excinfo:
            await command.Create(
                transaction_command_pb2.CreateTransactionRequest(
                    order_id=family.order_id,
                    merchant_id=family.merchant_id,
                    payment_method="credit_card",
                    amount=DERIVED_TOTAL - 1,
                    user_id=family.user_id,
                    payment_status="",
                ),
                timeout=30,
            )
        assert excinfo.value.code() == grpc.StatusCode.INVALID_ARGUMENT
        assert excinfo.value.details() == "Insufficient balance"
    finally:
        await channel.close()


async def test_update_state_machine_via_grpc(
    db: Database, family, transaction_grpc_server
) -> None:
    channel, (query, command) = _stub(transaction_grpc_server)
    try:
        created = await command.Create(
            transaction_command_pb2.CreateTransactionRequest(
                order_id=family.order_id,
                merchant_id=family.merchant_id,
                payment_method="credit_card",
                amount=DERIVED_TOTAL,
                user_id=family.user_id,
                payment_status="",
            ),
            timeout=30,
        )
        transaction_id = created.data.id

        # "refunded" is a legal transition from "success"; amount 0 falls back
        # to the existing row, order/merchant 0 fall back too.
        updated = await command.Update(
            transaction_command_pb2.UpdateTransactionRequest(
                transaction_id=transaction_id,
                payment_status="refunded",
            ),
            timeout=30,
        )
        assert updated.data.payment_status == "refunded"
        assert updated.data.amount == DERIVED_TOTAL

        # A terminal "refunded" row cannot be reopened: any further change is
        # rejected ("Cannot modify payment status").
        with pytest.raises(grpc.aio.AioRpcError) as excinfo:
            await command.Update(
                transaction_command_pb2.UpdateTransactionRequest(
                    transaction_id=transaction_id,
                    payment_status="pending",
                ),
                timeout=30,
            )
        assert excinfo.value.details() == "Cannot modify payment status"

        await _cleanup(db, family)
    finally:
        await channel.close()


async def test_trash_restore_delete_via_grpc(
    db: Database, family, transaction_grpc_server
) -> None:
    channel, (query, command) = _stub(transaction_grpc_server)
    try:
        created = await command.Create(
            transaction_command_pb2.CreateTransactionRequest(
                order_id=family.order_id,
                merchant_id=family.merchant_id,
                payment_method="credit_card",
                amount=DERIVED_TOTAL,
                user_id=family.user_id,
                payment_status="",
            ),
            timeout=30,
        )
        transaction_id = created.data.id

        trashed = await command.TrashedTransaction(
            transaction_common_pb2.FindByIdTransactionRequest(id=transaction_id),
            timeout=30,
        )
        assert trashed.data.deleted_at.value != ""

        restored = await command.RestoreTransaction(
            transaction_common_pb2.FindByIdTransactionRequest(id=transaction_id),
            timeout=30,
        )
        assert not restored.data.HasField("deleted_at")

        trashed_all = await query.FindByTrashed(
            transaction_query_pb2.FindAllTransactionRequest(), timeout=30
        )
        assert trashed_all.status == "success"

        deleted = await command.DeleteTransactionPermanent(
            transaction_common_pb2.FindByIdTransactionRequest(id=transaction_id),
            timeout=30,
        )
        assert deleted.message == "Successfully deleted transaction permanently"

        # by-order delete (internal RPC, also exposed over gRPC).
        created2 = await command.Create(
            transaction_command_pb2.CreateTransactionRequest(
                order_id=family.order_id,
                merchant_id=family.merchant_id,
                payment_method="credit_card",
                amount=DERIVED_TOTAL,
                user_id=family.user_id,
                payment_status="",
            ),
            timeout=30,
        )
        deleted_by_order = await command.DeleteTransactionByOrderPermanent(
            transaction_common_pb2.FindByIdTransactionRequest(id=family.order_id),
            timeout=30,
        )
        assert (
            deleted_by_order.message
            == "Successfully deleted transactions by order permanently"
        )
        _ = created2

        left = await db.execute(
            "SELECT COUNT(*) AS n FROM transactions WHERE order_id = :oid",
            {"oid": family.order_id},
        )
        assert left is not None and int(left["n"]) == 0
    finally:
        await channel.close()


async def test_stats_via_grpc(db: Database, family, transaction_grpc_server) -> None:
    channel, (_, command) = _stub(transaction_grpc_server)
    stats_channel = grpc.aio.insecure_channel(transaction_grpc_server)
    stats = transaction_stats_pb2_grpc.TransactionStatsServiceStub(stats_channel)
    stats_merchant = (
        transaction_stats_bymerchant_pb2_grpc.TransactionStatsByMerchantServiceStub(
            stats_channel
        )
    )
    try:
        await command.Create(
            transaction_command_pb2.CreateTransactionRequest(
                order_id=family.order_id,
                merchant_id=family.merchant_id,
                payment_method="credit_card",
                amount=DERIVED_TOTAL,
                user_id=family.user_id,
                payment_status="",
            ),
            timeout=30,
        )

        response = await stats.GetYearlyAmountSuccess(
            transaction_stats_pb2.YearAmountTransactionRequest(year=2026), timeout=30
        )
        assert response.status == "success"
        current = [row for row in response.data if row.year == str(2026)]
        assert current and current[0].total_success >= 1

        response = await stats.GetMonthlyAmountFailed(
            transaction_stats_pb2.MonthAmountTransactionRequest(year=2026, month=1),
            timeout=30,
        )
        assert response.status == "success"

        response = await stats_merchant.GetYearlyAmountSuccessByMerchant(
            transaction_stats_bymerchant_pb2.YearAmountTransactionMerchantRequest(
                merchant_id=family.merchant_id, year=2026
            ),
            timeout=30,
        )
        assert response.status == "success"
        mine = [row for row in response.data if row.year == str(2026)]
        assert mine and mine[0].total_success >= 1

        await _cleanup(db, family)
    finally:
        await stats_channel.close()
        await channel.close()

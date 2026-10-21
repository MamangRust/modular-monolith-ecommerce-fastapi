"""transaction command service. `create` derives the final amount from the order itself: the merchandise total (sum of item price × quantity) plus the per-order shipping cost, plus PPN 11%. The caller's amount acts as a payment cover — it must reach the derived total (`err_failed_payment_insufficient_balance`, 400 "Insufficient balance") — but the **stored** amount is the derived total. A successful derivation forces the status to `success` through the payment state machine; a caller-supplied canonical status must be a legal transition (the state machine lives in `payment_state_machine.py`). `create` is transactional: the insert and its two outbox events (email + the merchant round-trip event) commit in one database transaction (`async with db.transaction`), then the outbox relay publishes them. The merchant event carries `{merchantId, transactionId, amount, status, timestamp}`. `update` re-derives the amount from the (possibly defaulted) order and applies the state machine against the existing row; `merchant_id`/`order_id` of 0 fall back to the existing row, as do an empty `payment_method` and amount of 0. Single mutations evict the by-id key via the namespace invalidation; the bulk ops and `delete_by_order_id_permanent` invalidate the whole `transaction:*` namespace."""

from __future__ import annotations

import json
import time
from collections.abc import Awaitable, Callable
from typing import Any

from pkg.database.database import Database
from pkg.database.schema.transaction import Transaction, TransactionRow
from pkg.event import marshal_email
from pkg.logger.logger import Logger
from pkg.outbox import Event, enqueue
from service.transaction.redis.interfaces import TransactionCommandCache
from service.transaction.repository.interfaces import (
    MerchantQueryRepository,
    OrderItemRepository,
    OrderQueryRepository,
    ShippingAddressQueryRepository,
    TransactionCommandRepository,
    TransactionQueryRepository,
    UserQueryRepository,
)
from service.transaction.service.emails import email_body
from service.transaction.service.payment_state_machine import (
    PAYMENT_STATUS_SUCCESS,
    can_transition_payment_status,
    is_valid_payment_status,
)
from shared.domain.requests.transaction import (
    CreateTransactionRecordRequest,
    CreateTransactionRequest,
    UpdateTransactionRecordRequest,
    UpdateTransactionRequest,
)
from shared.errors.transaction_errors import (
    err_failed_order_item_empty,
    err_failed_payment_insufficient_balance,
    err_failed_payment_status_cannot_be_modified,
    err_failed_payment_status_invalid,
)
from shared.observability import Observability

EnqueueFn = Callable[[Any, Event], Awaitable[None]]

_TOPIC_EMAIL = "email-service-topic-transaction-create"
_TOPIC_MERCHANT_EVENT = "merchant-service-topic-transaction-event"

_PPN_PERCENT = 11


class TransactionCommandServiceImpl:
    def __init__(
        self,
        *,
        transaction_query: TransactionQueryRepository,
        transaction_command: TransactionCommandRepository,
        user_query: UserQueryRepository,
        merchant_query: MerchantQueryRepository,
        order_query: OrderQueryRepository,
        order_item: OrderItemRepository,
        shipping_address: ShippingAddressQueryRepository,
        cache: TransactionCommandCache,
        db: Database,
        logger: Logger,
        obs: Observability,
        enqueue_fn: EnqueueFn = enqueue,
    ) -> None:
        self._transaction_query = transaction_query
        self._transaction_command = transaction_command
        self._user_query = user_query
        self._merchant_query = merchant_query
        self._order_query = order_query
        self._order_item = order_item
        self._shipping_address = shipping_address
        self._cache = cache
        self._db = db
        self._logger = logger
        self._obs = obs
        self._enqueue = enqueue_fn

    # ------------------------------------------------------------------ create

    async def create(self, request: CreateTransactionRequest) -> TransactionRow:
        with self._obs.span(
            "transaction.command.create",
            user_id=request.user_id,
            merchant_id=request.merchant_id,
            order_id=request.order_id,
        ):
            order = await self._order_query.find_by_id(request.order_id)

            # The order is the source of truth for ownership: callers that do
            # not supply a user id (for example the REST API) get it from the
            # order.
            if request.user_id == 0:
                request.user_id = int(order.user_id)

            user = await self._user_query.find_by_id(request.user_id)
            await self._merchant_query.find_by_id(request.merchant_id)

            order_items = await self._order_item.find_order_item_by_order(
                request.order_id
            )
            shipping = await self._shipping_address.find_by_order(request.order_id)

            merchandise_total = 0
            for item in order_items:
                if item.quantity <= 0 or item.price < 0:
                    raise err_failed_order_item_empty
                merchandise_total += int(item.price) * int(item.quantity)

            # Shipping is charged once per order, not once per item.
            total_amount = merchandise_total + int(shipping.shippingCost)
            ppn = total_amount * _PPN_PERCENT // 100
            total_amount_with_tax = total_amount + ppn

            # Validate the caller-supplied status (if any) before deriving the
            # final status. A create may only start from a canonical
            # non-terminal status.
            if request.payment_status != "" and not is_valid_payment_status(
                request.payment_status
            ):
                raise err_failed_payment_status_invalid

            if request.amount >= total_amount_with_tax:
                payment_status = PAYMENT_STATUS_SUCCESS
            else:
                raise err_failed_payment_insufficient_balance

            if (
                request.payment_status != ""
                and not can_transition_payment_status(
                    request.payment_status, payment_status
                )
            ):
                raise err_failed_payment_status_cannot_be_modified

            request.amount = total_amount_with_tax
            request.payment_status = payment_status

            payload = marshal_email(
                "transaction.created",
                user.email,
                "Transaction Successful - SanEdge",
                email_body(
                    "Your transaction of "
                    f"{request.amount} has been processed successfully.",
                    "View History",
                    "https://sanedge.example.com/transaction/history",
                ),
            )

            record = CreateTransactionRecordRequest(
                user_id=request.user_id,
                order_id=request.order_id,
                merchant_id=request.merchant_id,
                payment_method=request.payment_method,
                amount=request.amount,
                payment_status=request.payment_status,
            )

            async with self._db.transaction() as conn:
                transaction = await self._transaction_command.create_in_tx(
                    conn, record
                )
                merchant_payload = json.dumps(
                    {
                        "merchantId": transaction.merchant_id,
                        "transactionId": transaction.transaction_id,
                        "amount": transaction.amount,
                        "status": transaction.payment_status,
                        "timestamp": int(time.time() * 1000),
                    }
                )
                await self._enqueue(
                    conn,
                    Event(
                        event_key=(
                            f"transaction-create:{transaction.transaction_id}"
                        ),
                        topic=_TOPIC_EMAIL,
                        key=str(transaction.transaction_id),
                        payload=payload,
                    ),
                )
                await self._enqueue(
                    conn,
                    Event(
                        event_key=(
                            "transaction-merchant-event:"
                            f"{transaction.transaction_id}"
                        ),
                        topic=_TOPIC_MERCHANT_EVENT,
                        key=str(transaction.merchant_id),
                        payload=merchant_payload,
                    ),
                )

            await self._cache.invalidate_transaction_cache()

            self._logger.info(
                "transaction created", transaction_id=transaction.transaction_id
            )
            return transaction

    # ------------------------------------------------------------------ update

    async def update(self, request: UpdateTransactionRequest) -> TransactionRow:
        with self._obs.span(
            "transaction.command.update", transaction_id=request.transaction_id
        ):
            existing = await self._transaction_query.find_by_id(
                request.transaction_id
            )

            # Payment status changes must follow the canonical state machine.
            # The requested status (if provided) must be canonical and a legal
            # transition from the current status; terminal statuses cannot be
            # reopened.
            if request.payment_status != "":
                if not is_valid_payment_status(request.payment_status):
                    raise err_failed_payment_status_invalid
                if (
                    request.payment_status != existing.payment_status
                    and not can_transition_payment_status(
                        existing.payment_status, request.payment_status
                    )
                ):
                    raise err_failed_payment_status_cannot_be_modified

            if request.merchant_id == 0:
                request.merchant_id = int(existing.merchant_id)
            await self._merchant_query.find_by_id(request.merchant_id)

            if request.order_id == 0:
                request.order_id = int(existing.order_id)
            await self._order_query.find_by_id(request.order_id)

            order_items = await self._order_item.find_order_item_by_order(
                request.order_id
            )
            shipping = await self._shipping_address.find_by_order(request.order_id)

            merchandise_total = 0
            for item in order_items:
                if item.quantity <= 0 or item.price < 0:
                    raise err_failed_order_item_empty
                merchandise_total += int(item.price) * int(item.quantity)

            total_amount = merchandise_total + int(shipping.shippingCost)

            if request.amount == 0:
                request.amount = int(existing.amount)

            if request.payment_method == "":
                request.payment_method = existing.payment_method

            ppn = total_amount * _PPN_PERCENT // 100
            total_amount_with_tax = total_amount + ppn

            # Derive the final status from the verified amount. The derived
            # status must itself be a legal transition from the current status
            # (e.g. a failed transaction cannot be reopened as success by a
            # later update).
            payment_status = PAYMENT_STATUS_SUCCESS
            if request.amount < total_amount_with_tax:
                raise err_failed_payment_insufficient_balance
            if (
                request.payment_status != ""
                and can_transition_payment_status(
                    existing.payment_status, request.payment_status
                )
                and request.payment_status != PAYMENT_STATUS_SUCCESS
            ):
                payment_status = request.payment_status
            if not can_transition_payment_status(
                existing.payment_status, payment_status
            ):
                raise err_failed_payment_status_cannot_be_modified

            request.amount = total_amount_with_tax
            request.payment_status = payment_status

            transaction = await self._transaction_command.update(
                UpdateTransactionRecordRequest(
                    transaction_id=request.transaction_id,
                    order_id=request.order_id,
                    merchant_id=request.merchant_id,
                    payment_method=request.payment_method,
                    amount=request.amount,
                    payment_status=request.payment_status,
                )
            )

            await self._cache.delete_transaction_cache(request.transaction_id)

            self._logger.info(
                "transaction updated", transaction_id=transaction.transaction_id
            )
            return transaction

    # --------------------------------------------------- single-row transitions

    async def trash(self, transaction_id: int) -> Transaction:
        with self._obs.span(
            "transaction.command.trash", transaction_id=transaction_id
        ):
            res = await self._transaction_command.trash(transaction_id)
            await self._cache.delete_transaction_cache(transaction_id)
            self._logger.info("transaction trashed", transaction_id=transaction_id)
            return res

    async def restore(self, transaction_id: int) -> Transaction:
        with self._obs.span(
            "transaction.command.restore", transaction_id=transaction_id
        ):
            res = await self._transaction_command.restore(transaction_id)
            await self._cache.delete_transaction_cache(transaction_id)
            self._logger.info("transaction restored", transaction_id=transaction_id)
            return res

    async def delete_permanent(self, transaction_id: int) -> bool:
        with self._obs.span(
            "transaction.command.delete_permanent", transaction_id=transaction_id
        ):
            success = await self._transaction_command.delete_permanent(transaction_id)
            await self._cache.delete_transaction_cache(transaction_id)
            self._logger.info(
                "transaction deleted permanently", transaction_id=transaction_id
            )
            return success

    # ------------------------------------------------------------- bulk + by-order

    async def delete_by_order_id_permanent(self, order_id: int) -> bool:
        with self._obs.span(
            "transaction.command.delete_by_order_id_permanent", order_id=order_id
        ):
            success = await self._transaction_command.delete_by_order_id_permanent(
                order_id
            )
            await self._cache.invalidate_transaction_cache()
            self._logger.info(
                "transactions deleted permanently by order", order_id=order_id
            )
            return success

    async def restore_all(self) -> bool:
        with self._obs.span("transaction.command.restore_all"):
            success = await self._transaction_command.restore_all()
            await self._cache.invalidate_transaction_cache()
            self._logger.info("all transactions restored")
            return success

    async def delete_all(self) -> bool:
        with self._obs.span("transaction.command.delete_all"):
            success = await self._transaction_command.delete_all()
            await self._cache.invalidate_transaction_cache()
            self._logger.info("all transactions deleted permanently")
            return success


__all__ = ["EnqueueFn", "TransactionCommandServiceImpl"]

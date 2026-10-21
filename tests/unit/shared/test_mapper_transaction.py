"""Unit tests for the transaction REST mappers. `deleted_at` is always emitted (`""` when the proto wrapper is absent — sets the pointer unconditionally); timestamps pass through already formatted."""

from __future__ import annotations

from typing import Any

from pb.transaction import transaction_common_pb2
from shared.mapper.transaction import (
    map_monthly_method,
    map_transaction_response,
    map_transaction_response_delete_at,
    to_api_response_pagination_transaction,
    to_api_response_transaction,
    to_api_response_transaction_delete,
    to_api_response_transaction_delete_at,
)


def _pb_transaction() -> Any:
    pb = transaction_common_pb2.TransactionResponse(
        id=5,
        order_id=42,
        merchant_id=3,
        payment_method="ewallet",
        amount=78900,
        payment_status="success",
        created_at="2026-01-02 03:04:05",
        updated_at="2026-01-03 04:05:06",
    )
    return pb


def test_map_transaction_response() -> None:
    mapped = map_transaction_response(_pb_transaction())
    assert mapped.id == 5
    assert mapped.order_id == 42
    assert mapped.merchant_id == 3
    assert mapped.payment_method == "ewallet"
    assert mapped.amount == 78900
    assert mapped.created_at == "2026-01-02 03:04:05"


def test_map_delete_at_always_emits_key() -> None:
    pb = transaction_common_pb2.TransactionResponseDeleteAt(id=5)
    mapped = map_transaction_response_delete_at(pb)
    assert mapped.deleted_at == ""

    pb = transaction_common_pb2.TransactionResponseDeleteAt(id=5)
    pb.deleted_at.value = "2026-02-01 06:07:08"
    mapped = map_transaction_response_delete_at(pb)
    assert mapped.deleted_at == "2026-02-01 06:07:08"


def test_api_response_envelopes() -> None:
    envelope = transaction_common_pb2.ApiResponseTransaction(
        status="success", message="Successfully fetched transaction"
    )
    envelope.data.CopyFrom(_pb_transaction())
    api = to_api_response_transaction(envelope)
    assert api.status == "success"
    assert api.data is not None and api.data.id == 5

    delete_envelope = transaction_common_pb2.ApiResponseTransactionDelete(
        status="success", message="Successfully deleted transaction permanently"
    )
    delete_api = to_api_response_transaction_delete(delete_envelope)
    assert delete_api.data is None

    at_envelope = transaction_common_pb2.ApiResponseTransactionDeleteAt(
        status="success", message="Successfully trashed transaction"
    )
    at_envelope.data.CopyFrom(
        transaction_common_pb2.TransactionResponseDeleteAt(id=5)
    )
    at_api = to_api_response_transaction_delete_at(at_envelope)
    assert at_api.data is not None and at_api.data.deleted_at == ""


def test_pagination_envelope() -> None:
    pb = transaction_common_pb2.ApiResponsePaginationTransaction(
        status="success", message="Successfully fetched transactions"
    )
    pb.data.add().CopyFrom(_pb_transaction())
    pb.pagination.current_page = 2
    pb.pagination.page_size = 10
    pb.pagination.total_pages = 5
    pb.pagination.total_records = 42

    api = to_api_response_pagination_transaction(pb)
    assert api.data is not None and len(api.data) == 1
    assert api.pagination.current_page == 2
    assert api.pagination.total_records == 42


def test_map_monthly_method() -> None:
    pb = transaction_common_pb2.TransactionMonthlyMethod(
        month="Jan",
        payment_method="ewallet",
        total_transactions=3,
        total_amount=12000,
    )
    mapped = map_monthly_method(pb)
    assert mapped.month == "Jan"
    assert mapped.total_transactions == 3
    assert mapped.total_amount == 12000

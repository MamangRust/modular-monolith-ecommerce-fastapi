"""Unit tests for the order item response mapper.

Covers both input shapes: row dataclasses (which the mapper formats) and
proto messages (which it passes through). The order item timestamp layout
(`%Y-%m-%d %H:%M:%S.mmm`) matches banner, not category's date-only form, so it
is asserted explicitly. The `...DeleteAt` proto only sets the wrapper when
non-empty, so an absent wrapper must render as `""`.
"""

from __future__ import annotations

from datetime import datetime

from pb.order_item import order_item_common_pb2
from pkg.database.schema.order_item import (
    CreateOrderItemRow,
    GetOrderItemsActiveRow,
    GetOrderItemsByOrderRow,
    GetOrderItemsRow,
    OrderItem,
)
from shared.mapper.order_item import (
    map_order_item_response,
    map_order_item_response_delete_at,
    map_pagination_meta,
    to_api_response_order_item,
    to_api_response_order_item_delete,
    to_api_response_pagination_order_item,
    to_api_response_pagination_order_item_delete_at,
    to_api_responses_order_item,
    to_order_item_response,
    to_order_item_response_delete_at,
)

CREATED = datetime(2026, 1, 2, 3, 4, 5, 123456)
UPDATED = datetime(2026, 1, 3, 4, 5, 6, 654321)
DELETED = datetime(2026, 2, 1, 10, 0, 0, 500000)


def _row() -> GetOrderItemsRow:
    return GetOrderItemsRow(
        order_item_id=1,
        order_id=10,
        product_id=20,
        quantity=2,
        price=5000,
        created_at=CREATED,
        updated_at=UPDATED,
        total_count=1,
    )


def _active_row() -> GetOrderItemsActiveRow:
    return GetOrderItemsActiveRow(
        order_item_id=2,
        order_id=11,
        product_id=21,
        quantity=3,
        price=6000,
        created_at=CREATED,
        updated_at=UPDATED,
        deleted_at=DELETED,
        total_count=1,
    )


def test_row_mapping_formats_order_item_timestamps() -> None:
    result = to_order_item_response(_row())
    assert result.id == 1
    assert result.order_id == 10
    assert result.product_id == 20
    assert result.quantity == 2
    assert result.price == 5000
    assert result.created_at == "2026-01-02 03:04:05.123"
    assert result.updated_at == "2026-01-03 04:05:06.654"


def test_row_mapping_delete_at_includes_deleted_at() -> None:
    result = to_order_item_response_delete_at(_active_row())
    assert result.id == 2
    assert result.deleted_at == "2026-02-01 10:00:00.500"


def test_row_mapping_accepts_all_row_shapes() -> None:
    create_row = CreateOrderItemRow(
        order_item_id=3,
        order_id=12,
        product_id=22,
        quantity=4,
        price=7000,
        created_at=CREATED,
        updated_at=UPDATED,
    )
    order_item = OrderItem(
        order_item_id=4,
        order_id=13,
        product_id=23,
        quantity=5,
        price=8000,
        created_at=CREATED,
        updated_at=UPDATED,
        deleted_at=None,
    )
    by_order = GetOrderItemsByOrderRow(
        order_item_id=5,
        order_id=14,
        product_id=24,
        quantity=6,
        price=9000,
        created_at=CREATED,
        updated_at=UPDATED,
    )
    assert to_order_item_response(create_row).id == 3
    assert to_order_item_response(by_order).product_id == 24
    # A restored row carries a None deleted_at, which formats to "".
    assert to_order_item_response_delete_at(order_item).deleted_at == ""


def _proto_order_item() -> order_item_common_pb2.OrderItemResponse:
    return order_item_common_pb2.OrderItemResponse(
        id=7,
        order_id=17,
        product_id=27,
        quantity=7,
        price=10000,
        created_at="2026-05-06 07:08:09.101",
        updated_at="2026-05-07 08:09:10.202",
    )


def test_proto_mapping_passes_strings_through_unchanged() -> None:
    message = order_item_common_pb2.ApiResponseOrderItem(
        status="success", message="ok"
    )
    message.data.CopyFrom(_proto_order_item())
    dumped = to_api_response_order_item(message).model_dump()
    assert dumped["data"] == {
        "id": 7,
        "order_id": 17,
        "product_id": 27,
        "quantity": 7,
        "price": 10000,
        "created_at": "2026-05-06 07:08:09.101",
        "updated_at": "2026-05-07 08:09:10.202",
    }


def test_proto_delete_at_missing_renders_empty_string() -> None:
    message = order_item_common_pb2.OrderItemResponseDeleteAt(id=1)
    mapped = map_order_item_response_delete_at(message)
    assert mapped.deleted_at == ""


def test_proto_delete_at_present_passes_through() -> None:
    message = order_item_common_pb2.OrderItemResponseDeleteAt(id=1)
    message.deleted_at.value = "2026-02-03 04:05:06.700"
    mapped = map_order_item_response_delete_at(message)
    assert mapped.deleted_at == "2026-02-03 04:05:06.700"


def test_proto_response_mapping_uses_rest_field_id() -> None:
    mapped = map_order_item_response(_proto_order_item())
    assert mapped.id == 7
    assert mapped.price == 10000


def test_multi_response_mapping() -> None:
    message = order_item_common_pb2.ApiResponsesOrderItem(
        status="success", message="ok"
    )
    message.data.add(id=1, order_id=10)
    message.data.add(id=2, order_id=10)
    dumped = to_api_responses_order_item(message).model_dump()
    assert [row["id"] for row in dumped["data"]] == [1, 2]


def test_pagination_mapping() -> None:
    message = order_item_common_pb2.ApiResponsePaginationOrderItem(
        status="success", message="ok"
    )
    message.data.add(id=1, order_id=10)
    message.pagination.current_page = 2
    message.pagination.page_size = 5
    message.pagination.total_pages = 3
    message.pagination.total_records = 11
    dumped = to_api_response_pagination_order_item(message).model_dump()
    assert dumped["data"][0]["order_id"] == 10
    assert dumped["pagination"] == {
        "current_page": 2,
        "page_size": 5,
        "total_pages": 3,
        "total_records": 11,
    }


def test_trashed_pagination_delete_at() -> None:
    message = order_item_common_pb2.ApiResponsePaginationOrderItemDeleteAt(
        status="success", message="ok"
    )
    message.data.add(id=9)
    message.data[0].deleted_at.value = "2026-02-03 00:00:00.000"
    dumped = to_api_response_pagination_order_item_delete_at(message).model_dump()
    assert dumped["data"][0]["deleted_at"] == "2026-02-03 00:00:00.000"


def test_delete_envelope_has_no_data() -> None:
    message = order_item_common_pb2.ApiResponseOrderItemDelete(
        status="success", message="deleted"
    )
    dumped = to_api_response_order_item_delete(message).model_dump()
    assert dumped == {"status": "success", "message": "deleted", "data": None}


def test_map_pagination_meta_none_defaults() -> None:
    meta = map_pagination_meta(None)
    assert meta.current_page == 1
    assert meta.total_records == 0

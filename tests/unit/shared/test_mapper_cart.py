"""Unit tests for the cart REST mappers.

The proto already carries date-only strings (`%Y-%m-%d`), so the mapper passes
them through unchanged. `id` is the wire name on both sides and `image` maps
straight across.
"""

from __future__ import annotations

from pb.cart import cart_common_pb2
from shared.mapper.cart import (
    map_cart_response,
    map_pagination_meta,
    to_api_response_cart,
    to_api_response_cart_all,
    to_api_response_cart_delete,
    to_api_response_pagination_cart,
    to_api_responses_carts,
)


def _proto_cart(**overrides):
    values = {
        "id": 7,
        "user_id": 5,
        "product_id": 10,
        "name": "Galaxy S24",
        "price": 1200,
        "image": "uploads/products/galaxy-s24.jpg",
        "quantity": 2,
        "weight": 200,
        "created_at": "2026-05-06",
        "updated_at": "2026-05-07",
    }
    values.update(overrides)
    return cart_common_pb2.CartResponse(**values)


def test_cart_proto_mapping_passes_strings_through() -> None:
    message = cart_common_pb2.ApiResponseCart(status="success", message="ok")
    message.data.CopyFrom(_proto_cart())
    dumped = to_api_response_cart(message).model_dump()
    assert dumped["data"] == {
        "id": 7,
        "user_id": 5,
        "product_id": 10,
        "name": "Galaxy S24",
        "price": 1200,
        "image": "uploads/products/galaxy-s24.jpg",
        "quantity": 2,
        "weight": 200,
        "created_at": "2026-05-06",
        "updated_at": "2026-05-07",
    }


def test_cart_plain_list_api_response() -> None:
    message = cart_common_pb2.ApiResponseCart(status="success", message="ok")
    message.data.id = 1
    single = to_api_response_cart(message).model_dump()
    assert single["data"]["id"] == 1

    list_message = cart_common_pb2.ApiResponsePaginationCart(
        status="success", message="ok"
    )
    list_message.data.add(id=1, user_id=5, name="A")
    list_message.data.add(id=2, user_id=5, name="B")
    dumped = to_api_responses_carts(list_message).model_dump()
    assert [row["id"] for row in dumped["data"]] == [1, 2]


def test_cart_pagination_mapping() -> None:
    message = cart_common_pb2.ApiResponsePaginationCart(
        status="success", message="ok"
    )
    message.data.add(id=1, user_id=5, name="A")
    message.pagination.current_page = 2
    message.pagination.page_size = 5
    message.pagination.total_pages = 3
    message.pagination.total_records = 11
    dumped = to_api_response_pagination_cart(message).model_dump()
    assert dumped["data"][0]["id"] == 1
    assert dumped["pagination"] == {
        "current_page": 2,
        "page_size": 5,
        "total_pages": 3,
        "total_records": 11,
    }


def test_cart_delete_and_all_envelopes() -> None:
    deleted = cart_common_pb2.ApiResponseCartDelete(
        status="success", message="Successfully deleted cart item permanently"
    )
    assert to_api_response_cart_delete(deleted).model_dump()["data"] is None

    all_message = cart_common_pb2.ApiResponseCartAll(
        status="success", message="Successfully deleted all cart items permanently"
    )
    assert to_api_response_cart_all(all_message).message == (
        "Successfully deleted all cart items permanently"
    )


def test_map_pagination_meta_none_defaults() -> None:
    meta = map_pagination_meta(None)
    assert meta.current_page == 1
    assert meta.total_records == 0


def test_map_cart_response_uses_defaults_for_zero_values() -> None:
    proto = cart_common_pb2.CartResponse(id=1)
    mapped = map_cart_response(proto)
    assert mapped.user_id == 0
    assert mapped.name == ""
    assert mapped.image == ""


__all__ = []

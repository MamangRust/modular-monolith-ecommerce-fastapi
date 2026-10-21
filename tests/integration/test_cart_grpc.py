"""cart gRPC integration tests. Marked `integration`. Runs the two real cart servicers behind an ephemeral port; the `cart_grpc_server` fixture points the cart user/product adapters at the real user and product servers (both spun up by their own fixtures). Tests seed the real user + merchant + category + product rows the cart FKs and adapters need. Verifies the wire contract (date-only `%Y-%m-%d` timestamps, the cart envelopes) and the error mapping: - an invalid create body -> 400 `validation failed: invalid create cart request`; - `quantity > count_in_stock` -> 400 `Insufficient product stock`; - a missing product -> 404 `product not found` (adapter: any error is remapped to the product-not-found sentinel); - a missing owner -> 404 (user adapter)."""

from __future__ import annotations

import uuid

import grpc
import pytest

from pb.cart import (
    cart_command_pb2,
    cart_command_pb2_grpc,
    cart_query_pb2,
    cart_query_pb2_grpc,
)
from pkg.database.database import Database
from shared.errors import parse_grpc_error

pytestmark = pytest.mark.integration


async def _seed(db: Database) -> tuple[int, int, int, int]:
    email = f"test_cart_grpc_{uuid.uuid4().hex[:10]}@example.com"
    merchant_name = f"Merchant {uuid.uuid4().hex[:10]}"
    category_name = f"Category {uuid.uuid4().hex[:10]}"
    user = await db.execute(
        """
        INSERT INTO users (firstname, lastname, email, password, verification_code)
        VALUES ('T', 'U', :email, 'x', 'v')
        RETURNING user_id
        """,
        {"email": email},
    )
    assert user is not None
    user_id = int(user["user_id"])
    merchant = await db.execute(
        """
        INSERT INTO merchants (
            user_id, name, description, address, contact_email, contact_phone, status
        )
        VALUES (:user_id, :name, 'd', 'a', 'e@f.com', '0812', 'active')
        RETURNING merchant_id
        """,
        {"user_id": user_id, "name": merchant_name},
    )
    assert merchant is not None
    merchant_id = int(merchant["merchant_id"])
    category = await db.execute(
        """
        INSERT INTO categories (name, description, slug_category, image_category)
        VALUES (:name, 'd', :slug, 'img.jpg')
        RETURNING category_id
        """,
        {"name": category_name, "slug": uuid.uuid4().hex[:10]},
    )
    assert category is not None
    category_id = int(category["category_id"])
    product = await db.execute(
        """
        INSERT INTO products (
            merchant_id, category_id, name, description, price,
            count_in_stock, brand, weight, rating, slug_product, image_product
        )
        VALUES (
            :mid, :cid, :name, 'd', 1200, 5, 'Samsung', 200, 4.5, :slug, 'galaxy-s24.jpg'
        )
        RETURNING product_id
        """,
        {
            "mid": merchant_id,
            "cid": category_id,
            "name": f"Galaxy S24 {uuid.uuid4().hex[:6]}",
            "slug": f"galaxy-{uuid.uuid4().hex[:8]}",
        },
    )
    assert product is not None
    product_id = int(product["product_id"])
    return user_id, product_id, merchant_id, category_id


async def _cleanup(db: Database, user_id: int, merchant_id: int, category_id: int) -> None:
    await db.execute("DELETE FROM carts WHERE user_id = :uid", {"uid": user_id})
    await db.execute(
        "DELETE FROM products WHERE merchant_id = :mid", {"mid": merchant_id}
    )
    await db.execute(
        "DELETE FROM categories WHERE category_id = :cid", {"cid": category_id}
    )
    await db.execute(
        "DELETE FROM merchants WHERE merchant_id = :mid", {"mid": merchant_id}
    )
    await db.execute("DELETE FROM users WHERE user_id = :uid", {"uid": user_id})


async def test_cart_grpc_lifecycle(db: Database, cart_grpc_server: str) -> None:
    channel = grpc.aio.insecure_channel(cart_grpc_server)
    query = cart_query_pb2_grpc.CartQueryServiceStub(channel)
    command = cart_command_pb2_grpc.CartCommandServiceStub(channel)

    user_id, product_id, merchant_id, category_id = await _seed(db)
    try:
        created = await command.Create(
            cart_command_pb2.CreateCartRequest(
                product_id=product_id, user_id=user_id, quantity=2
            ),
            timeout=5,
        )
        assert created.message == "Successfully created cart"
        assert created.data.user_id == user_id
        assert created.data.product_id == product_id
        assert created.data.price == 1200
        assert created.data.image == "galaxy-s24.jpg"
        assert created.data.weight == 200
        assert created.data.quantity == 2
        # Date-only wire format (unlike product's .mmm).
        assert len(created.data.created_at) == 10
        cart_id = created.data.id

        listed = await query.FindAll(
            cart_query_pb2.FindAllCartRequest(user_id=user_id, page=1, page_size=10),
            timeout=5,
        )
        assert listed.message == "Successfully fetched cart items"
        assert listed.pagination.total_records >= 1
        assert any(r.id == cart_id for r in listed.data)

        deleted = await command.Delete(
            cart_command_pb2.DeleteCartRequest(cart_id=cart_id, user_id=user_id),
            timeout=5,
        )
        assert deleted.message == "Successfully deleted cart item permanently"

        after_delete = await query.FindAll(
            cart_query_pb2.FindAllCartRequest(user_id=user_id, page=1, page_size=10),
            timeout=5,
        )
        assert all(r.id != cart_id for r in after_delete.data)

        first = await command.Create(
            cart_command_pb2.CreateCartRequest(
                product_id=product_id, user_id=user_id, quantity=1
            ),
            timeout=5,
        )
        second = await command.Create(
            cart_command_pb2.CreateCartRequest(
                product_id=product_id, user_id=user_id, quantity=1
            ),
            timeout=5,
        )
        deleted_all = await command.DeleteAll(
            cart_command_pb2.DeleteAllCartRequest(
                user_id=user_id, cart_ids=[first.data.id, second.data.id]
            ),
            timeout=5,
        )
        assert deleted_all.message == "Successfully deleted all cart items permanently"

        final = await query.FindAll(
            cart_query_pb2.FindAllCartRequest(user_id=user_id, page=1, page_size=10),
            timeout=5,
        )
        assert final.pagination.total_records == 0
    finally:
        await channel.close()
        await _cleanup(db, user_id, merchant_id, category_id)


async def test_cart_grpc_error_mapping(db: Database, cart_grpc_server: str) -> None:
    channel = grpc.aio.insecure_channel(cart_grpc_server)
    command = cart_command_pb2_grpc.CartCommandServiceStub(channel)

    user_id, product_id, merchant_id, category_id = await _seed(db)
    try:
        # An invalid create body fails validation.
        with pytest.raises(grpc.aio.AioRpcError) as bad_body:
            await command.Create(
                cart_command_pb2.CreateCartRequest(
                    product_id=product_id, user_id=user_id, quantity=0
                ),
                timeout=5,
            )
        assert bad_body.value.code() is grpc.StatusCode.INVALID_ARGUMENT
        assert parse_grpc_error(bad_body.value).message == (
            "Validation failed: invalid create cart request"
        )

        # quantity > count_in_stock (5) -> 400.
        with pytest.raises(grpc.aio.AioRpcError) as stock:
            await command.Create(
                cart_command_pb2.CreateCartRequest(
                    product_id=product_id, user_id=user_id, quantity=6
                ),
                timeout=5,
            )
        assert stock.value.code() is grpc.StatusCode.INVALID_ARGUMENT
        assert parse_grpc_error(stock.value).message == "Insufficient product stock"

        # A missing product is remapped to the product-not-found sentinel (404).
        with pytest.raises(grpc.aio.AioRpcError) as missing_product:
            await command.Create(
                cart_command_pb2.CreateCartRequest(
                    product_id=2_000_000_000, user_id=user_id, quantity=1
                ),
                timeout=5,
            )
        assert missing_product.value.code() is grpc.StatusCode.NOT_FOUND
        assert parse_grpc_error(missing_product.value).code == 404

        # A missing owner fails the user adapter (404).
        with pytest.raises(grpc.aio.AioRpcError) as missing_user:
            await command.Create(
                cart_command_pb2.CreateCartRequest(
                    product_id=product_id, user_id=2_000_000_000, quantity=1
                ),
                timeout=5,
            )
        assert missing_user.value.code() is grpc.StatusCode.NOT_FOUND
        assert parse_grpc_error(missing_user.value).code == 404
    finally:
        await channel.close()
        await _cleanup(db, user_id, merchant_id, category_id)


__all__ = []

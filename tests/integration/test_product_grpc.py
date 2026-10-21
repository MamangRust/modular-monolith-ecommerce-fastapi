"""product gRPC integration tests. Marked `integration`. Runs the two real product servicers behind an ephemeral port (the `product_grpc_server` fixture also stands up tiny category/merchant `FindById` stubs so the command service's adapter checks succeed). Tests seed the real merchant + category rows the product FKs require. Verifies the wire contract (`.mmm` timestamps, the stock rows emitting only `id`/`count_in_stock`, the `deleted_at` wrapper only on the `...DeleteAt` projections, the product envelopes for delete/restore-all) and the error mapping: - `Update id == 0` -> 400 `invalid ID`; - an invalid create body -> 400 `validation failed: invalid create product request`; - a repository 404 stays NOT_FOUND; - a create for a non-existent parent (FK violation) is remapped to the service's 500 sentinel."""

from __future__ import annotations

import uuid

import grpc
import pytest
from google.protobuf import empty_pb2

from pb.product import (
    product_command_pb2,
    product_command_pb2_grpc,
    product_common_pb2,
    product_query_pb2,
    product_query_pb2_grpc,
)
from pkg.database.database import Database
from shared.errors import parse_grpc_error

pytestmark = pytest.mark.integration


async def _seed(db: Database) -> tuple[int, int, int, str, str]:
    email = f"test_product_grpc_{uuid.uuid4().hex[:10]}@example.com"
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
    return user_id, merchant_id, category_id, merchant_name, category_name


async def _cleanup(db: Database, user_id: int, merchant_id: int, category_id: int) -> None:
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


def _create_pb(merchant_id: int, category_id: int, **overrides):
    values = {
        "merchant_id": merchant_id,
        "category_id": category_id,
        "name": f"Galaxy S24 {uuid.uuid4().hex[:6]}",
        "description": "desc",
        "price": 1200,
        "count_in_stock": 5,
        "brand": "Samsung",
        "weight": 200,
        "rating": 4,
        "slug_product": f"galaxy-{uuid.uuid4().hex[:8]}",
        "image_product": "uploads/products/galaxy.jpg",
    }
    values.update(overrides)
    return product_command_pb2.CreateProductRequest(**values)


async def test_product_grpc_lifecycle(db: Database, product_grpc_server: str) -> None:
    channel = grpc.aio.insecure_channel(product_grpc_server)
    query = product_query_pb2_grpc.ProductQueryServiceStub(channel)
    command = product_command_pb2_grpc.ProductCommandServiceStub(channel)

    user_id, merchant_id, category_id, _, category_name = await _seed(db)
    try:
        created = await command.Create(
            _create_pb(merchant_id, category_id), timeout=5
        )
        assert created.message == "Successfully created product"
        assert created.data.merchant_id == merchant_id
        assert len(created.data.created_at) == 23
        assert created.data.rating == 4.0
        product_id = created.data.id

        found = await query.FindById(
            product_common_pb2.FindByIdProductRequest(id=product_id), timeout=5
        )
        assert found.message == "Successfully fetched product"
        assert found.data.id == product_id

        listed = await query.FindAll(
            product_query_pb2.FindAllProductRequest(
                page=1, page_size=10, search=created.data.name
            ),
            timeout=5,
        )
        assert listed.pagination.total_records >= 1
        assert any(r.id == product_id for r in listed.data)

        by_merchant = await query.FindByMerchant(
            product_query_pb2.FindAllProductMerchantRequest(
                merchant_id=merchant_id, page=1, page_size=10
            ),
            timeout=5,
        )
        assert by_merchant.message == "Successfully fetched merchant products"
        assert any(r.id == product_id for r in by_merchant.data)

        by_category = await query.FindByCategory(
            product_query_pb2.FindAllProductCategoryRequest(
                category_name=category_name, page=1, page_size=10
            ),
            timeout=5,
        )
        assert by_category.message == "Successfully fetched category products"
        assert any(r.id == product_id for r in by_category.data)

        updated = await command.Update(
            product_command_pb2.UpdateProductRequest(
                product_id=product_id,
                merchant_id=merchant_id,
                category_id=category_id,
                name="Galaxy S25 Ultra",
                description="updated",
                price=1500,
                count_in_stock=8,
                brand="Samsung",
                weight=210,
                rating=5,
                slug_product=created.data.slug_product,
                image_product=created.data.image_product,
            ),
            timeout=5,
        )
        assert updated.message == "Successfully updated product"
        assert updated.data.name == "Galaxy S25 Ultra"
        assert updated.data.rating == 5.0

        count_stock = await command.UpdateProductCountStock(
            product_command_pb2.UpdateProductCountStockRequest(
                product_id=product_id, stock=20
            ),
            timeout=5,
        )
        assert count_stock.data.id == product_id
        assert count_stock.data.count_in_stock == 20
        # The stock projection carries no other columns.
        assert count_stock.data.name == ""
        assert count_stock.data.created_at == ""

        adjusted = await command.AdjustProductStock(
            product_command_pb2.AdjustProductStockRequest(
                product_id=product_id, delta=-5, operation_id=uuid.uuid4().hex
            ),
            timeout=5,
        )
        assert adjusted.data.count_in_stock == 15

        trashed = await command.TrashedProduct(
            product_common_pb2.FindByIdProductRequest(id=product_id), timeout=5
        )
        assert trashed.message == "Successfully trashed product"
        # Single-row trash omits `deleted_at`.
        assert trashed.data.HasField("deleted_at") is False

        trashed_rows = await query.FindByTrashed(
            product_query_pb2.FindAllProductRequest(
                page=1, page_size=10, search="Galaxy S25"
            ),
            timeout=5,
        )
        assert any(
            r.id == product_id and r.deleted_at.value for r in trashed_rows.data
        )

        restored = await command.RestoreProduct(
            product_common_pb2.FindByIdProductRequest(id=product_id), timeout=5
        )
        assert restored.message == "Successfully restored product"

        deleted = await command.DeleteProductPermanent(
            product_common_pb2.FindByIdProductRequest(id=product_id), timeout=5
        )
        assert deleted.message == "Successfully deleted product permanently"
    finally:
        await channel.close()
        await _cleanup(db, user_id, merchant_id, category_id)


async def test_product_grpc_error_mapping(
    db: Database, product_grpc_server: str
) -> None:
    channel = grpc.aio.insecure_channel(product_grpc_server)
    command = product_command_pb2_grpc.ProductCommandServiceStub(channel)
    query = product_query_pb2_grpc.ProductQueryServiceStub(channel)

    user_id, merchant_id, category_id, _, _ = await _seed(db)
    try:
        # Update guards id == 0.
        with pytest.raises(grpc.aio.AioRpcError) as invalid:
            await command.Update(
                product_command_pb2.UpdateProductRequest(
                    product_id=0,
                    merchant_id=merchant_id,
                    category_id=category_id,
                    name="n",
                    description="d",
                    price=1,
                    count_in_stock=1,
                    brand="b",
                    weight=1,
                    rating=5,
                    slug_product="s",
                    image_product="i",
                ),
                timeout=5,
            )
        assert invalid.value.code() is grpc.StatusCode.INVALID_ARGUMENT
        assert parse_grpc_error(invalid.value).message == "invalid ID"

        # An invalid create body fails validation.
        with pytest.raises(grpc.aio.AioRpcError) as bad_body:
            await command.Create(
                _create_pb(merchant_id, category_id, name=""), timeout=5
            )
        assert bad_body.value.code() is grpc.StatusCode.INVALID_ARGUMENT
        assert parse_grpc_error(bad_body.value).message == (
            "validation failed: invalid create product request"
        )

        # A missing product stays NOT_FOUND.
        with pytest.raises(grpc.aio.AioRpcError) as missing:
            await query.FindById(
                product_common_pb2.FindByIdProductRequest(id=2_000_000_000),
                timeout=5,
            )
        assert missing.value.code() is grpc.StatusCode.NOT_FOUND
        assert parse_grpc_error(missing.value).code == 404

        # A create whose parent merchant does not exist violates the FK; the
        # repository 500 is remapped by the service to its own 500 sentinel.
        with pytest.raises(grpc.aio.AioRpcError) as bad_create:
            await command.Create(
                _create_pb(2_000_000_000, category_id), timeout=5
            )
        assert bad_create.value.code() is grpc.StatusCode.INTERNAL
        assert parse_grpc_error(bad_create.value).message == (
            "failed to create product"
        )
    finally:
        await channel.close()
        await _cleanup(db, user_id, merchant_id, category_id)


async def test_product_grpc_bulk(db: Database, product_grpc_server: str) -> None:
    channel = grpc.aio.insecure_channel(product_grpc_server)
    query = product_query_pb2_grpc.ProductQueryServiceStub(channel)
    command = product_command_pb2_grpc.ProductCommandServiceStub(channel)

    user_id, merchant_id, category_id, _, _ = await _seed(db)
    try:
        created = await command.Create(_create_pb(merchant_id, category_id), timeout=5)
        product_id = created.data.id

        await command.TrashedProduct(
            product_common_pb2.FindByIdProductRequest(id=product_id), timeout=5
        )
        restored_all = await command.RestoreAllProduct(empty_pb2.Empty(), timeout=5)
        assert restored_all.message == "Successfully restored all products"

        active = await query.FindByActive(
            product_query_pb2.FindAllProductRequest(
                page=1, page_size=10, search=created.data.name
            ),
            timeout=5,
        )
        assert any(r.id == product_id for r in active.data)

        await command.TrashedProduct(
            product_common_pb2.FindByIdProductRequest(id=product_id), timeout=5
        )
        deleted_all = await command.DeleteAllProductPermanent(
            empty_pb2.Empty(), timeout=5
        )
        assert deleted_all.message == "Successfully deleted all products permanently"
    finally:
        await channel.close()
        await _cleanup(db, user_id, merchant_id, category_id)


__all__ = []

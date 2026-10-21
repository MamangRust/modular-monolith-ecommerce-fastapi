"""End-to-end journey through the real REST gateway (marked `e2e`).

One test walks the full ecommerce flow over HTTP, exactly as a client would:

register → verify-code → login → /me → category → merchant → product →
 cart → order (multi-service saga) → transaction (payment derivation) →
 review

Every domain behind the gateway is the REAL service on an ephemeral gRPC port
(the fixtures spin up PostgreSQL-backed handlers), so cross-domain adapters,
caches and the JWT middleware all run for real. Role validation is the
`RoleValidatorGRPC` middleware contract: the freshly registered user carries
the default ROLE_ADMIN, but the role-query route demands the seeded
"Admin_Role_10" permission role, so the route answers 403 "Role not
permitted".

Run with `make e2e` (deselected from `make test` / `make test-int`)."""

from __future__ import annotations

import uuid

import grpc
import httpx
import pytest
from fastapi import FastAPI

from pkg.auth import TokenManager
from pkg.database.database import Database
from pkg.logger.logger import get_logger
from pkg.upload_image import new_image_upload
from service.apigateway.app.client import ServiceConnections
from service.apigateway.handler import register_routers
from service.apigateway.handler.category import handler as category_handler
from service.apigateway.handler.product import handler as product_handler
from service.apigateway.middlewares.auth import JwtAuthMiddleware
from service.apigateway.middlewares.role_grpc import RoleValidatorGRPC
from service.apigateway.redis.role import RoleCache
from shared.cache import CacheStore
from shared.errorhandler import register_exception_handlers

pytestmark = pytest.mark.e2e

EMAIL_PREFIX = "e2e_"


def _email() -> str:
    return f"{EMAIL_PREFIX}{uuid.uuid4().hex[:12]}@test.example"


def _app(
    servers: dict[str, str],
    channels: list[grpc.aio.Channel],
    cache_store: CacheStore,
    token_manager: TokenManager,
) -> FastAPI:
    """The full gateway surface wired to the real domain servers."""
    connections = ServiceConnections(
        channels=dict(zip(servers, channels, strict=True)),
        addresses=dict(servers),
    )
    app = FastAPI()
    app.state.logger = get_logger("test-e2e")
    app.state.connections = connections
    app.state.cache_store = cache_store
    app.state.token_manager = token_manager
    app.state.upload_image = new_image_upload(get_logger("test-e2e"))
    app.state.role_validator = RoleValidatorGRPC(
        connections.channel("role"), RoleCache(cache_store, get_logger("test-e2e")), get_logger("test-e2e")
    )
    register_exception_handlers(app)
    app.add_middleware(JwtAuthMiddleware)
    register_routers(app)
    return app


def _order_body(merchant_id: int, user_id: int, product_id: int) -> dict:
    return {
        "merchant_id": merchant_id,
        "user_id": user_id,
        "total_price": 1,
        "items": [{"product_id": product_id, "quantity": 2, "price": 5000}],
        "shipping_address": {
            "alamat": "Jalan E2E No 1",
            "provinsi": "DKI Jakarta",
            "kota": "Jakarta",
            "courier": "jne",
            "shipping_method": "reg",
            "shipping_cost": 15000,
            "negara": "Indonesia",
        },
    }


async def test_gateway_e2e_journey(
    db: Database,
    cache_store: CacheStore,
    token_manager: TokenManager,
    auth_grpc_server: str,
    role_grpc_server: str,
    user_grpc_server: str,
    category_grpc_server: str,
    merchant_grpc_server: str,
    product_grpc_server: str,
    cart_grpc_server: str,
    shipping_address_grpc_server: str,
    order_item_grpc_server: str,
    order_grpc_server: str,
    transaction_grpc_server: str,
    review_grpc_server: str,
    tmp_path,
    monkeypatch,
) -> None:
    monkeypatch.setattr(category_handler, "_UPLOAD_DIR", str(tmp_path / "category"))
    monkeypatch.setattr(product_handler, "_UPLOAD_DIR", str(tmp_path / "products"))

    domains = {
        "auth": auth_grpc_server,
        "role": role_grpc_server,
        "user": user_grpc_server,
        "category": category_grpc_server,
        "merchant": merchant_grpc_server,
        "product": product_grpc_server,
        "cart": cart_grpc_server,
        "shipping_address": shipping_address_grpc_server,
        "order_item": order_item_grpc_server,
        "order": order_grpc_server,
        "transaction": transaction_grpc_server,
        "review": review_grpc_server,
    }
    channels = [
        grpc.aio.insecure_channel(address) for address in domains.values()
    ]
    app = _app(domains, channels, cache_store, token_manager)
    email = _email()

    transport = httpx.ASGITransport(app=app)
    try:
        async with httpx.AsyncClient(
            transport=transport, base_url="http://test"
        ) as client:
            # ------------------------------------------------ auth: register
            registered = await client.post(
                "/api/auth/register",
                json={
                    "firstname": "EndtoEnd",
                    "lastname": "Journey",
                    "email": email,
                    "password": "secret1",
                    "confirm_password": "secret1",
                },
            )
            assert registered.status_code == 201, registered.text
            user_id = registered.json()["data"]["id"]

            # -------------------------------------- auth: verify then login
            code_row = await db.scalar(
                "SELECT verification_code FROM users WHERE user_id = :id",
                {"id": user_id},
            )
            verified = await client.post(
                "/api/auth/verify-code",
                json={"code": code_row["verification_code"]},
            )
            assert verified.status_code == 200

            logged_in = await client.post(
                "/api/auth/login", json={"email": email, "password": "secret1"}
            )
            assert logged_in.status_code == 200
            token = logged_in.json()["data"]["access_token"]
            headers = {"Authorization": f"Bearer {token}"}

            me = await client.get("/api/auth/me", headers=headers)
            assert me.status_code == 200
            assert me.json()["data"]["email"] == email

            # -------------------------------------------- role validation
            # Register assigns the default ROLE_ADMIN, but the role-query
            # route requires the seeded "Admin_Role_10" permission role — the
            # RoleValidatorGRPC + require_roles contract answers 403 "Role not
            # permitted" (401 only fires for a user with NO roles at all).
            forbidden = await client.get("/api/role-query", headers=headers)
            assert forbidden.status_code == 403
            assert forbidden.json()["message"] == "Role not permitted"

            # ------------------------------------------------- category
            suffix = uuid.uuid4().hex[:10]
            created_category = await client.post(
                "/api/category-command/create",
                data={
                    "name": f"E2E Category {suffix}",
                    "description": "e2e journey",
                    "slug_category": f"e2e-{suffix}",
                    "image_category": "e2e.png",
                },
                files={"image": ("e2e.png", b"img", "image/png")},
                headers=headers,
            )
            assert created_category.status_code == 201, created_category.text
            category_id = created_category.json()["data"]["id"]

            # ------------------------------------------------- merchant
            created_merchant = await client.post(
                "/api/merchant-command/create",
                json={
                    "name": f"E2E Merchant {suffix}",
                    "description": "e2e journey",
                    "address": "a",
                    "contact_email": "e2e@f.com",
                    "contact_phone": "0812",
                    "status": "active",
                },
                headers=headers,
            )
            assert created_merchant.status_code == 201, created_merchant.text
            merchant_id = created_merchant.json()["data"]["id"]
            assert created_merchant.json()["data"]["status"] == "active"

            # -------------------------------------------------- product
            created_product = await client.post(
                "/api/product-command/create",
                data={
                    "merchant_id": str(merchant_id),
                    "category_id": str(category_id),
                    "name": f"E2E Product {suffix}",
                    "description": "e2e journey",
                    "price": "5000",
                    "count_in_stock": "100",
                    "brand": "E2E",
                    "weight": "100",
                    "slug_product": f"e2e-product-{suffix}",
                },
                files={"image": ("prod.png", b"img", "image/png")},
                headers=headers,
            )
            assert created_product.status_code == 201, created_product.text
            product_id = created_product.json()["data"]["id"]

            # ----------------------------------------------------- cart
            created_cart = await client.post(
                "/api/cart-command/create",
                json={"product_id": product_id, "quantity": 1},
                headers=headers,
            )
            assert created_cart.status_code == 201, created_cart.text
            assert created_cart.json()["data"]["user_id"] == user_id

            # ------------------------------- order (multi-service saga)
            created_order = await client.post(
                "/api/order-command/create",
                json=_order_body(merchant_id, user_id, product_id),
                headers=headers,
            )
            assert created_order.status_code == 200, created_order.text
            order_body = created_order.json()
            assert order_body["message"] == "Successfully created order"
            assert order_body["data"]["total_price"] == 25000  # 2*5000 + 15000
            order_id = order_body["data"]["id"]

            # Items + shipping were created by the saga over real adapters.
            items = await client.get(
                f"/api/order-item/order/{order_id}", headers=headers
            )
            assert items.status_code == 200
            assert len(items.json()["data"]) == 1
            shipping = await client.get(
                f"/api/shipping-address-query/order/{order_id}", headers=headers
            )
            assert shipping.status_code == 200
            assert shipping.json()["data"]["shipping_cost"] == 15000

            # ------------------------- transaction (payment derivation)
            # Derived amount: items 2*5000 + shipping 15000 = 25000, +11% PPN
            # = 27750; the stored amount is the DERIVED total and the status
            # is forced to `success`.
            derived_total = 27750
            created_transaction = await client.post(
                "/api/transaction-command/create",
                json={
                    "order_id": order_id,
                    "merchant_id": merchant_id,
                    "payment_method": "credit_card",
                    "amount": derived_total,
                    "payment_status": "",
                },
                headers=headers,
            )
            assert created_transaction.status_code == 201, created_transaction.text
            tx_body = created_transaction.json()
            assert tx_body["message"] == "Successfully created transaction"
            assert tx_body["data"]["amount"] == derived_total
            assert tx_body["data"]["payment_status"] == "success"
            assert tx_body["data"]["order_id"] == order_id
            transaction_id = tx_body["data"]["id"]

            by_id = await client.get(
                f"/api/transaction-query/{transaction_id}", headers=headers
            )
            assert by_id.status_code == 200
            assert by_id.json()["data"]["order_id"] == order_id

            # --------------------------------------------------- review
            created_review = await client.post(
                "/api/review-command/create",
                json={
                    "product_id": product_id,
                    "rating": 5,
                    "comment": "E2E journey review!",
                },
                headers=headers,
            )
            assert created_review.status_code == 201, created_review.text
            review_body = created_review.json()
            assert review_body["data"]["user_id"] == user_id
            assert review_body["data"]["product_id"] == product_id

            by_product = await client.get(
                f"/api/review-query/product/{product_id}", headers=headers
            )
            assert by_product.status_code == 200
            # The data list carries the review (the by-product route's
            assert by_product.json()["data"] is not None
            assert by_product.json()["data"][0]["id"] == review_body["data"]["id"]
    finally:
        for channel in channels:
            await channel.close()
        await _cleanup(db, email)


async def _cleanup(db: Database, email: str) -> None:
    pattern = f"{EMAIL_PREFIX}%"
    user = await db.scalar(
        "SELECT user_id FROM users WHERE email = :email", {"email": email}
    )
    if user is None:
        return
    user_id = int(user["user_id"])
    # Children first, then parents (FK order).
    await db.execute(
        "DELETE FROM transactions WHERE order_id IN "
        "(SELECT order_id FROM orders WHERE user_id = :uid)",
        {"uid": user_id},
    )
    await db.execute(
        "DELETE FROM order_stock_reservations WHERE order_id IN "
        "(SELECT order_id FROM orders WHERE user_id = :uid)",
        {"uid": user_id},
    )
    await db.execute(
        "DELETE FROM order_items WHERE order_id IN "
        "(SELECT order_id FROM orders WHERE user_id = :uid)",
        {"uid": user_id},
    )
    await db.execute(
        "DELETE FROM shipping_addresses WHERE order_id IN "
        "(SELECT order_id FROM orders WHERE user_id = :uid)",
        {"uid": user_id},
    )
    await db.execute("DELETE FROM orders WHERE user_id = :uid", {"uid": user_id})
    await db.execute("DELETE FROM carts WHERE user_id = :uid", {"uid": user_id})
    await db.execute(
        "DELETE FROM review_details WHERE review_id IN "
        "(SELECT review_id FROM reviews WHERE user_id = :uid)",
        {"uid": user_id},
    )
    await db.execute("DELETE FROM reviews WHERE user_id = :uid", {"uid": user_id})
    await db.execute(
        "DELETE FROM products WHERE merchant_id IN "
        "(SELECT merchant_id FROM merchants WHERE user_id = :uid)",
        {"uid": user_id},
    )
    await db.execute(
        "DELETE FROM merchant_documents WHERE merchant_id IN "
        "(SELECT merchant_id FROM merchants WHERE user_id = :uid)",
        {"uid": user_id},
    )
    await db.execute("DELETE FROM merchants WHERE user_id = :uid", {"uid": user_id})
    await db.execute(
        "DELETE FROM categories WHERE slug_category LIKE 'e2e-%'"
    )
    await db.execute(
        "DELETE FROM outbox_events WHERE payload->>'email' LIKE :pattern",
        {"pattern": pattern},
    )
    await db.execute("DELETE FROM refresh_tokens WHERE user_id = :uid", {"uid": user_id})
    await db.execute("DELETE FROM user_roles WHERE user_id = :uid", {"uid": user_id})
    await db.execute("DELETE FROM users WHERE user_id = :uid", {"uid": user_id})

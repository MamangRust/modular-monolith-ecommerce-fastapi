"""Gateway HTTP handlers and router registration.

Per-domain routers are appended here as their stages land (ecommerce order:
role, user, auth, category, merchant* , product, cart, shipping_address,
review*, order*, transaction).
"""

from __future__ import annotations

from fastapi import FastAPI

from service.apigateway.handler.auth import router as auth_router
from service.apigateway.handler.banner import command_router as banner_command_router
from service.apigateway.handler.banner import query_router as banner_query_router
from service.apigateway.handler.cart import command_router as cart_command_router
from service.apigateway.handler.cart import query_router as cart_query_router
from service.apigateway.handler.category import command_router as category_command_router
from service.apigateway.handler.category import query_router as category_query_router
from service.apigateway.handler.category import stats_router as category_stats_router
from service.apigateway.handler.merchant import (
    command_router as merchant_command_router,
)
from service.apigateway.handler.merchant import query_router as merchant_query_router
from service.apigateway.handler.merchant_award import (
    command_router as merchant_award_command_router,
)
from service.apigateway.handler.merchant_award import (
    query_router as merchant_award_query_router,
)
from service.apigateway.handler.merchant_business import (
    command_router as merchant_business_command_router,
)
from service.apigateway.handler.merchant_business import (
    query_router as merchant_business_query_router,
)
from service.apigateway.handler.merchant_detail import (
    command_router as merchant_detail_command_router,
)
from service.apigateway.handler.merchant_detail import (
    query_router as merchant_detail_query_router,
)
from service.apigateway.handler.merchant_document import (
    command_router as merchant_document_command_router,
)
from service.apigateway.handler.merchant_document import (
    query_router as merchant_document_query_router,
)
from service.apigateway.handler.merchant_policy import (
    command_router as merchant_policy_command_router,
)
from service.apigateway.handler.merchant_policy import (
    query_router as merchant_policy_query_router,
)
from service.apigateway.handler.merchant_social_link import (
    command_router as merchant_social_link_command_router,
)
from service.apigateway.handler.order import command_router as order_command_router
from service.apigateway.handler.order import query_router as order_query_router
from service.apigateway.handler.order import stats_router as order_stats_router
from service.apigateway.handler.order_item import command_router as order_item_command_router
from service.apigateway.handler.order_item import query_router as order_item_query_router
from service.apigateway.handler.product import (
    command_router as product_command_router,
)
from service.apigateway.handler.product import query_router as product_query_router
from service.apigateway.handler.review import (
    command_router as review_command_router,
)
from service.apigateway.handler.review import query_router as review_query_router
from service.apigateway.handler.review_detail import (
    command_router as review_detail_command_router,
)
from service.apigateway.handler.review_detail import (
    query_router as review_detail_query_router,
)
from service.apigateway.handler.role import command_router as role_command_router
from service.apigateway.handler.role import query_router as role_query_router
from service.apigateway.handler.shipping_address import (
    command_router as shipping_address_command_router,
)
from service.apigateway.handler.shipping_address import (
    query_router as shipping_address_query_router,
)
from service.apigateway.handler.slider import command_router as slider_command_router
from service.apigateway.handler.slider import query_router as slider_query_router
from service.apigateway.handler.transaction import (
    command_router as transaction_command_router,
)
from service.apigateway.handler.transaction import (
    query_router as transaction_query_router,
)
from service.apigateway.handler.transaction import (
    stats_router as transaction_stats_router,
)
from service.apigateway.handler.user import command_router as user_command_router
from service.apigateway.handler.user import query_router as user_query_router


def register_routers(app: FastAPI) -> None:
    """Register every domain router on the gateway app."""
    app.include_router(auth_router)
    app.include_router(banner_query_router)
    app.include_router(banner_command_router)
    app.include_router(cart_query_router)
    app.include_router(cart_command_router)
    app.include_router(category_query_router)
    app.include_router(category_command_router)
    app.include_router(category_stats_router)
    app.include_router(merchant_query_router)
    app.include_router(merchant_command_router)
    app.include_router(merchant_document_query_router)
    app.include_router(merchant_document_command_router)
    app.include_router(merchant_award_query_router)
    app.include_router(merchant_award_command_router)
    app.include_router(merchant_business_query_router)
    app.include_router(merchant_business_command_router)
    app.include_router(merchant_detail_query_router)
    app.include_router(merchant_detail_command_router)
    app.include_router(merchant_policy_query_router)
    app.include_router(merchant_policy_command_router)
    app.include_router(merchant_social_link_command_router)
    app.include_router(product_query_router)
    app.include_router(product_command_router)
    app.include_router(order_query_router)
    app.include_router(order_command_router)
    app.include_router(order_stats_router)
    app.include_router(order_item_query_router)
    app.include_router(order_item_command_router)
    app.include_router(role_query_router)
    app.include_router(role_command_router)
    app.include_router(shipping_address_query_router)
    app.include_router(shipping_address_command_router)
    app.include_router(slider_query_router)
    app.include_router(slider_command_router)
    app.include_router(transaction_query_router)
    app.include_router(transaction_command_router)
    app.include_router(transaction_stats_router)
    app.include_router(review_query_router)
    app.include_router(review_command_router)
    app.include_router(review_detail_query_router)
    app.include_router(review_detail_command_router)
    app.include_router(user_query_router)
    app.include_router(user_command_router)

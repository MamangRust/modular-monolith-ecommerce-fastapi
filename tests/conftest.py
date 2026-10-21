"""Shared test fixtures: PostgreSQL/Redis integration fixtures plus ephemeral grpc.aio servers for the verticals (role, user, auth). Integration fixtures skip gracefully when the infrastructure is unavailable (`make test` runs unit-only; `make test-int` needs the compose infra up)."""

from __future__ import annotations

import uuid
from collections.abc import AsyncIterator
from typing import NamedTuple

import grpc
import pytest

from pb.auth import auth_pb2_grpc
from pb.banner import banner_command_pb2_grpc, banner_query_pb2_grpc
from pb.cart import cart_command_pb2_grpc, cart_query_pb2_grpc
from pb.category import (
    category_command_pb2_grpc,
    category_common_pb2,
    category_query_pb2_grpc,
)
from pb.category.stats import (
    category_stats_byid_pb2_grpc,
    category_stats_bymerchant_pb2_grpc,
    category_stats_pb2_grpc,
)
from pb.merchant import (
    merchant_command_pb2_grpc,
    merchant_common_pb2,
    merchant_query_pb2_grpc,
)
from pb.merchant_award import (
    merchant_award_command_pb2_grpc,
    merchant_award_query_pb2_grpc,
)
from pb.merchant_business import (
    merchant_business_command_pb2_grpc,
    merchant_business_query_pb2_grpc,
)
from pb.merchant_detail import (
    merchant_detail_command_pb2_grpc,
    merchant_detail_query_pb2_grpc,
)
from pb.merchant_document import (
    merchant_document_command_pb2_grpc,
    merchant_document_query_pb2_grpc,
)
from pb.merchant_policy import (
    merchant_policy_command_pb2_grpc,
    merchant_policy_query_pb2_grpc,
)
from pb.merchant_social_link import merchant_social_link_command_pb2_grpc
from pb.order import order_command_pb2_grpc, order_query_pb2_grpc
from pb.order.stats import (
    order_stats_pb2_grpc,
    order_statsbymerchant_pb2_grpc,
)
from pb.order_item import order_item_command_pb2_grpc, order_item_query_pb2_grpc
from pb.product import product_command_pb2_grpc, product_query_pb2_grpc
from pb.review import review_command_pb2_grpc, review_query_pb2_grpc
from pb.review_detail import (
    review_detail_command_pb2_grpc,
    review_detail_query_pb2_grpc,
)
from pb.role import role_command_pb2_grpc, role_query_pb2_grpc
from pb.shipping_address import (
    shipping_address_command_pb2_grpc,
    shipping_address_query_pb2_grpc,
)
from pb.slider import slider_command_pb2_grpc, slider_query_pb2_grpc
from pb.transaction import (
    transaction_command_pb2_grpc,
    transaction_query_pb2_grpc,
)
from pb.transaction.stats import (
    transaction_stats_bymerchant_pb2_grpc,
    transaction_stats_pb2_grpc,
)
from pb.user import user_command_pb2_grpc, user_query_pb2_grpc
from pkg.adapter.guard import default_guard
from pkg.auth import TokenManager, new_manager
from pkg.config.settings import get_settings
from pkg.database.database import Database
from pkg.logger.logger import get_logger
from pkg.redis.redis import close_redis, new_redis_client
from service.auth.handler import new_handler as new_auth_handler
from service.auth.repository import (
    GuardOptions as AuthGuardOptions,
)
from service.auth.repository import (
    new_repositories as new_auth_repositories,
)
from service.auth.service import new_service as new_auth_service
from service.banner.handler import new_handler as new_banner_handler
from service.banner.repository import new_repositories as new_banner_repositories
from service.banner.service import new_service as new_banner_service
from service.cart.handler import new_handler as new_cart_handler
from service.cart.redis import new_mencache as new_cart_mencache
from service.cart.repository import (
    GuardOptions as CartGuardOptions,
)
from service.cart.repository import (
    new_repositories as new_cart_repositories,
)
from service.cart.service import new_service as new_cart_service
from service.category.handler import new_handler as new_category_handler
from service.category.repository import new_repositories as new_category_repositories
from service.category.service import new_service as new_category_service
from service.merchant.handler import new_handler as new_merchant_handler
from service.merchant.redis import new_mencache as new_merchant_mencache
from service.merchant.repository import (
    GuardOptions as MerchantGuardOptions,
)
from service.merchant.repository import (
    new_repositories as new_merchant_repositories,
)
from service.merchant.service import new_service as new_merchant_service
from service.merchant_award.handler import new_handler as new_merchant_award_handler
from service.merchant_award.redis import new_mencache as new_merchant_award_mencache
from service.merchant_award.repository import (
    GuardOptions as MerchantAwardGuardOptions,
)
from service.merchant_award.repository import (
    new_repositories as new_merchant_award_repositories,
)
from service.merchant_award.service import new_service as new_merchant_award_service
from service.merchant_business.handler import (
    new_handler as new_merchant_business_handler,
)
from service.merchant_business.redis import (
    new_mencache as new_merchant_business_mencache,
)
from service.merchant_business.repository import (
    GuardOptions as MerchantBusinessGuardOptions,
)
from service.merchant_business.repository import (
    new_repositories as new_merchant_business_repositories,
)
from service.merchant_business.service import (
    new_service as new_merchant_business_service,
)
from service.merchant_detail.handler import new_handler as new_merchant_detail_handler
from service.merchant_detail.redis import (
    new_mencache as new_merchant_detail_mencache,
)
from service.merchant_detail.repository import (
    GuardOptions as MerchantDetailGuardOptions,
)
from service.merchant_detail.repository import (
    new_repositories as new_merchant_detail_repositories,
)
from service.merchant_detail.service import new_service as new_merchant_detail_service
from service.merchant_policy.handler import (
    new_handler as new_merchant_policy_handler,
)
from service.merchant_policy.redis import (
    new_mencache as new_merchant_policy_mencache,
)
from service.merchant_policy.repository import (
    GuardOptions as MerchantPolicyGuardOptions,
)
from service.merchant_policy.repository import (
    new_repositories as new_merchant_policy_repositories,
)
from service.merchant_policy.service import (
    new_service as new_merchant_policy_service,
)
from service.order.handler import new_handler as new_order_handler
from service.order.redis import new_mencache as new_order_mencache
from service.order.repository import (
    GuardOptions as OrderGuardOptions,
)
from service.order.repository import (
    new_repositories as new_order_repositories,
)
from service.order.service import new_service as new_order_service
from service.order_item.handler import new_handler as new_order_item_handler
from service.order_item.repository import (
    new_repositories as new_order_item_repositories,
)
from service.order_item.service import new_service as new_order_item_service
from service.product.handler import new_handler as new_product_handler
from service.product.redis import new_mencache as new_product_mencache
from service.product.repository import (
    GuardOptions as ProductGuardOptions,
)
from service.product.repository import (
    new_repositories as new_product_repositories,
)
from service.product.service import new_service as new_product_service
from service.review.handler import new_handler as new_review_handler
from service.review.redis import new_mencache as new_review_mencache
from service.review.repository import (
    GuardOptions as ReviewGuardOptions,
)
from service.review.repository import (
    new_repositories as new_review_repositories,
)
from service.review.service import new_service as new_review_service
from service.review_detail.handler import new_handler as new_review_detail_handler
from service.review_detail.repository import (
    new_repositories as new_review_detail_repositories,
)
from service.review_detail.service import new_service as new_review_detail_service
from service.role.handler import new_handler
from service.role.repository import new_repositories
from service.role.service import new_service
from service.shipping_address.handler import (
    new_handler as new_shipping_address_handler,
)
from service.shipping_address.repository import (
    new_repositories as new_shipping_address_repositories,
)
from service.shipping_address.service import new_service as new_shipping_address_service
from service.slider.handler import new_handler as new_slider_handler
from service.slider.repository import new_repositories as new_slider_repositories
from service.slider.service import new_service as new_slider_service
from service.transaction.handler import new_handler as new_transaction_handler
from service.transaction.redis import new_mencache as new_transaction_mencache
from service.transaction.repository import (
    GuardOptions as TransactionGuardOptions,
)
from service.transaction.repository import (
    new_repositories as new_transaction_repositories,
)
from service.transaction.service import new_service as new_transaction_service
from service.user.handler import new_handler as new_user_handler
from service.user.repository import new_repositories as new_user_repositories
from service.user.service import new_service as new_user_service
from shared.cache import CacheStore


@pytest.fixture
async def db() -> AsyncIterator[Database]:
    settings = get_settings()
    if not settings.database.db_host:
        pytest.skip("DB_HOST not configured")
    database = Database.create(settings.database, get_logger("test-role"))
    try:
        await database.ping()
    except Exception as exc:
        pytest.skip(f"PostgreSQL unavailable: {exc}")
    try:
        yield database
    finally:
        await database.close()


@pytest.fixture
async def redis_client():
    settings = get_settings()
    if not settings.redis.redis_host:
        pytest.skip("REDIS_HOST not configured")
    try:
        client = await new_redis_client(settings.redis, "test-role", get_logger("test-role"))
    except Exception as exc:
        pytest.skip(f"Redis unavailable: {exc}")
    try:
        yield client
    finally:
        await close_redis(client, get_logger("test-role"))


@pytest.fixture
async def cache_store(redis_client):
    return CacheStore(redis_client, get_logger("test-role"))


@pytest.fixture
async def role_grpc_server(db: Database, cache_store: CacheStore) -> AsyncIterator[str]:
    """Run the real role handlers on an ephemeral grpc.aio port."""
    logger = get_logger("test-role")
    service = new_service(new_repositories(db), cache_store, logger)
    handler = new_handler(service, logger)

    server = grpc.aio.server()
    role_query_pb2_grpc.add_RoleQueryServiceServicer_to_server(handler.role_query, server)
    role_command_pb2_grpc.add_RoleCommandServiceServicer_to_server(handler.role_command, server)
    port = server.add_insecure_port("127.0.0.1:0")
    await server.start()
    try:
        yield f"127.0.0.1:{port}"
    finally:
        await server.stop(0)


@pytest.fixture
async def user_grpc_server(db: Database, cache_store: CacheStore) -> AsyncIterator[str]:
    """Run the real user handlers on an ephemeral grpc.aio port."""
    logger = get_logger("test-user")
    service = new_user_service(new_user_repositories(db), cache_store, logger)
    handler = new_user_handler(service, logger)

    server = grpc.aio.server()
    user_query_pb2_grpc.add_UserQueryServiceServicer_to_server(handler.user_query, server)
    user_command_pb2_grpc.add_UserCommandServiceServicer_to_server(handler.user_command, server)
    port = server.add_insecure_port("127.0.0.1:0")
    await server.start()
    try:
        yield f"127.0.0.1:{port}"
    finally:
        await server.stop(0)


@pytest.fixture
async def banner_grpc_server(db: Database, cache_store: CacheStore) -> AsyncIterator[str]:
    """Run the real banner handlers on an ephemeral grpc.aio port."""
    logger = get_logger("test-banner")
    service = new_banner_service(new_banner_repositories(db), cache_store, logger)
    handler = new_banner_handler(service, logger)

    server = grpc.aio.server()
    banner_query_pb2_grpc.add_BannerQueryServiceServicer_to_server(handler.banner_query, server)
    banner_command_pb2_grpc.add_BannerCommandServiceServicer_to_server(handler.banner_command, server)
    port = server.add_insecure_port("127.0.0.1:0")
    await server.start()
    try:
        yield f"127.0.0.1:{port}"
    finally:
        await server.stop(0)


@pytest.fixture
async def category_grpc_server(db: Database, cache_store: CacheStore) -> AsyncIterator[str]:
    """Run the real category handlers (all five servicers) on an ephemeral port."""
    logger = get_logger("test-category")
    service = new_category_service(new_category_repositories(db), cache_store, logger)
    handler = new_category_handler(service, logger)

    server = grpc.aio.server()
    category_query_pb2_grpc.add_CategoryQueryServiceServicer_to_server(handler.category_query, server)
    category_command_pb2_grpc.add_CategoryCommandServiceServicer_to_server(handler.category_command, server)
    category_stats_pb2_grpc.add_CategoryStatsServiceServicer_to_server(handler.category_stats, server)
    category_stats_byid_pb2_grpc.add_CategoryStatsByIdServiceServicer_to_server(
        handler.category_stats_by_id, server
    )
    category_stats_bymerchant_pb2_grpc.add_CategoryStatsByMerchantServiceServicer_to_server(
        handler.category_stats_by_merchant, server
    )
    port = server.add_insecure_port("127.0.0.1:0")
    await server.start()
    try:
        yield f"127.0.0.1:{port}"
    finally:
        await server.stop(0)


@pytest.fixture
async def order_item_grpc_server(db: Database, cache_store: CacheStore) -> AsyncIterator[str]:
    """Run the real order item handlers on an ephemeral grpc.aio port."""
    logger = get_logger("test-order-item")
    service = new_order_item_service(new_order_item_repositories(db), cache_store, logger)
    handler = new_order_item_handler(service, logger)

    server = grpc.aio.server()
    order_item_query_pb2_grpc.add_OrderItemQueryServiceServicer_to_server(handler.order_item_query, server)
    order_item_command_pb2_grpc.add_OrderItemCommandServiceServicer_to_server(
        handler.order_item_command, server
    )
    port = server.add_insecure_port("127.0.0.1:0")
    await server.start()
    try:
        yield f"127.0.0.1:{port}"
    finally:
        await server.stop(0)


@pytest.fixture
async def shipping_address_grpc_server(db: Database, cache_store: CacheStore) -> AsyncIterator[str]:
    """Run the real shipping address handlers on an ephemeral grpc.aio port."""
    logger = get_logger("test-shipping-address")
    service = new_shipping_address_service(new_shipping_address_repositories(db), cache_store, logger)
    handler = new_shipping_address_handler(service, logger)

    server = grpc.aio.server()
    shipping_address_query_pb2_grpc.add_ShippingQueryServiceServicer_to_server(
        handler.shipping_address_query, server
    )
    shipping_address_command_pb2_grpc.add_ShippingCommandServiceServicer_to_server(
        handler.shipping_address_command, server
    )
    port = server.add_insecure_port("127.0.0.1:0")
    await server.start()
    try:
        yield f"127.0.0.1:{port}"
    finally:
        await server.stop(0)


@pytest.fixture
async def slider_grpc_server(db: Database, cache_store: CacheStore) -> AsyncIterator[str]:
    """Run the real slider handlers on an ephemeral grpc.aio port."""
    logger = get_logger("test-slider")
    service = new_slider_service(new_slider_repositories(db), cache_store, logger)
    handler = new_slider_handler(service, logger)

    server = grpc.aio.server()
    slider_query_pb2_grpc.add_SliderQueryServiceServicer_to_server(handler.slider_query, server)
    slider_command_pb2_grpc.add_SliderCommandServiceServicer_to_server(handler.slider_command, server)
    port = server.add_insecure_port("127.0.0.1:0")
    await server.start()
    try:
        yield f"127.0.0.1:{port}"
    finally:
        await server.stop(0)


@pytest.fixture
async def review_detail_grpc_server(db: Database, cache_store: CacheStore) -> AsyncIterator[str]:
    """Run the real review detail handlers on an ephemeral grpc.aio port."""
    logger = get_logger("test-review-detail")
    service = new_review_detail_service(new_review_detail_repositories(db), cache_store, logger)
    handler = new_review_detail_handler(service, logger)

    server = grpc.aio.server()
    review_detail_query_pb2_grpc.add_ReviewDetailQueryServiceServicer_to_server(
        handler.review_detail_query, server
    )
    review_detail_command_pb2_grpc.add_ReviewDetailCommandServiceServicer_to_server(
        handler.review_detail_command, server
    )
    port = server.add_insecure_port("127.0.0.1:0")
    await server.start()
    try:
        yield f"127.0.0.1:{port}"
    finally:
        await server.stop(0)


@pytest.fixture
async def merchant_grpc_server(
    db: Database, cache_store: CacheStore, user_grpc_server: str
) -> AsyncIterator[str]:
    """Run the real merchant handlers (four servicers) on an ephemeral port. Merchant resolves owners over gRPC, so this fixture also spins up the user server and points the merchant repositories' guarded user adapter at it."""
    logger = get_logger("test-merchant")
    channel_user = grpc.aio.insecure_channel(user_grpc_server)
    guards = MerchantGuardOptions(user=default_guard("user", logger))
    repos = new_merchant_repositories(db, user_channel=channel_user, guards=guards)
    mencache = new_merchant_mencache(cache_store, logger)
    service = new_merchant_service(repos, mencache, db, None, logger)
    handler = new_merchant_handler(service, logger)

    server = grpc.aio.server()
    merchant_query_pb2_grpc.add_MerchantQueryServiceServicer_to_server(handler.merchant_query, server)
    merchant_command_pb2_grpc.add_MerchantCommandServiceServicer_to_server(handler.merchant_command, server)
    merchant_document_query_pb2_grpc.add_MerchantDocumentQueryServiceServicer_to_server(
        handler.merchant_document_query, server
    )
    merchant_document_command_pb2_grpc.add_MerchantDocumentCommandServiceServicer_to_server(
        handler.merchant_document_command, server
    )
    port = server.add_insecure_port("127.0.0.1:0")
    await server.start()
    try:
        yield f"127.0.0.1:{port}"
    finally:
        await server.stop(0)
        await channel_user.close()


@pytest.fixture
async def merchant_detail_grpc_server(
    db: Database, cache_store: CacheStore, merchant_grpc_server: str
) -> AsyncIterator[str]:
    """Run the real merchant_detail handlers (three servicers) on an ephemeral port. merchant_detail resolves the parent merchant over gRPC, so this fixture also spins up the merchant server and points the merchant_detail repositories' guarded merchant adapter at it."""
    logger = get_logger("test-merchant-detail")
    channel_merchant = grpc.aio.insecure_channel(merchant_grpc_server)
    guards = MerchantDetailGuardOptions(merchant=default_guard("merchant", logger))
    repos = new_merchant_detail_repositories(db, merchant_channel=channel_merchant, guards=guards)
    mencache = new_merchant_detail_mencache(cache_store, logger)
    service = new_merchant_detail_service(repos, mencache, logger)
    handler = new_merchant_detail_handler(service, logger)

    server = grpc.aio.server()
    merchant_detail_query_pb2_grpc.add_MerchantDetailQueryServiceServicer_to_server(
        handler.merchant_detail_query, server
    )
    merchant_detail_command_pb2_grpc.add_MerchantDetailCommandServiceServicer_to_server(
        handler.merchant_detail_command, server
    )
    merchant_social_link_command_pb2_grpc.add_MerchantSocialCommandServiceServicer_to_server(
        handler.merchant_social_link_command, server
    )
    port = server.add_insecure_port("127.0.0.1:0")
    await server.start()
    try:
        yield f"127.0.0.1:{port}"
    finally:
        await server.stop(0)
        await channel_merchant.close()


@pytest.fixture
async def merchant_award_grpc_server(db: Database, cache_store: CacheStore) -> AsyncIterator[str]:
    """Run the real merchant_award handlers (two servicers) on an ephemeral port."""
    logger = get_logger("test-merchant-award")
    channel_merchant = grpc.aio.insecure_channel("127.0.0.1:1")
    repos = new_merchant_award_repositories(
        db, merchant_channel=channel_merchant, guards=MerchantAwardGuardOptions()
    )
    mencache = new_merchant_award_mencache(cache_store, logger)
    service = new_merchant_award_service(repos, mencache, logger)
    handler = new_merchant_award_handler(service, logger)

    server = grpc.aio.server()
    merchant_award_query_pb2_grpc.add_MerchantAwardQueryServiceServicer_to_server(
        handler.merchant_award_query, server
    )
    merchant_award_command_pb2_grpc.add_MerchantAwardCommandServiceServicer_to_server(
        handler.merchant_award_command, server
    )
    port = server.add_insecure_port("127.0.0.1:0")
    await server.start()
    try:
        yield f"127.0.0.1:{port}"
    finally:
        await server.stop(0)
        await channel_merchant.close()


@pytest.fixture
async def merchant_business_grpc_server(db: Database, cache_store: CacheStore) -> AsyncIterator[str]:
    """Run the real merchant_business handlers (two servicers) on an ephemeral port."""
    logger = get_logger("test-merchant-business")
    channel_merchant = grpc.aio.insecure_channel("127.0.0.1:1")
    repos = new_merchant_business_repositories(
        db, merchant_channel=channel_merchant, guards=MerchantBusinessGuardOptions()
    )
    mencache = new_merchant_business_mencache(cache_store, logger)
    service = new_merchant_business_service(repos, mencache, logger)
    handler = new_merchant_business_handler(service, logger)

    server = grpc.aio.server()
    merchant_business_query_pb2_grpc.add_MerchantBusinessQueryServiceServicer_to_server(
        handler.merchant_business_query, server
    )
    merchant_business_command_pb2_grpc.add_MerchantBusinessCommandServiceServicer_to_server(
        handler.merchant_business_command, server
    )
    port = server.add_insecure_port("127.0.0.1:0")
    await server.start()
    try:
        yield f"127.0.0.1:{port}"
    finally:
        await server.stop(0)
        await channel_merchant.close()


@pytest.fixture
async def merchant_policy_grpc_server(db: Database, cache_store: CacheStore) -> AsyncIterator[str]:
    """Run the real merchant_policy handlers (two servicers) on an ephemeral port."""
    logger = get_logger("test-merchant-policy")
    channel_merchant = grpc.aio.insecure_channel("127.0.0.1:1")
    repos = new_merchant_policy_repositories(
        db, merchant_channel=channel_merchant, guards=MerchantPolicyGuardOptions()
    )
    mencache = new_merchant_policy_mencache(cache_store, logger)
    service = new_merchant_policy_service(repos, mencache, logger)
    handler = new_merchant_policy_handler(service, logger)

    server = grpc.aio.server()
    merchant_policy_query_pb2_grpc.add_MerchantPolicyQueryServiceServicer_to_server(
        handler.merchant_policy_query, server
    )
    merchant_policy_command_pb2_grpc.add_MerchantPolicyCommandServiceServicer_to_server(
        handler.merchant_policy_command, server
    )
    port = server.add_insecure_port("127.0.0.1:0")
    await server.start()
    try:
        yield f"127.0.0.1:{port}"
    finally:
        await server.stop(0)
        await channel_merchant.close()


class _CategoryFindByIdStub(category_query_pb2_grpc.CategoryQueryServiceServicer):
    """Answer `FindById` with a success envelope for any id. Product's command service validates the parent category through the gRPC adapter; the returned row is discarded (existence check only), so a stub suffices — the product FK still requires a real category row seeded by the test."""

    async def FindById(self, request, context):
        response = category_common_pb2.ApiResponseCategory(status="success", message="ok")
        response.data.id = request.id
        response.data.name = "Stub Category"
        return response


class _MerchantFindByIdStub(merchant_query_pb2_grpc.MerchantQueryServiceServicer):
    """Answer `FindById` with a success envelope for any id (see above)."""

    async def FindById(self, request, context):
        response = merchant_common_pb2.ApiResponseMerchant(status="success", message="ok")
        response.data.id = request.id
        response.data.name = "Stub Merchant"
        return response


async def _start_stub(servicer, add_to_server) -> tuple[str, grpc.aio.Server]:
    server = grpc.aio.server()
    add_to_server(servicer, server)
    port = server.add_insecure_port("127.0.0.1:0")
    await server.start()
    return f"127.0.0.1:{port}", server


@pytest.fixture
async def product_grpc_server(db: Database, cache_store: CacheStore) -> AsyncIterator[str]:
    """Run the real product handlers (two servicers) on an ephemeral port. The command service validates the parent category and merchant through the gRPC adapters, so the fixture also stands up two tiny `FindById` stub servers (category + merchant) and wires the real adapters to them. Tests still seed the real merchant/category rows the product FKs require."""
    logger = get_logger("test-product")
    category_addr, category_stub = await _start_stub(
        _CategoryFindByIdStub(),
        category_query_pb2_grpc.add_CategoryQueryServiceServicer_to_server,
    )
    merchant_addr, merchant_stub = await _start_stub(
        _MerchantFindByIdStub(),
        merchant_query_pb2_grpc.add_MerchantQueryServiceServicer_to_server,
    )
    channel_category = grpc.aio.insecure_channel(category_addr)
    channel_merchant = grpc.aio.insecure_channel(merchant_addr)

    repos = new_product_repositories(
        db,
        category_channel=channel_category,
        merchant_channel=channel_merchant,
        guards=ProductGuardOptions(),
    )
    mencache = new_product_mencache(cache_store, logger)
    service = new_product_service(repos, mencache, logger)
    handler = new_product_handler(service, logger)

    server = grpc.aio.server()
    product_query_pb2_grpc.add_ProductQueryServiceServicer_to_server(handler.product_query, server)
    product_command_pb2_grpc.add_ProductCommandServiceServicer_to_server(handler.product_command, server)
    port = server.add_insecure_port("127.0.0.1:0")
    await server.start()
    try:
        yield f"127.0.0.1:{port}"
    finally:
        await server.stop(0)
        await channel_category.close()
        await channel_merchant.close()
        await category_stub.stop(0)
        await merchant_stub.stop(0)


@pytest.fixture
async def cart_grpc_server(
    db: Database,
    cache_store: CacheStore,
    product_grpc_server: str,
    user_grpc_server: str,
) -> AsyncIterator[str]:
    """Run the real cart handlers (two servicers) on an ephemeral port. Cart's command service resolves the product (snapshot fields + stock check) and validates the owner through gRPC adapters, so the fixture points those adapters at the real product and user servers (both spun up by their own fixtures). Tests still seed the real product/user rows the cart FKs require."""
    logger = get_logger("test-cart")
    channel_user = grpc.aio.insecure_channel(user_grpc_server)
    channel_product = grpc.aio.insecure_channel(product_grpc_server)
    repos = new_cart_repositories(
        db,
        user_channel=channel_user,
        product_channel=channel_product,
        guards=CartGuardOptions(),
    )
    mencache = new_cart_mencache(cache_store, logger)
    service = new_cart_service(repos, mencache, logger)
    handler = new_cart_handler(service, logger)

    server = grpc.aio.server()
    cart_query_pb2_grpc.add_CartQueryServiceServicer_to_server(handler.cart_query, server)
    cart_command_pb2_grpc.add_CartCommandServiceServicer_to_server(handler.cart_command, server)
    port = server.add_insecure_port("127.0.0.1:0")
    await server.start()
    try:
        yield f"127.0.0.1:{port}"
    finally:
        await server.stop(0)
        await channel_user.close()
        await channel_product.close()


@pytest.fixture
async def review_grpc_server(
    db: Database,
    cache_store: CacheStore,
    product_grpc_server: str,
    user_grpc_server: str,
) -> AsyncIterator[str]:
    """Run the real review handlers (two servicers) on an ephemeral port. Review's command service validates the author (user) and the reviewed product through gRPC adapters, so the fixture points those adapters at the real product and user servers (both spun up by their own fixtures). Tests still seed the real user/product rows the review FKs require."""
    logger = get_logger("test-review")
    channel_user = grpc.aio.insecure_channel(user_grpc_server)
    channel_product = grpc.aio.insecure_channel(product_grpc_server)
    repos = new_review_repositories(
        db,
        user_channel=channel_user,
        product_channel=channel_product,
        guards=ReviewGuardOptions(),
    )
    mencache = new_review_mencache(cache_store, logger)
    service = new_review_service(repos, mencache, logger)
    handler = new_review_handler(service, logger)

    server = grpc.aio.server()
    review_query_pb2_grpc.add_ReviewQueryServiceServicer_to_server(handler.review_query, server)
    review_command_pb2_grpc.add_ReviewCommandServiceServicer_to_server(handler.review_command, server)
    port = server.add_insecure_port("127.0.0.1:0")
    await server.start()
    try:
        yield f"127.0.0.1:{port}"
    finally:
        await server.stop(0)
        await channel_user.close()
        await channel_product.close()


ADMIN_ROLE_NAME = "ROLE_ADMIN"


@pytest.fixture
def auth_secret() -> str:
    """Secret shared by the test token manager and the auth service fixture."""
    return get_settings().app.secret_key or "integration-test-secret-key-0123456789"


@pytest.fixture
def token_manager(auth_secret: str) -> TokenManager:
    return new_manager(auth_secret)


@pytest.fixture
async def admin_role(db: Database) -> AsyncIterator[int]:
    """Ensure `ROLE_ADMIN` exists for the registration flow. Registration resolves `ROLE_ADMIN` unconditionally. The row is created if missing and removed afterwards *only if this fixture created it*, so a seeded database is left untouched."""
    row = await db.scalar(
        "SELECT role_id FROM roles WHERE role_name = :name",
        {"name": ADMIN_ROLE_NAME},
    )
    created = row is None
    if created:
        await db.execute(
            "INSERT INTO roles (role_name) VALUES (:name) ON CONFLICT (role_name) DO NOTHING",
            {"name": ADMIN_ROLE_NAME},
        )
        row = await db.scalar(
            "SELECT role_id FROM roles WHERE role_name = :name",
            {"name": ADMIN_ROLE_NAME},
        )
    try:
        yield int(row["role_id"])
    finally:
        if created:
            await db.execute(
                "DELETE FROM roles WHERE role_name = :name",
                {"name": ADMIN_ROLE_NAME},
            )


@pytest.fixture
async def auth_grpc_server(
    db: Database,
    cache_store: CacheStore,
    token_manager: TokenManager,
    admin_role: int,
    role_grpc_server: str,
) -> AsyncIterator[str]:
    """Run the real auth handlers on an ephemeral grpc.aio port. Auth resolves roles over gRPC, so this fixture also spins up the role server and points the auth repositories' guarded role adapter at it."""
    logger = get_logger("test-auth")
    channel_role = grpc.aio.insecure_channel(role_grpc_server)
    guards = AuthGuardOptions(
        role=default_guard("role", logger),
        user_role=default_guard("user_role", logger),
    )
    service = new_auth_service(
        new_auth_repositories(db, role_channel=channel_role, guards=guards),
        cache_store,
        token_manager,
        logger,
    )
    handler = new_auth_handler(service, logger)

    server = grpc.aio.server()
    auth_pb2_grpc.add_AuthServiceServicer_to_server(handler.auth, server)
    port = server.add_insecure_port("127.0.0.1:0")
    await server.start()
    try:
        yield f"127.0.0.1:{port}"
    finally:
        await server.stop(0)
        await channel_role.close()


class OrderParents(NamedTuple):
    """FK parents an order-family test needs (see `order_parents`)."""

    user_id: int
    merchant_id: int
    category_id: int
    product_id: int


@pytest.fixture
async def order_parents(db: Database) -> AsyncIterator[OrderParents]:
    """Seed a user + merchant + category + product for order-family tests."""
    suffix = uuid.uuid4().hex[:10]
    user = await db.execute(
        """
        INSERT INTO users (firstname, lastname, email, password, verification_code)
        VALUES ('T', 'O', :email, 'x', 'v')
        RETURNING user_id
        """,
        {"email": f"test_order_parents_{suffix}@example.com"},
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
        {"user_id": user_id, "name": f"Order Merchant {suffix}"},
    )
    assert merchant is not None
    merchant_id = int(merchant["merchant_id"])
    category = await db.execute(
        """
        INSERT INTO categories (name, description, slug_category, image_category)
        VALUES (:name, 'd', :slug, 'img.jpg')
        RETURNING category_id
        """,
        {"name": f"Order Category {suffix}", "slug": f"order-{suffix}"},
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
            :mid, :cid, :name, 'd', 5000, 1000, 'Brand', 100, 4.5, :slug, 'p.jpg'
        )
        RETURNING product_id
        """,
        {
            "mid": merchant_id,
            "cid": category_id,
            "name": f"Order Product {suffix}",
            "slug": f"order-product-{suffix}",
        },
    )
    assert product is not None
    product_id = int(product["product_id"])
    try:
        yield OrderParents(user_id, merchant_id, category_id, product_id)
    finally:
        for table in (
            "order_stock_reservations",
            "order_items",
            "transactions",
            "shipping_addresses",
        ):
            await db.execute(
                f"DELETE FROM {table} WHERE order_id IN "
                "(SELECT order_id FROM orders WHERE user_id = :uid)",
                {"uid": user_id},
            )
        await db.execute("DELETE FROM orders WHERE user_id = :uid", {"uid": user_id})
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


@pytest.fixture
async def order_grpc_server(
    db: Database,
    cache_store: CacheStore,
    user_grpc_server: str,
    product_grpc_server: str,
    order_item_grpc_server: str,
    shipping_address_grpc_server: str,
) -> AsyncIterator[str]:
    """Run the real order handlers (four servicers) on an ephemeral port. The command saga reserves stock, writes the reservation ledger and order items, and creates the shipping address remotely, so the fixture points the product/order_item/shipping adapters at the real servers (each spun up by its own fixture) and the user adapter at the real user server. The merchant and transaction channels are dead wiring, so they point at an unused address. Tests still seed the real parents the FKs require."""
    logger = get_logger("test-order")
    channel_user = grpc.aio.insecure_channel(user_grpc_server)
    channel_product = grpc.aio.insecure_channel(product_grpc_server)
    channel_merchant = grpc.aio.insecure_channel("127.0.0.1:1")
    channel_order_item = grpc.aio.insecure_channel(order_item_grpc_server)
    channel_shipping = grpc.aio.insecure_channel(shipping_address_grpc_server)
    channel_transaction = grpc.aio.insecure_channel("127.0.0.1:1")

    repos = new_order_repositories(
        db,
        user_channel=channel_user,
        merchant_channel=channel_merchant,
        product_channel=channel_product,
        order_item_channel=channel_order_item,
        shipping_channel=channel_shipping,
        transaction_channel=channel_transaction,
        guards=OrderGuardOptions(),
    )
    mencache = new_order_mencache(cache_store, logger)
    service = new_order_service(repos, mencache, logger)
    handler = new_order_handler(service, logger)

    server = grpc.aio.server()
    order_query_pb2_grpc.add_OrderQueryServiceServicer_to_server(
        handler.order_query, server
    )
    order_stats_pb2_grpc.add_OrderStatsServiceServicer_to_server(
        handler.order_stats, server
    )
    order_statsbymerchant_pb2_grpc.add_OrderStatsByMerchantServiceServicer_to_server(
        handler.order_stats, server
    )
    order_command_pb2_grpc.add_OrderCommandServiceServicer_to_server(
        handler.order_command, server
    )
    port = server.add_insecure_port("127.0.0.1:0")
    await server.start()
    try:
        yield f"127.0.0.1:{port}"
    finally:
        await server.stop(0)
        for channel in (
            channel_user,
            channel_product,
            channel_merchant,
            channel_order_item,
            channel_shipping,
            channel_transaction,
        ):
            await channel.close()


@pytest.fixture
async def transaction_grpc_server(
    db: Database,
    cache_store: CacheStore,
    user_grpc_server: str,
    merchant_grpc_server: str,
    order_grpc_server: str,
    order_item_grpc_server: str,
    shipping_address_grpc_server: str,
) -> AsyncIterator[str]:
    """Run the real transaction handlers (four servicers) on an ephemeral port. The create/update saga resolves the order, user, merchant, items and shipping remotely, so the fixture points all five adapters at the real dependency servers (each spun up by its own fixture; the order server transitively starts the product server too)."""
    logger = get_logger("test-transaction")
    channel_user = grpc.aio.insecure_channel(user_grpc_server)
    channel_merchant = grpc.aio.insecure_channel(merchant_grpc_server)
    channel_order = grpc.aio.insecure_channel(order_grpc_server)
    channel_order_item = grpc.aio.insecure_channel(order_item_grpc_server)
    channel_shipping = grpc.aio.insecure_channel(shipping_address_grpc_server)

    repos = new_transaction_repositories(
        db,
        user_channel=channel_user,
        merchant_channel=channel_merchant,
        order_channel=channel_order,
        order_item_channel=channel_order_item,
        shipping_channel=channel_shipping,
        guards=TransactionGuardOptions(),
    )
    mencache = new_transaction_mencache(cache_store, logger)
    service = new_transaction_service(repos, mencache, db, logger)
    handler = new_transaction_handler(service, logger)

    server = grpc.aio.server()
    transaction_query_pb2_grpc.add_TransactionQueryServiceServicer_to_server(
        handler.transaction_query, server
    )
    transaction_stats_pb2_grpc.add_TransactionStatsServiceServicer_to_server(
        handler.transaction_stats, server
    )
    transaction_stats_bymerchant_pb2_grpc.add_TransactionStatsByMerchantServiceServicer_to_server(
        handler.transaction_stats, server
    )
    transaction_command_pb2_grpc.add_TransactionCommandServiceServicer_to_server(
        handler.transaction_command, server
    )
    port = server.add_insecure_port("127.0.0.1:0")
    await server.start()
    try:
        yield f"127.0.0.1:{port}"
    finally:
        await server.stop(0)
        for channel in (
            channel_user,
            channel_merchant,
            channel_order,
            channel_order_item,
            channel_shipping,
        ):
            await channel.close()

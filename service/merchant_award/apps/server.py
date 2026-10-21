"""Merchant award service composition root. merchant_award has no outbox/Kafka surface (the service does not produce events). Note: the merchant adapter is wired but never consumed by a service — the merchant_award service has the same dead wiring (unlike merchant_detail, which validates the parent merchant on create)."""

from __future__ import annotations

import grpc.aio as grpc_aio

from pb.merchant_award import (
    merchant_award_command_pb2_grpc,
    merchant_award_query_pb2_grpc,
)
from pkg.adapter.guard import default_guard
from pkg.config.settings import Settings, get_settings
from pkg.redis.redis import new_redis_client
from pkg.server import GRPCServer
from pkg.server import new_server as new_grpc_server
from pkg.server.config import ServerConfig
from service.merchant_award.handler import new_handler
from service.merchant_award.redis import new_mencache
from service.merchant_award.repository import GuardOptions, new_repositories
from service.merchant_award.service import new_service
from shared.cache import CacheStore

SERVICE_NAME = "merchant_award-service"
SERVICE_PORT = 50065
MERCHANT_AWARD_SERVICE_NAMES = [
    "pb.merchant_award.MerchantAwardQueryService",
    "pb.merchant_award.MerchantAwardCommandService",
]


async def new_server(settings: Settings | None = None) -> GRPCServer:
    resolved = settings or get_settings()
    config = ServerConfig(
        service_name=SERVICE_NAME,
        port=SERVICE_PORT,
        environment=resolved.app.env,
        otel_endpoint=resolved.app.otel_endpoint,
        enable_telemetry=resolved.app.otel_enabled,
        enable_reflection=resolved.app.enable_reflection,
    )

    srv = await new_grpc_server(config, resolved.database)
    assert srv.db is not None

    redis = await new_redis_client(resolved.redis, SERVICE_NAME, srv.logger)
    srv.redis = redis
    cache_store = CacheStore(redis, srv.logger)
    mencache = new_mencache(cache_store, srv.logger)

    # wires a merchant client here even though no service path consumes it.
    channel_merchant = grpc_aio.insecure_channel(resolved.grpc.grpc_merchant_addr)
    srv.add_cleanup_hook(channel_merchant.close)
    guards = GuardOptions(merchant=default_guard("merchant", srv.logger))

    repos = new_repositories(srv.db, merchant_channel=channel_merchant, guards=guards)
    service = new_service(repos, mencache, srv.logger)
    handler = new_handler(service, srv.logger)

    def register(server) -> None:
        merchant_award_query_pb2_grpc.add_MerchantAwardQueryServiceServicer_to_server(
            handler.merchant_award_query, server
        )
        merchant_award_command_pb2_grpc.add_MerchantAwardCommandServiceServicer_to_server(
            handler.merchant_award_command, server
        )

    srv.register_services = register
    srv.reflection_services = list(MERCHANT_AWARD_SERVICE_NAMES)
    return srv


__all__ = [
    "MERCHANT_AWARD_SERVICE_NAMES",
    "SERVICE_NAME",
    "SERVICE_PORT",
    "new_server",
]

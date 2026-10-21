"""Merchant service composition root. Kafka being unavailable is logged and non-fatal: the gRPC surface still serves, the relay is not started, the transaction consumer is not registered, and the merchant command service simply skips the direct status-event publish."""

from __future__ import annotations

import asyncio

import grpc.aio as grpc_aio

from pb.merchant import merchant_command_pb2_grpc, merchant_query_pb2_grpc
from pb.merchant_document import (
    merchant_document_command_pb2_grpc,
    merchant_document_query_pb2_grpc,
)
from pkg.adapter.guard import default_guard
from pkg.config.settings import Settings, get_settings
from pkg.kafka.kafka import Kafka
from pkg.outbox import OutboxRelay
from pkg.redis.redis import new_redis_client
from pkg.server import GRPCServer
from pkg.server import new_server as new_grpc_server
from pkg.server.config import ServerConfig
from service.merchant.handler import new_handler
from service.merchant.kafka import (
    CONSUMER_GROUP,
    TRANSACTION_TOPIC,
    MerchantTransactionConsumer,
)
from service.merchant.redis import new_mencache
from service.merchant.repository import GuardOptions, new_repositories
from service.merchant.service import new_service
from shared.cache import CacheStore

SERVICE_NAME = "merchant-service"
SERVICE_PORT = 50055
MERCHANT_SERVICE_NAMES = [
    "pb.merchant.MerchantQueryService",
    "pb.merchant.MerchantCommandService",
    "pb.merchant_document.MerchantDocumentQueryService",
    "pb.merchant_document.MerchantDocumentCommandService",
]

_RELAY_SHUTDOWN_TIMEOUT = 5.0


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

    # The user service owns the users table; merchant resolves owners over gRPC
    # through the shared user adapter. The dependency gets its own circuit
    # breaker + bulkhead + per-call deadline.
    channel_user = grpc_aio.insecure_channel(resolved.grpc.grpc_user_addr)
    srv.add_cleanup_hook(channel_user.close)
    guards = GuardOptions(user=default_guard("user", srv.logger))

    repos = new_repositories(srv.db, user_channel=channel_user, guards=guards)

    kafka_client = Kafka(srv.logger, resolved.kafka.broker_list)
    kafka: Kafka | None = kafka_client
    try:
        await kafka_client.start()
    except Exception as exc:
        srv.logger.error(
            "kafka producer start failed; outbox relay and consumer disabled",
            error=str(exc),
        )
        kafka = None
    else:
        srv.add_cleanup_hook(kafka_client.close)

        relay = OutboxRelay(srv.db, kafka_client, srv.logger)
        relay_stop = asyncio.Event()
        relay_task = asyncio.create_task(relay.run(relay_stop))

        async def stop_relay() -> None:
            relay_stop.set()
            try:
                await asyncio.wait_for(relay_task, timeout=_RELAY_SHUTDOWN_TIMEOUT)
            except (TimeoutError, asyncio.CancelledError):
                relay_task.cancel()

        srv.add_cleanup_hook(stop_relay)

        consumer = MerchantTransactionConsumer(mencache.merchant_command, srv.logger)
        try:
            await kafka_client.start_consumers(
                [TRANSACTION_TOPIC],
                CONSUMER_GROUP,
                consumer.handle,
                manual_commit=False,
            )
        except Exception as exc:
            srv.logger.error(
                "merchant transaction consumer start failed; continuing without it",
                error=str(exc),
            )

    service = new_service(repos, mencache, srv.db, kafka, srv.logger)
    handler = new_handler(service, srv.logger)

    def register(server) -> None:
        merchant_query_pb2_grpc.add_MerchantQueryServiceServicer_to_server(
            handler.merchant_query, server
        )
        merchant_command_pb2_grpc.add_MerchantCommandServiceServicer_to_server(
            handler.merchant_command, server
        )
        merchant_document_query_pb2_grpc.add_MerchantDocumentQueryServiceServicer_to_server(
            handler.merchant_document_query, server
        )
        merchant_document_command_pb2_grpc.add_MerchantDocumentCommandServiceServicer_to_server(
            handler.merchant_document_command, server
        )

    srv.register_services = register
    srv.reflection_services = list(MERCHANT_SERVICE_NAMES)
    return srv


__all__ = [
    "MERCHANT_SERVICE_NAMES",
    "SERVICE_NAME",
    "SERVICE_PORT",
    "new_server",
]

"""Transaction service composition root. Kafka being unavailable is logged and non-fatal: the gRPC surface still serves, the relay is not started, and the merchant-status consumer is not registered (merchant precedent). The `Create` flow itself never talks to Kafka directly — it only writes outbox rows, which the relay publishes."""

from __future__ import annotations

import asyncio

import grpc.aio as grpc_aio

from pb.transaction import (
    transaction_command_pb2_grpc,
    transaction_query_pb2_grpc,
)
from pb.transaction.stats import (
    transaction_stats_bymerchant_pb2_grpc,
    transaction_stats_pb2_grpc,
)
from pkg.adapter.guard import default_guard
from pkg.config.settings import Settings, get_settings
from pkg.kafka.kafka import Kafka
from pkg.outbox import OutboxRelay
from pkg.redis.redis import new_redis_client
from pkg.server import GRPCServer
from pkg.server import new_server as new_grpc_server
from pkg.server.config import ServerConfig
from service.transaction.handler import new_handler
from service.transaction.kafka import (
    CONSUMER_GROUP,
    MERCHANT_STATUS_TOPIC,
    MerchantStatusConsumer,
)
from service.transaction.redis import new_mencache
from service.transaction.repository import GuardOptions, new_repositories
from service.transaction.service import new_service
from shared.cache import CacheStore

SERVICE_NAME = "transaction-service"
SERVICE_PORT = 50059
TRANSACTION_SERVICE_NAMES = [
    "pb.transaction.TransactionQueryService",
    "pb.transaction.TransactionCommandService",
    "pb.transaction.stats.TransactionStatsService",
    "pb.transaction.stats.TransactionStatsByMerchantService",
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

    channel_user = grpc_aio.insecure_channel(resolved.grpc.grpc_user_addr)
    channel_merchant = grpc_aio.insecure_channel(resolved.grpc.grpc_merchant_addr)
    channel_order = grpc_aio.insecure_channel(resolved.grpc.grpc_order_addr)
    channel_order_item = grpc_aio.insecure_channel(
        resolved.grpc.grpc_order_item_addr
    )
    channel_shipping = grpc_aio.insecure_channel(
        resolved.grpc.grpc_shipping_address_addr
    )
    for channel in (
        channel_user,
        channel_merchant,
        channel_order,
        channel_order_item,
        channel_shipping,
    ):
        srv.add_cleanup_hook(channel.close)

    guards = GuardOptions(
        user=default_guard("user", srv.logger),
        merchant=default_guard("merchant", srv.logger),
        order=default_guard("order", srv.logger),
        order_item=default_guard("order_item", srv.logger),
        shipping=default_guard("shipping", srv.logger),
    )

    repos = new_repositories(
        srv.db,
        user_channel=channel_user,
        merchant_channel=channel_merchant,
        order_channel=channel_order,
        order_item_channel=channel_order_item,
        shipping_channel=channel_shipping,
        guards=guards,
    )

    kafka_client = Kafka(srv.logger, resolved.kafka.broker_list)
    try:
        await kafka_client.start()
    except Exception as exc:
        srv.logger.error(
            "kafka producer start failed; outbox relay and consumer disabled",
            error=str(exc),
        )
    else:
        srv.add_cleanup_hook(kafka_client.close)

        relay = OutboxRelay(srv.db, kafka_client, srv.logger)
        relay_stop = asyncio.Event()
        relay_task = asyncio.create_task(relay.run(relay_stop))

        async def stop_relay() -> None:
            relay_stop.set()
            try:
                await asyncio.wait_for(
                    relay_task, timeout=_RELAY_SHUTDOWN_TIMEOUT
                )
            except (TimeoutError, asyncio.CancelledError):
                relay_task.cancel()

        srv.add_cleanup_hook(stop_relay)

        consumer = MerchantStatusConsumer(
            mencache.transaction_command, srv.logger
        )
        try:
            await kafka_client.start_consumers(
                [MERCHANT_STATUS_TOPIC],
                CONSUMER_GROUP,
                consumer.handle,
                manual_commit=False,
            )
        except Exception as exc:
            srv.logger.error(
                "merchant status consumer start failed; continuing without it",
                error=str(exc),
            )

    service = new_service(repos, mencache, srv.db, srv.logger)
    handler = new_handler(service, srv.logger)

    def register(server) -> None:
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

    srv.register_services = register
    srv.reflection_services = list(TRANSACTION_SERVICE_NAMES)
    return srv


__all__ = [
    "SERVICE_NAME",
    "SERVICE_PORT",
    "TRANSACTION_SERVICE_NAMES",
    "new_server",
]

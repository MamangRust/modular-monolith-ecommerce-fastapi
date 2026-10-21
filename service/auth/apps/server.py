"""Auth service composition root. Kafka being unavailable is logged and non-fatal (the gRPC surface still serves), but the relay is only started once Kafka is up because it has nothing to publish without it."""

from __future__ import annotations

import asyncio

import grpc.aio as grpc_aio

from pb.auth import auth_pb2_grpc
from pkg.adapter.guard import default_guard
from pkg.auth import new_manager
from pkg.config.settings import Settings, get_settings
from pkg.kafka.kafka import Kafka
from pkg.outbox import OutboxRelay
from pkg.redis.redis import new_redis_client
from pkg.server import GRPCServer
from pkg.server import new_server as new_grpc_server
from pkg.server.config import ServerConfig
from service.auth.handler import new_handler
from service.auth.repository import GuardOptions, new_repositories
from service.auth.service import new_service
from shared.cache import CacheStore

SERVICE_NAME = "auth-service"
SERVICE_PORT = 50051
AUTH_SERVICE_NAMES = ["pb.AuthService"]

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

    token_manager = new_manager(resolved.app.require_secret_key(SERVICE_NAME))

    redis = await new_redis_client(resolved.redis, SERVICE_NAME, srv.logger)
    srv.redis = redis
    cache_store = CacheStore(redis, srv.logger)

    # gRPC client to the role service: the role service owns the roles and
    # user_roles tables, so auth reaches them through the shared role adapters
    # instead of reading/writing those tables directly. Each dependency gets
    # its own circuit breaker + bulkhead + per-call deadline.
    channel_role = grpc_aio.insecure_channel(resolved.grpc.grpc_role_addr)
    srv.add_cleanup_hook(channel_role.close)

    guards = GuardOptions(
        role=default_guard("role", srv.logger),
        user_role=default_guard("user_role", srv.logger),
    )

    repos = new_repositories(srv.db, role_channel=channel_role, guards=guards)
    service = new_service(repos, cache_store, token_manager, srv.logger)
    handler = new_handler(service, srv.logger)

    kafka = Kafka(srv.logger, resolved.kafka.broker_list)
    try:
        await kafka.start()
    except Exception as exc:
        srv.logger.error(
            "kafka producer start failed; outbox relay disabled", error=str(exc)
        )
    else:
        srv.add_cleanup_hook(kafka.close)
        relay = OutboxRelay(srv.db, kafka, srv.logger)
        relay_stop = asyncio.Event()
        relay_task = asyncio.create_task(relay.run(relay_stop))

        async def stop_relay() -> None:
            relay_stop.set()
            try:
                await asyncio.wait_for(relay_task, timeout=_RELAY_SHUTDOWN_TIMEOUT)
            except (TimeoutError, asyncio.CancelledError):
                relay_task.cancel()

        srv.add_cleanup_hook(stop_relay)

    def register(server) -> None:
        auth_pb2_grpc.add_AuthServiceServicer_to_server(handler.auth, server)

    srv.register_services = register
    srv.reflection_services = list(AUTH_SERVICE_NAMES)
    return srv


__all__ = ["AUTH_SERVICE_NAMES", "SERVICE_NAME", "SERVICE_PORT", "new_server"]

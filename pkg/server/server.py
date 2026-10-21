"""gRPC service bootstrap.

`GRPCServer` owns the shared resources of one domain process:
logger, database pool, redis, cache store, telemetry, and optional
consumer/relay lifecycle. Domain services build repositories, services,
and handlers, then register their gRPC servicers on the returned server.

Health and reflection Matches the expected server: the standard health service
is always registered and reports SERVING until shutdown, while
reflection is opt-in for development only."""

from __future__ import annotations

import asyncio
from collections.abc import Awaitable, Callable
from typing import Any

import grpc
from grpc_health.v1 import health, health_pb2, health_pb2_grpc
from grpc_reflection.v1alpha import reflection

from pkg.database.database import Database
from pkg.logger.logger import Logger, get_logger
from pkg.otel.otel import Telemetry, TelemetryConfig
from pkg.redis.redis import close_redis
from pkg.server.config import (
    DEFAULT_KEEPALIVE_TIME,
    DEFAULT_KEEPALIVE_TIMEOUT,
    DEFAULT_MAX_CONCURRENT_STREAMS,
    SHUTDOWN_TIMEOUT,
    ServerConfig,
)

CleanupHook = Callable[[], Awaitable[None]]

_GRPC_OPTIONS = [
    ("grpc.max_concurrent_streams", DEFAULT_MAX_CONCURRENT_STREAMS),
    ("grpc.keepalive_time_ms", int(DEFAULT_KEEPALIVE_TIME * 1000)),
    ("grpc.keepalive_timeout_ms", int(DEFAULT_KEEPALIVE_TIMEOUT * 1000)),
    ("grpc.keepalive_permit_without_calls", 1),
]


class GRPCServer:
    """Holds shared per-process resources and hosts a grpc.aio server."""

    def __init__(self, config: ServerConfig, logger: Logger) -> None:
        self.config = config
        self.logger = logger
        self.db: Database | None = None
        self.redis: Any = None
        self.telemetry: Telemetry | None = None
        self.health_servicer: health.aio.HealthServicer | None = None
        self.reflection_services: list[str] = []
        self._cleanup_hooks: list[CleanupHook] = []
        self._register_services: Callable[[Any], None] | None = None
        self._stop = asyncio.Event()

    def add_cleanup_hook(self, hook: CleanupHook) -> None:
        if hook is not None:
            self._cleanup_hooks.append(hook)

    @property
    def register_services(self) -> Callable[[Any], None] | None:
        return self._register_services

    @register_services.setter
    def register_services(self, fn: Callable[[Any], None] | None) -> None:
        self._register_services = fn

    def stop(self) -> None:
        self._stop.set()


async def new_server(config: ServerConfig, db_settings: Any) -> GRPCServer:
    """Initialize shared resources."""
    logger = get_logger(config.service_name)
    logger.info("initializing service", service=config.service_name)

    telemetry = Telemetry(
        TelemetryConfig(
            service_name=config.service_name,
            environment=config.environment,
            endpoint=config.otel_endpoint,
            insecure=True,
            enabled=config.enable_telemetry,
        ),
        logger,
    )
    telemetry.init()

    db = Database.create(db_settings, logger)
    srv = GRPCServer(config, logger)
    srv.telemetry = telemetry
    srv.db = db
    try:
        await db.ping()
    except Exception as exc:
        logger.error("failed to connect to database", error=str(exc))
        raise

    return srv


async def start(srv: GRPCServer) -> grpc.aio.Server:
    """Start the grpc.aio server, register health, servicers and reflection."""
    if srv.telemetry is not None:
        srv.telemetry.instrument_grpc_server()
    server = grpc.aio.server(options=_GRPC_OPTIONS)

    health_servicer = health.aio.HealthServicer()
    health_pb2_grpc.add_HealthServicer_to_server(health_servicer, server)
    srv.health_servicer = health_servicer

    if srv.register_services is not None:
        srv.register_services(server)

    server.add_insecure_port(f"[::]:{srv.config.port}")

    if srv.config.enable_reflection:
        names = [health.SERVICE_NAME, *srv.reflection_services]
        reflection.enable_server_reflection(names, server)
        srv.logger.info("grpc reflection enabled", services=names)

    await server.start()

    await health_servicer.set("", health_pb2.HealthCheckResponse.SERVING)
    for service_name in srv.reflection_services:
        await health_servicer.set(service_name, health_pb2.HealthCheckResponse.SERVING)

    srv.logger.info("grpc server started", port=srv.config.port)
    return server


async def serve(srv: GRPCServer, stop_event: asyncio.Event | None = None) -> None:
    """Full lifecycle: resources -> run -> graceful cleanup."""
    server = await start(srv)
    event = stop_event or srv._stop
    await event.wait()
    if srv.health_servicer is not None:
        await srv.health_servicer.enter_graceful_shutdown()
    await server.stop(grace=SHUTDOWN_TIMEOUT)


async def cleanup(srv: GRPCServer) -> None:
    srv.logger.info("cleaning up resources")
    for hook in reversed(srv._cleanup_hooks):
        try:
            await hook()
        except Exception as exc:
            srv.logger.error("failed to close application resource", error=str(exc))
    if srv.db is not None:
        await srv.db.close()
    if srv.redis is not None:
        await close_redis(srv.redis, srv.logger)
    if srv.telemetry is not None:
        await srv.telemetry.shutdown()
    srv.logger.info("cleanup completed")


__all__ = ["GRPCServer", "cleanup", "new_server", "serve", "start"]

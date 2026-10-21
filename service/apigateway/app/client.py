"""Managed gRPC channels for the gateway. One shared channel per domain is created at startup and reused by every handler. Every channel carries the per-method DependencyGuardInterceptor, so all outbound RPCs get a circuit breaker + bulkhead keyed by the downstream method — one failing domain cannot exhaust the gateway or open the circuits of the others. Readiness performs a real health check against each channel so the gateway never reports ready while a domain it routes to is down."""

from __future__ import annotations

import asyncio
from dataclasses import dataclass, field

import grpc
from grpc_health.v1 import health_pb2, health_pb2_grpc

from pkg.config.settings import GrpcSettings
from pkg.logger.logger import Logger
from pkg.resilience.client_interceptor import DependencyGuardInterceptor

# The 19 ecommerce downstreams, in the gateway's order
# merchant_document is served by the
# merchant service; merchant_social_link's command servicer lives on
# merchant_detail — handlers reach both through the entries below when their
# stages land.
DOMAINS: tuple[str, ...] = (
    "auth",
    "role",
    "user",
    "category",
    "merchant",
    "order_item",
    "order",
    "product",
    "transaction",
    "cart",
    "review",
    "slider",
    "shipping_address",
    "banner",
    "merchant_award",
    "merchant_business",
    "merchant_detail",
    "merchant_policy",
    "review_detail",
)

READINESS_TIMEOUT = 1.0

_CHANNEL_OPTIONS = [
    ("grpc.max_send_message_length", 16 * 1024 * 1024),
    ("grpc.max_receive_message_length", 16 * 1024 * 1024),
    ("grpc.keepalive_time_ms", 20_000),
    ("grpc.keepalive_timeout_ms", 5_000),
    ("grpc.keepalive_permit_without_calls", 1),
    ("grpc.initial_reconnect_backoff_ms", 1_000),
]


@dataclass
class ServiceConnections:
    channels: dict[str, grpc.aio.Channel] = field(default_factory=dict)
    addresses: dict[str, str] = field(default_factory=dict)

    def channel(self, domain: str) -> grpc.aio.Channel:
        try:
            return self.channels[domain]
        except KeyError as exc:
            raise KeyError(f"no gRPC channel configured for domain {domain!r}") from exc

    def get(self, domain: str) -> grpc.aio.Channel | None:
        return self.channels.get(domain)

    async def close(self) -> None:
        for channel in self.channels.values():
            await channel.close()
        self.channels.clear()

    async def check_readiness(self) -> dict[str, bool]:
        results: dict[str, bool] = {}
        for domain, channel in self.channels.items():
            results[domain] = await _check_channel(channel)
        return results


async def _check_channel(channel: grpc.aio.Channel) -> bool:
    stub = health_pb2_grpc.HealthStub(channel)
    try:
        response = await asyncio.wait_for(
            stub.Check(health_pb2.HealthCheckRequest(service="")),
            timeout=READINESS_TIMEOUT,
        )
    except Exception:
        return False
    return response.status == health_pb2.HealthCheckResponse.SERVING


async def connect(settings: GrpcSettings, logger: Logger) -> ServiceConnections:
    connections = ServiceConnections()
    interceptor = DependencyGuardInterceptor(logger)
    for domain in DOMAINS:
        address = getattr(settings, f"grpc_{domain}_addr")
        connections.channels[domain] = grpc.aio.insecure_channel(
            address, options=_CHANNEL_OPTIONS, interceptors=[interceptor]
        )
        connections.addresses[domain] = address
    logger.info("grpc channels created", addresses=connections.addresses)
    return connections


__all__ = ["DOMAINS", "ServiceConnections", "connect"]

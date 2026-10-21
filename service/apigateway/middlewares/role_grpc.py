"""Direct-gRPC role validation. Replaces the legacy Kafka request/reply `RoleValidator` (inherited from the payment-gateway port): the ecommerce gateway validates roles synchronously with `RoleQueryService.FindByUserId` (5s timeout) and stores the role names in the request context, so `require_roles` can decide 403. the comment records why: the Kafka round-trip did not work in local stacks and every admin route timed out with 408."""

from __future__ import annotations

from typing import Any

import grpc

from pkg.logger.logger import Logger
from service.apigateway.redis.role import RoleCache
from shared.errors import new_internal_error, new_unauthorized_error

RPC_TIMEOUT = 5.0


class RoleValidatorGRPC:
    def __init__(
        self, channel: grpc.aio.Channel, cache: RoleCache, logger: Logger
    ) -> None:
        from pb.role import role_query_pb2_grpc

        self._query = role_query_pb2_grpc.RoleQueryServiceStub(channel)
        self._cache = cache
        self._logger = logger

    async def validate(self, user_id: int) -> list[str]:
        cached = await self._cache.get_user_roles(user_id)
        if cached:
            return cached

        from pb.role import role_query_pb2

        request = role_query_pb2.FindByIdUserRoleRequest(user_id=user_id)
        try:
            response: Any = await self._query.FindByUserId(
                request, timeout=RPC_TIMEOUT
            )
        except grpc.aio.AioRpcError as exc:
            self._logger.error(
                "Role validation via gRPC failed",
                user_id=user_id,
                error=str(exc),
            )
            raise new_internal_error().with_message(
                "Role validation failed"
            ) from exc

        roles = [str(rg.name) for rg in response.data]
        if not roles:
            self._logger.debug("Role validation failed (no roles)", user_id=user_id)
            raise new_unauthorized_error("Role validation failed")

        await self._cache.set_user_roles(user_id, roles)
        return roles


__all__ = ["RoleValidatorGRPC"]

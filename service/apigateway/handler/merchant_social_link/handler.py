"""Gateway merchant_social_link handler: REST <-> merchant_detail gRPC. The social-link command servicer is hosted by the **merchant_detail** service (`pb.merchant_social_link.MerchantSocialCommandService`), so this handler rides the `merchant_detail` channel. `ServiceConnections.MerchantSocial` is never assigned (a leftover defect in the gateway), and its `merchant_social_link` handler is registered against `deps.Client`, which is the merchant_detail connection — reproduces that wiring. There is no query surface: registers only the command routes, because a query social-link RPC does not exist."""

from __future__ import annotations

import grpc

from pb.merchant_social_link import (
    merchant_social_link_command_pb2,
    merchant_social_link_command_pb2_grpc,
)
from service.apigateway.app.client import ServiceConnections
from shared.errors import new_bad_request_error, parse_grpc_error
from shared.mapper.merchant_social_link import to_api_response_merchant_social_link

RPC_TIMEOUT = 30.0


class MerchantSocialLinkHandler:
    def __init__(self, connections: ServiceConnections) -> None:
        channel = connections.channel("merchant_detail")
        self._command = (
            merchant_social_link_command_pb2_grpc.MerchantSocialCommandServiceStub(
                channel
            )
        )

    async def create(self, merchant_detail_id: int, platform: str, url: str):
        request = merchant_social_link_command_pb2.CreateMerchantSocialRequest(
            merchant_detail_id=merchant_detail_id,
            platform=platform,
            url=url,
        )
        try:
            response = await self._command.Create(request, timeout=RPC_TIMEOUT)
        except grpc.aio.AioRpcError as exc:
            raise parse_grpc_error(exc) from exc
        return to_api_response_merchant_social_link(response)

    async def update(self, social_id: int, merchant_detail_id: int, platform: str, url: str):
        # guards `id <= 0` on this route too (message "Invalid ID").
        if social_id <= 0:
            raise new_bad_request_error("Invalid ID")
        request = merchant_social_link_command_pb2.UpdateMerchantSocialRequest(
            id=social_id,
            merchant_detail_id=merchant_detail_id,
            platform=platform,
            url=url,
        )
        try:
            response = await self._command.Update(request, timeout=RPC_TIMEOUT)
        except grpc.aio.AioRpcError as exc:
            raise parse_grpc_error(exc) from exc
        return to_api_response_merchant_social_link(response)


__all__ = ["MerchantSocialLinkHandler"]

"""merchant_social_link command gRPC handler. Only `Create`/`Update` exist (the proto surface is command-only — note #5). The handler borrows merchant_detail's gRPC sentinels for its guards and validation failures,."""

from __future__ import annotations

from typing import Any

from pydantic import ValidationError

from pb.merchant_social_link import (
    merchant_social_link_command_pb2_grpc,
    merchant_social_link_common_pb2,
)
from pkg.logger.logger import Logger
from pkg.middleware import grpc_method
from service.merchant_detail.handler.mapping import (
    fill_merchant_social_link_response,
)
from service.merchant_detail.service.interfaces import (
    MerchantSocialLinkCommandService,
)
from service.merchant_detail.service.service import SERVICE_NAME
from shared.domain.requests.merchant_detail import (
    CreateMerchantSocialRequest,
    UpdateMerchantSocialRequest,
)
from shared.errors.merchant_detail_errors import (
    err_grpc_invalid_merchant_detail_id,
    err_grpc_validate_create_merchant_detail,
    err_grpc_validate_update_merchant_detail,
)


class MerchantSocialLinkCommandHandler(
    merchant_social_link_command_pb2_grpc.MerchantSocialCommandServiceServicer
):
    def __init__(
        self, service: MerchantSocialLinkCommandService, logger: Logger
    ) -> None:
        self._service = service
        self.logger = logger

    @grpc_method("MerchantSocialCommandService.Create", SERVICE_NAME)
    async def Create(self, request: Any, context: Any) -> Any:
        try:
            create_request = CreateMerchantSocialRequest(
                merchant_detail_id=request.merchant_detail_id,
                platform=request.platform,
                url=request.url,
            )
        except ValidationError as exc:
            raise err_grpc_validate_create_merchant_detail from exc
        link = await self._service.create(create_request)
        response = merchant_social_link_common_pb2.ApiResponseMerchantSocial(
            status="success", message="Successfully created merchant social link"
        )
        fill_merchant_social_link_response(response.data, link)
        return response

    @grpc_method("MerchantSocialCommandService.Update", SERVICE_NAME)
    async def Update(self, request: Any, context: Any) -> Any:
        if request.id == 0:
            raise err_grpc_invalid_merchant_detail_id
        try:
            update_request = UpdateMerchantSocialRequest(
                id=request.id,
                merchant_detail_id=request.merchant_detail_id,
                platform=request.platform,
                url=request.url,
            )
        except ValidationError as exc:
            raise err_grpc_validate_update_merchant_detail from exc
        link = await self._service.update(update_request)
        response = merchant_social_link_common_pb2.ApiResponseMerchantSocial(
            status="success", message="Successfully updated merchant social link"
        )
        fill_merchant_social_link_response(response.data, link)
        return response


__all__ = ["MerchantSocialLinkCommandHandler"]

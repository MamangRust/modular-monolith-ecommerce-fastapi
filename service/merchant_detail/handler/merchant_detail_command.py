"""merchant_detail command gRPC handler. Id-carrying commands guard `id == 0` with `err_grpc_invalid_merchant_detail_id` (400). `Create`/`Update` validate the request body; a validation failure raises the matching sentinel. `DeleteMerchantDetailPermanent` / `RestoreAll` / `DeleteAll` reuse the merchant response envelopes (`pb.merchant.ApiResponseMerchantDelete`/`All`),."""

from __future__ import annotations

from typing import Any

from pydantic import ValidationError

from pb.merchant import merchant_common_pb2
from pb.merchant_detail import (
    merchant_detail_command_pb2_grpc,
    merchant_detail_common_pb2,
)
from pkg.logger.logger import Logger
from pkg.middleware import grpc_method
from service.merchant_detail.handler.mapping import (
    fill_merchant_detail_response,
    fill_merchant_detail_response_delete_at,
)
from service.merchant_detail.service.interfaces import (
    MerchantDetailCommandService,
)
from service.merchant_detail.service.service import SERVICE_NAME
from shared.domain.requests.merchant_detail import (
    CreateMerchantDetailRequest,
    UpdateMerchantDetailRequest,
)
from shared.errors.merchant_detail_errors import (
    err_grpc_invalid_merchant_detail_id,
    err_grpc_validate_create_merchant_detail,
    err_grpc_validate_update_merchant_detail,
)


class MerchantDetailCommandHandler(
    merchant_detail_command_pb2_grpc.MerchantDetailCommandServiceServicer
):
    def __init__(
        self, service: MerchantDetailCommandService, logger: Logger
    ) -> None:
        self._service = service
        self.logger = logger

    @grpc_method("MerchantDetailCommandService.Create", SERVICE_NAME)
    async def Create(self, request: Any, context: Any) -> Any:
        try:
            create_request = CreateMerchantDetailRequest(
                merchant_id=request.merchant_id,
                display_name=request.display_name,
                cover_image_url=request.cover_image_url,
                logo_url=request.logo_url,
                short_description=request.short_description,
                website_url=request.website_url,
            )
        except ValidationError as exc:
            raise err_grpc_validate_create_merchant_detail from exc
        detail = await self._service.create(create_request)
        response = merchant_detail_common_pb2.ApiResponseMerchantDetail(
            status="success", message="Successfully created merchant detail"
        )
        fill_merchant_detail_response(response.data, detail)
        return response

    @grpc_method("MerchantDetailCommandService.Update", SERVICE_NAME)
    async def Update(self, request: Any, context: Any) -> Any:
        if request.merchant_detail_id == 0:
            raise err_grpc_invalid_merchant_detail_id
        try:
            update_request = UpdateMerchantDetailRequest(
                merchant_detail_id=request.merchant_detail_id,
                display_name=request.display_name,
                cover_image_url=request.cover_image_url,
                logo_url=request.logo_url,
                short_description=request.short_description,
                website_url=request.website_url,
            )
        except ValidationError as exc:
            raise err_grpc_validate_update_merchant_detail from exc
        detail = await self._service.update(update_request)
        response = merchant_detail_common_pb2.ApiResponseMerchantDetail(
            status="success", message="Successfully updated merchant detail"
        )
        fill_merchant_detail_response(response.data, detail)
        return response

    @grpc_method("MerchantDetailCommandService.TrashedMerchantDetail", SERVICE_NAME)
    async def TrashedMerchantDetail(self, request: Any, context: Any) -> Any:
        if request.id == 0:
            raise err_grpc_invalid_merchant_detail_id
        detail = await self._service.trash(request.id)
        response = merchant_detail_common_pb2.ApiResponseMerchantDetailDeleteAt(
            status="success", message="Successfully trashed merchant detail"
        )
        fill_merchant_detail_response_delete_at(response.data, detail)
        return response

    @grpc_method("MerchantDetailCommandService.RestoreMerchantDetail", SERVICE_NAME)
    async def RestoreMerchantDetail(self, request: Any, context: Any) -> Any:
        if request.id == 0:
            raise err_grpc_invalid_merchant_detail_id
        detail = await self._service.restore(request.id)
        response = merchant_detail_common_pb2.ApiResponseMerchantDetailDeleteAt(
            status="success", message="Successfully restored merchant detail"
        )
        fill_merchant_detail_response_delete_at(response.data, detail)
        return response

    @grpc_method(
        "MerchantDetailCommandService.DeleteMerchantDetailPermanent", SERVICE_NAME
    )
    async def DeleteMerchantDetailPermanent(
        self, request: Any, context: Any
    ) -> Any:
        if request.id == 0:
            raise err_grpc_invalid_merchant_detail_id
        await self._service.delete_permanent(request.id)
        return merchant_common_pb2.ApiResponseMerchantDelete(
            status="success",
            message="Successfully deleted merchant detail permanently",
        )

    @grpc_method(
        "MerchantDetailCommandService.RestoreAllMerchantDetail", SERVICE_NAME
    )
    async def RestoreAllMerchantDetail(self, request: Any, context: Any) -> Any:
        await self._service.restore_all()
        return merchant_common_pb2.ApiResponseMerchantAll(
            status="success",
            message="Successfully restored all merchant details",
        )

    @grpc_method(
        "MerchantDetailCommandService.DeleteAllMerchantDetailPermanent",
        SERVICE_NAME,
    )
    async def DeleteAllMerchantDetailPermanent(
        self, request: Any, context: Any
    ) -> Any:
        await self._service.delete_all()
        return merchant_common_pb2.ApiResponseMerchantAll(
            status="success",
            message="Successfully deleted all merchant details permanently",
        )


__all__ = ["MerchantDetailCommandHandler"]

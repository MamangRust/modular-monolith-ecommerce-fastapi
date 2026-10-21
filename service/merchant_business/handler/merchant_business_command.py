"""merchant_business command gRPC handler. `Create`/`Update` validate the request body; a validation failure raises the matching sentinel. `Trash`/`Restore`/`DeletePermanent` guard `id == 0` with `err_grpc_invalid_merchant_business_id` (400 "Invalid merchant business ID"). `Update` deliberately does NOT guard `id == 0` (satisfies the `required` tag even for 0, so the repository answers 404) — note (same as merchant_award #88). `DeleteMerchantBusinessPermanent` / `RestoreAllMerchantBusiness` / `DeleteAllMerchantBusinessPermanent` reuse the merchant response envelopes (`pb.merchant.ApiResponseMerchantDelete`/`All`),."""

from __future__ import annotations

from typing import Any

from pydantic import ValidationError

from pb.merchant import merchant_common_pb2
from pb.merchant_business import (
    merchant_business_command_pb2_grpc,
    merchant_business_common_pb2,
)
from pkg.logger.logger import Logger
from pkg.middleware import grpc_method
from service.merchant_business.handler.mapping import (
    fill_merchant_business_response,
    fill_merchant_business_response_delete_at,
)
from service.merchant_business.service.interfaces import (
    MerchantBusinessCommandService,
)
from service.merchant_business.service.service import SERVICE_NAME
from shared.domain.requests.merchant_business import (
    CreateMerchantBusinessInformationRequest,
    UpdateMerchantBusinessInformationRequest,
)
from shared.errors import (
    err_grpc_invalid_merchant_business_id,
    err_grpc_validate_create_merchant_business,
    err_grpc_validate_update_merchant_business,
)


class MerchantBusinessCommandHandler(
    merchant_business_command_pb2_grpc.MerchantBusinessCommandServiceServicer
):
    def __init__(
        self, service: MerchantBusinessCommandService, logger: Logger
    ) -> None:
        self._service = service
        self.logger = logger

    @grpc_method("MerchantBusinessCommandService.Create", SERVICE_NAME)
    async def Create(self, request: Any, context: Any) -> Any:
        try:
            create_request = CreateMerchantBusinessInformationRequest(
                merchant_id=request.merchant_id,
                business_type=request.business_type,
                tax_id=request.tax_id,
                established_year=request.established_year,
                number_of_employees=request.number_of_employees,
                website_url=request.website_url,
            )
        except ValidationError as exc:
            raise err_grpc_validate_create_merchant_business from exc
        business = await self._service.create(create_request)
        response = merchant_business_common_pb2.ApiResponseMerchantBusiness(
            status="success", message="Successfully created merchant business"
        )
        fill_merchant_business_response(response.data, business)
        return response

    @grpc_method("MerchantBusinessCommandService.Update", SERVICE_NAME)
    async def Update(self, request: Any, context: Any) -> Any:
        # No `id == 0` guard here — pointer `required` passes for 0 (see
        # module docstring); the repository then answers 404.
        try:
            update_request = UpdateMerchantBusinessInformationRequest(
                merchant_business_info_id=request.merchant_business_info_id,
                business_type=request.business_type,
                tax_id=request.tax_id,
                established_year=request.established_year,
                number_of_employees=request.number_of_employees,
                website_url=request.website_url,
            )
        except ValidationError as exc:
            raise err_grpc_validate_update_merchant_business from exc
        business = await self._service.update(update_request)
        response = merchant_business_common_pb2.ApiResponseMerchantBusiness(
            status="success", message="Successfully updated merchant business"
        )
        fill_merchant_business_response(response.data, business)
        return response

    @grpc_method(
        "MerchantBusinessCommandService.TrashedMerchantBusiness", SERVICE_NAME
    )
    async def TrashedMerchantBusiness(self, request: Any, context: Any) -> Any:
        if request.id == 0:
            raise err_grpc_invalid_merchant_business_id
        business = await self._service.trash(request.id)
        response = (
            merchant_business_common_pb2.ApiResponseMerchantBusinessDeleteAt(
                status="success", message="Successfully trashed merchant business"
            )
        )
        fill_merchant_business_response_delete_at(response.data, business)
        return response

    @grpc_method(
        "MerchantBusinessCommandService.RestoreMerchantBusiness", SERVICE_NAME
    )
    async def RestoreMerchantBusiness(self, request: Any, context: Any) -> Any:
        if request.id == 0:
            raise err_grpc_invalid_merchant_business_id
        business = await self._service.restore(request.id)
        response = (
            merchant_business_common_pb2.ApiResponseMerchantBusinessDeleteAt(
                status="success", message="Successfully restored merchant business"
            )
        )
        fill_merchant_business_response_delete_at(response.data, business)
        return response

    @grpc_method(
        "MerchantBusinessCommandService.DeleteMerchantBusinessPermanent",
        SERVICE_NAME,
    )
    async def DeleteMerchantBusinessPermanent(
        self, request: Any, context: Any
    ) -> Any:
        if request.id == 0:
            raise err_grpc_invalid_merchant_business_id
        await self._service.delete_permanent(request.id)
        return merchant_common_pb2.ApiResponseMerchantDelete(
            status="success",
            message="Successfully deleted merchant business permanently",
        )

    @grpc_method(
        "MerchantBusinessCommandService.RestoreAllMerchantBusiness", SERVICE_NAME
    )
    async def RestoreAllMerchantBusiness(self, request: Any, context: Any) -> Any:
        await self._service.restore_all()
        return merchant_common_pb2.ApiResponseMerchantAll(
            status="success",
            message="Successfully restored all trashed merchant businesses",
        )

    @grpc_method(
        "MerchantBusinessCommandService.DeleteAllMerchantBusinessPermanent",
        SERVICE_NAME,
    )
    async def DeleteAllMerchantBusinessPermanent(
        self, request: Any, context: Any
    ) -> Any:
        await self._service.delete_all()
        return merchant_common_pb2.ApiResponseMerchantAll(
            status="success",
            message="Successfully deleted all merchant businesses permanently",
        )


__all__ = ["MerchantBusinessCommandHandler"]

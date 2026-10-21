"""merchant_award command gRPC handler. `DeleteMerchantAwardPermanent` / `RestoreAllMerchantAward` / `DeleteAllMerchantAwardPermanent` reuse the merchant response envelopes (`pb.merchant.ApiResponseMerchantDelete`/`All`),."""

from __future__ import annotations

from typing import Any

from pydantic import ValidationError

from pb.merchant import merchant_common_pb2
from pb.merchant_award import (
    merchant_award_command_pb2_grpc,
    merchant_award_common_pb2,
)
from pkg.logger.logger import Logger
from pkg.middleware import grpc_method
from service.merchant_award.handler.mapping import (
    fill_merchant_award_response,
    fill_merchant_award_response_delete_at,
)
from service.merchant_award.service.interfaces import (
    MerchantAwardCommandService,
)
from service.merchant_award.service.service import SERVICE_NAME
from shared.domain.requests.merchant_award import (
    CreateMerchantCertificationOrAwardRequest,
    UpdateMerchantCertificationOrAwardRequest,
)
from shared.errors import (
    err_grpc_merchant_award_invalid_id,
    err_grpc_validate_create_merchant_award,
    err_grpc_validate_update_merchant_award,
)


class MerchantAwardCommandHandler(
    merchant_award_command_pb2_grpc.MerchantAwardCommandServiceServicer
):
    def __init__(self, service: MerchantAwardCommandService, logger: Logger) -> None:
        self._service = service
        self.logger = logger

    @grpc_method("MerchantAwardCommandService.Create", SERVICE_NAME)
    async def Create(self, request: Any, context: Any) -> Any:
        try:
            create_request = CreateMerchantCertificationOrAwardRequest(
                merchant_id=request.merchant_id,
                title=request.title,
                description=request.description,
                issued_by=request.issued_by,
                issue_date=request.issue_date,
                expiry_date=request.expiry_date,
                certificate_url=request.certificate_url,
            )
        except ValidationError as exc:
            raise err_grpc_validate_create_merchant_award from exc
        award = await self._service.create(create_request)
        response = merchant_award_common_pb2.ApiResponseMerchantAward(
            status="success", message="Successfully created merchant award"
        )
        fill_merchant_award_response(response.data, award)
        return response

    @grpc_method("MerchantAwardCommandService.Update", SERVICE_NAME)
    async def Update(self, request: Any, context: Any) -> Any:
        # No `id == 0` guard here — pointer `required` passes for 0 (see
        # module docstring); the repository then answers 404.
        try:
            update_request = UpdateMerchantCertificationOrAwardRequest(
                merchant_certification_id=request.merchant_certification_id,
                title=request.title,
                description=request.description,
                issued_by=request.issued_by,
                issue_date=request.issue_date,
                expiry_date=request.expiry_date,
                certificate_url=request.certificate_url,
            )
        except ValidationError as exc:
            raise err_grpc_validate_update_merchant_award from exc
        award = await self._service.update(update_request)
        response = merchant_award_common_pb2.ApiResponseMerchantAward(
            status="success", message="Successfully updated merchant award"
        )
        fill_merchant_award_response(response.data, award)
        return response

    @grpc_method("MerchantAwardCommandService.TrashedMerchantAward", SERVICE_NAME)
    async def TrashedMerchantAward(self, request: Any, context: Any) -> Any:
        if request.id == 0:
            raise err_grpc_merchant_award_invalid_id
        award = await self._service.trash(request.id)
        response = merchant_award_common_pb2.ApiResponseMerchantAwardDeleteAt(
            status="success", message="Successfully trashed merchant award"
        )
        fill_merchant_award_response_delete_at(response.data, award)
        return response

    @grpc_method("MerchantAwardCommandService.RestoreMerchantAward", SERVICE_NAME)
    async def RestoreMerchantAward(self, request: Any, context: Any) -> Any:
        if request.id == 0:
            raise err_grpc_merchant_award_invalid_id
        award = await self._service.restore(request.id)
        response = merchant_award_common_pb2.ApiResponseMerchantAwardDeleteAt(
            status="success", message="Successfully restored merchant award"
        )
        fill_merchant_award_response_delete_at(response.data, award)
        return response

    @grpc_method(
        "MerchantAwardCommandService.DeleteMerchantAwardPermanent", SERVICE_NAME
    )
    async def DeleteMerchantAwardPermanent(self, request: Any, context: Any) -> Any:
        if request.id == 0:
            raise err_grpc_merchant_award_invalid_id
        await self._service.delete_permanent(request.id)
        return merchant_common_pb2.ApiResponseMerchantDelete(
            status="success",
            message="Successfully deleted merchant award permanently",
        )

    @grpc_method(
        "MerchantAwardCommandService.RestoreAllMerchantAward", SERVICE_NAME
    )
    async def RestoreAllMerchantAward(self, request: Any, context: Any) -> Any:
        await self._service.restore_all()
        return merchant_common_pb2.ApiResponseMerchantAll(
            status="success",
            message="Successfully restored all trashed merchant awards",
        )

    @grpc_method(
        "MerchantAwardCommandService.DeleteAllMerchantAwardPermanent",
        SERVICE_NAME,
    )
    async def DeleteAllMerchantAwardPermanent(
        self, request: Any, context: Any
    ) -> Any:
        await self._service.delete_all()
        return merchant_common_pb2.ApiResponseMerchantAll(
            status="success",
            message="Successfully deleted all merchant awards permanently",
        )


__all__ = ["MerchantAwardCommandHandler"]

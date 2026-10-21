"""merchant_policy command gRPC handler. `Create`/`Update` validate the request body; a validation failure raises the matching sentinel. `Trash`/`Restore`/`DeletePermanent` guard `id == 0` with `err_grpc_invalid_merchant_policy_id` (400 "invalid merchant policy id"). As with merchant_award/merchant_business, `Update` deliberately does NOT guard `id == 0` (the pointer/optional id satisfies the `required` tag even for 0, so the repository answers 404). NORMALISATION: handler has no validation and never references its `err_grpc_validate_*` sentinels; wires them for other merchant_* domains. `DeleteMerchantPoliciesPermanent` / `RestoreAllMerchantPolicies` / `DeleteAllMerchantPoliciesPermanent` reuse the merchant response envelopes (`pb.merchant.ApiResponseMerchantDelete`/`All`),."""

from __future__ import annotations

from typing import Any

from pydantic import ValidationError

from pb.merchant import merchant_common_pb2
from pb.merchant_policy import (
    merchant_policy_command_pb2_grpc,
    merchant_policy_common_pb2,
)
from pkg.logger.logger import Logger
from pkg.middleware import grpc_method
from service.merchant_policy.handler.mapping import (
    fill_merchant_policy_response,
    fill_merchant_policy_response_delete_at,
)
from service.merchant_policy.service.interfaces import MerchantPolicyCommandService
from service.merchant_policy.service.service import SERVICE_NAME
from shared.domain.requests.merchant_policy import (
    CreateMerchantPolicyRequest,
    UpdateMerchantPolicyRequest,
)
from shared.errors import (
    err_grpc_invalid_merchant_policy_id,
    err_grpc_validate_create_merchant_policy,
    err_grpc_validate_update_merchant_policy,
)


class MerchantPolicyCommandHandler(
    merchant_policy_command_pb2_grpc.MerchantPolicyCommandServiceServicer
):
    def __init__(
        self, service: MerchantPolicyCommandService, logger: Logger
    ) -> None:
        self._service = service
        self.logger = logger

    @grpc_method("MerchantPolicyCommandService.Create", SERVICE_NAME)
    async def Create(self, request: Any, context: Any) -> Any:
        try:
            create_request = CreateMerchantPolicyRequest(
                merchant_id=request.merchant_id,
                policy_type=request.policy_type,
                title=request.title,
                description=request.description,
            )
        except ValidationError as exc:
            raise err_grpc_validate_create_merchant_policy from exc
        policy = await self._service.create(create_request)
        response = merchant_policy_common_pb2.ApiResponseMerchantPolicies(
            status="success", message="Successfully created merchant policy"
        )
        fill_merchant_policy_response(response.data, policy)
        return response

    @grpc_method("MerchantPolicyCommandService.Update", SERVICE_NAME)
    async def Update(self, request: Any, context: Any) -> Any:
        # No `id == 0` guard here — pointer `required` passes for 0 (see
        # module docstring); the repository then answers 404.
        try:
            update_request = UpdateMerchantPolicyRequest(
                merchant_policy_id=request.merchant_policy_id,
                policy_type=request.policy_type,
                title=request.title,
                description=request.description,
            )
        except ValidationError as exc:
            raise err_grpc_validate_update_merchant_policy from exc
        policy = await self._service.update(update_request)
        response = merchant_policy_common_pb2.ApiResponseMerchantPolicies(
            status="success", message="Successfully updated merchant policy"
        )
        fill_merchant_policy_response(response.data, policy)
        return response

    @grpc_method(
        "MerchantPolicyCommandService.TrashedMerchantPolicies", SERVICE_NAME
    )
    async def TrashedMerchantPolicies(self, request: Any, context: Any) -> Any:
        if request.id == 0:
            raise err_grpc_invalid_merchant_policy_id
        policy = await self._service.trash(request.id)
        response = (
            merchant_policy_common_pb2.ApiResponseMerchantPoliciesDeleteAt(
                status="success", message="Successfully processed merchant policy"
            )
        )
        fill_merchant_policy_response_delete_at(response.data, policy)
        return response

    @grpc_method(
        "MerchantPolicyCommandService.RestoreMerchantPolicies", SERVICE_NAME
    )
    async def RestoreMerchantPolicies(self, request: Any, context: Any) -> Any:
        if request.id == 0:
            raise err_grpc_invalid_merchant_policy_id
        policy = await self._service.restore(request.id)
        response = (
            merchant_policy_common_pb2.ApiResponseMerchantPoliciesDeleteAt(
                status="success", message="Successfully processed merchant policy"
            )
        )
        fill_merchant_policy_response_delete_at(response.data, policy)
        return response

    @grpc_method(
        "MerchantPolicyCommandService.DeleteMerchantPoliciesPermanent",
        SERVICE_NAME,
    )
    async def DeleteMerchantPoliciesPermanent(
        self, request: Any, context: Any
    ) -> Any:
        if request.id == 0:
            raise err_grpc_invalid_merchant_policy_id
        await self._service.delete_permanent(request.id)
        return merchant_common_pb2.ApiResponseMerchantDelete(
            status="success",
            message="Successfully deleted merchant policy permanently",
        )

    @grpc_method(
        "MerchantPolicyCommandService.RestoreAllMerchantPolicies", SERVICE_NAME
    )
    async def RestoreAllMerchantPolicies(self, request: Any, context: Any) -> Any:
        await self._service.restore_all()
        return merchant_common_pb2.ApiResponseMerchantAll(
            status="success",
            message="Successfully restored all merchant policies",
        )

    @grpc_method(
        "MerchantPolicyCommandService.DeleteAllMerchantPoliciesPermanent",
        SERVICE_NAME,
    )
    async def DeleteAllMerchantPoliciesPermanent(
        self, request: Any, context: Any
    ) -> Any:
        await self._service.delete_all()
        return merchant_common_pb2.ApiResponseMerchantAll(
            status="success",
            message="Successfully deleted all merchant policies permanently",
        )


__all__ = ["MerchantPolicyCommandHandler"]

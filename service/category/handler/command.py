"""Category command gRPC handler. Request-shape validation re-runs the `validator` rules through the shared Pydantic DTOs. Unlike `DeleteCategoryPermanent`/`DeleteAllCategoryPermanent` (which let the service's `AppError` — including a 409 FK conflict — flow through `errors.ToGrpcError`), the create/update/trash/restore paths collapse every service failure to their dedicated gRPC error, exactly."""

from __future__ import annotations

from typing import Any

from pydantic import ValidationError

from pb.category import category_command_pb2_grpc, category_common_pb2
from pkg.logger.logger import Logger
from pkg.middleware import grpc_method
from service.category.handler.mapping import (
    fill_category_response,
    fill_category_response_delete_at,
)
from service.category.service.interfaces import CategoryCommandService
from service.category.service.service import SERVICE_NAME
from shared.domain.requests.category import (
    CreateCategoryRequest,
    UpdateCategoryRequest,
)
from shared.errors import (
    err_grpc_category_invalid_id,
    err_grpc_category_not_found,
    err_grpc_create_category,
    err_grpc_update_category,
    err_grpc_validate_create_category,
    err_grpc_validate_update_category,
)


class CategoryCommandHandler(category_command_pb2_grpc.CategoryCommandServiceServicer):
    def __init__(self, service: CategoryCommandService, logger: Logger) -> None:
        self._service = service
        self.logger = logger

    @grpc_method("CategoryCommandService.Create", SERVICE_NAME)
    async def Create(self, request: Any, context: Any) -> Any:
        try:
            create_request = CreateCategoryRequest(
                name=request.name,
                description=request.description,
                slug_category=request.slug_category,
                image_category=request.image_category,
            )
        except ValidationError as exc:
            raise err_grpc_validate_create_category.with_internal(exc) from exc

        try:
            category = await self._service.create(create_request)
        except Exception as exc:  # noqa: BLE001 - collapses to one grpc error
            self.logger.error(f"Failed to create category: {exc}")
            raise err_grpc_create_category from exc

        response = category_common_pb2.ApiResponseCategory(
            status="success", message="Successfully created category"
        )
        fill_category_response(response.data, category)
        return response

    @grpc_method("CategoryCommandService.Update", SERVICE_NAME)
    async def Update(self, request: Any, context: Any) -> Any:
        if request.category_id == 0:
            raise err_grpc_category_invalid_id
        try:
            update_request = UpdateCategoryRequest(
                category_id=request.category_id,
                name=request.name,
                description=request.description,
                slug_category=request.slug_category,
                image_category=request.image_category,
            )
        except ValidationError as exc:
            raise err_grpc_validate_update_category.with_internal(exc) from exc

        try:
            category = await self._service.update(update_request)
        except Exception as exc:  # noqa: BLE001 - collapses to one grpc error
            self.logger.error(f"Failed to update category: {exc}")
            raise err_grpc_update_category from exc

        response = category_common_pb2.ApiResponseCategory(
            status="success", message="Successfully updated category"
        )
        fill_category_response(response.data, category)
        return response

    @grpc_method("CategoryCommandService.TrashedCategory", SERVICE_NAME)
    async def TrashedCategory(self, request: Any, context: Any) -> Any:
        if request.id == 0:
            raise err_grpc_category_invalid_id
        try:
            category = await self._service.trash(request.id)
        except Exception as exc:  # noqa: BLE001 - maps any error to NotFound
            self.logger.error(f"Failed to trash category: {exc}")
            raise err_grpc_category_not_found from exc

        response = category_common_pb2.ApiResponseCategoryDeleteAt(
            status="success", message="Successfully trashed category"
        )
        fill_category_response_delete_at(response.data, category)
        return response

    @grpc_method("CategoryCommandService.RestoreCategory", SERVICE_NAME)
    async def RestoreCategory(self, request: Any, context: Any) -> Any:
        if request.id == 0:
            raise err_grpc_category_invalid_id
        try:
            category = await self._service.restore(request.id)
        except Exception as exc:  # noqa: BLE001 - maps any error to NotFound
            self.logger.error(f"Failed to restore category: {exc}")
            raise err_grpc_category_not_found from exc

        response = category_common_pb2.ApiResponseCategoryDeleteAt(
            status="success", message="Successfully restored category"
        )
        fill_category_response_delete_at(response.data, category)
        return response

    @grpc_method("CategoryCommandService.DeleteCategoryPermanent", SERVICE_NAME)
    async def DeleteCategoryPermanent(self, request: Any, context: Any) -> Any:
        if request.id == 0:
            raise err_grpc_category_invalid_id
        # propagates the service error via errors.ToGrpcError (preserves a
        # 409 FK conflict); the middleware decorator does the same for us.
        await self._service.delete_permanent(request.id)
        return category_common_pb2.ApiResponseCategoryDelete(
            status="success", message="Successfully deleted category permanently"
        )

    @grpc_method("CategoryCommandService.RestoreAllCategory", SERVICE_NAME)
    async def RestoreAllCategory(self, request: Any, context: Any) -> Any:
        try:
            await self._service.restore_all()
        except Exception as exc:  # noqa: BLE001 - maps any error to NotFound
            self.logger.error(f"Failed to restore all categories: {exc}")
            raise err_grpc_category_not_found from exc

        return category_common_pb2.ApiResponseCategoryAll(
            status="success", message="Successfully restored all categories"
        )

    @grpc_method("CategoryCommandService.DeleteAllCategoryPermanent", SERVICE_NAME)
    async def DeleteAllCategoryPermanent(self, request: Any, context: Any) -> Any:
        # propagates via errors.ToGrpcError; the decorator preserves the code.
        await self._service.delete_all()
        return category_common_pb2.ApiResponseCategoryAll(
            status="success", message="Successfully deleted all categories permanently"
        )


__all__ = ["CategoryCommandHandler"]

"""product command gRPC handler. `Create`/`Update` build the request DTO and validate it; a validation failure raises the matching sentinel (`err_grpc_validate_create_product` / `err_grpc_validate_update_product`). `UpdateProductCountStock`/`AdjustProductStock` are internal RPCs (the gateway does not expose them) but are served."""

from __future__ import annotations

from typing import Any

from pydantic import ValidationError

from pb.product import product_command_pb2_grpc, product_common_pb2
from pkg.logger.logger import Logger
from pkg.middleware import grpc_method
from service.product.handler.mapping import (
    fill_product_response,
    fill_product_response_delete_at,
)
from service.product.service.interfaces import ProductCommandService
from service.product.service.service import SERVICE_NAME
from shared.domain.requests.product import (
    CreateProductRequest,
    UpdateProductRequest,
)
from shared.errors.product_errors import (
    err_grpc_invalid_id,
    err_grpc_validate_create_product,
    err_grpc_validate_update_product,
)


class ProductCommandHandler(product_command_pb2_grpc.ProductCommandServiceServicer):
    def __init__(self, service: ProductCommandService, logger: Logger) -> None:
        self._service = service
        self.logger = logger

    @grpc_method("ProductCommandService.Create", SERVICE_NAME)
    async def Create(self, request: Any, context: Any) -> Any:
        try:
            create_request = CreateProductRequest(
                merchant_id=request.merchant_id,
                category_id=request.category_id,
                name=request.name,
                description=request.description,
                price=request.price,
                count_in_stock=request.count_in_stock,
                brand=request.brand,
                weight=request.weight,
                rating=request.rating,
                slug_product=request.slug_product,
                image_product=request.image_product,
            )
        except ValidationError as exc:
            raise err_grpc_validate_create_product from exc
        product = await self._service.create(create_request)
        response = product_common_pb2.ApiResponseProduct(
            status="success", message="Successfully created product"
        )
        fill_product_response(response.data, product)
        return response

    @grpc_method("ProductCommandService.Update", SERVICE_NAME)
    async def Update(self, request: Any, context: Any) -> Any:
        if request.product_id == 0:
            raise err_grpc_invalid_id
        try:
            update_request = UpdateProductRequest(
                product_id=request.product_id,
                merchant_id=request.merchant_id,
                category_id=request.category_id,
                name=request.name,
                description=request.description,
                price=request.price,
                count_in_stock=request.count_in_stock,
                brand=request.brand,
                weight=request.weight,
                rating=request.rating,
                slug_product=request.slug_product,
                image_product=request.image_product,
            )
        except ValidationError as exc:
            raise err_grpc_validate_update_product from exc
        product = await self._service.update(update_request)
        response = product_common_pb2.ApiResponseProduct(
            status="success", message="Successfully updated product"
        )
        fill_product_response(response.data, product)
        return response

    @grpc_method("ProductCommandService.UpdateProductCountStock", SERVICE_NAME)
    async def UpdateProductCountStock(self, request: Any, context: Any) -> Any:
        product = await self._service.update_product_count_stock(request.product_id, request.stock)
        response = product_common_pb2.ApiResponseProduct(
            status="success", message="Successfully updated product count stock"
        )
        fill_product_response(response.data, product)
        return response

    @grpc_method("ProductCommandService.AdjustProductStock", SERVICE_NAME)
    async def AdjustProductStock(self, request: Any, context: Any) -> Any:
        product = await self._service.adjust_product_stock(
            request.product_id, request.delta, request.operation_id
        )
        response = product_common_pb2.ApiResponseProduct(
            status="success", message="Successfully adjusted product stock"
        )
        fill_product_response(response.data, product)
        return response

    @grpc_method("ProductCommandService.TrashedProduct", SERVICE_NAME)
    async def TrashedProduct(self, request: Any, context: Any) -> Any:
        if request.id == 0:
            raise err_grpc_invalid_id
        product = await self._service.trash(request.id)
        response = product_common_pb2.ApiResponseProductDeleteAt(
            status="success", message="Successfully trashed product"
        )
        fill_product_response_delete_at(response.data, product)
        return response

    @grpc_method("ProductCommandService.RestoreProduct", SERVICE_NAME)
    async def RestoreProduct(self, request: Any, context: Any) -> Any:
        if request.id == 0:
            raise err_grpc_invalid_id
        product = await self._service.restore(request.id)
        response = product_common_pb2.ApiResponseProductDeleteAt(
            status="success", message="Successfully restored product"
        )
        fill_product_response_delete_at(response.data, product)
        return response

    @grpc_method("ProductCommandService.DeleteProductPermanent", SERVICE_NAME)
    async def DeleteProductPermanent(self, request: Any, context: Any) -> Any:
        if request.id == 0:
            raise err_grpc_invalid_id
        await self._service.delete_permanent(request.id)
        return product_common_pb2.ApiResponseProductDelete(
            status="success",
            message="Successfully deleted product permanently",
        )

    @grpc_method("ProductCommandService.RestoreAllProduct", SERVICE_NAME)
    async def RestoreAllProduct(self, request: Any, context: Any) -> Any:
        await self._service.restore_all()
        return product_common_pb2.ApiResponseProductAll(
            status="success", message="Successfully restored all products"
        )

    @grpc_method("ProductCommandService.DeleteAllProductPermanent", SERVICE_NAME)
    async def DeleteAllProductPermanent(self, request: Any, context: Any) -> Any:
        await self._service.delete_all()
        return product_common_pb2.ApiResponseProductAll(
            status="success",
            message="Successfully deleted all products permanently",
        )


__all__ = ["ProductCommandHandler"]

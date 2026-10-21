"""Gateway product handler: REST <-> product gRPC. Only transport concerns live here: build the proto request, call the domain over gRPC, convert a gRPC failure back to its original AppError, and map the proto response to the shared response envelope. No SQL, no business rules. Like the other domains, deliberately does not cache in the gateway, so every request goes straight to the product service, which serves its own cache. `create`/`update` accept a multipart `image` file (`FormFile("image")` -> `uploads/products`) through `pkg.upload_image`. sends the uploaded path (empty when no file) as `image_product` and discards any `image_product` form field; a non-empty stored image is cleaned up when the RPC fails. Guards match exactly: query `find_by_id` rejects `id <= 0` with 400 `Invalid Product ID`, `find_by_merchant` rejects `merchant_id <= 0` with `Invalid Merchant ID`, `find_by_category` rejects an empty name with `Category Name is required`, and every command path-id route rejects `id <= 0` with `Invalid ID`. the gateway does not forward `min_price`/`max_price` on the merchant/category list routes, so does not either."""

from __future__ import annotations

from typing import Any

import grpc
from google.protobuf import empty_pb2

from pb.product import (
    product_command_pb2,
    product_command_pb2_grpc,
    product_common_pb2,
    product_query_pb2,
    product_query_pb2_grpc,
)
from pkg.upload_image import ImageUpload
from service.apigateway.app.client import ServiceConnections
from shared.domain.response.product import (
    ProductResponse,
    ProductResponseDeleteAt,
)
from shared.domain.response.responses import ApiResponse, APIResponsePagination
from shared.errors import new_bad_request_error, parse_grpc_error
from shared.mapper.product import (
    to_api_response_pagination_product,
    to_api_response_pagination_product_delete_at,
    to_api_response_product,
    to_api_response_product_all,
    to_api_response_product_delete,
    to_api_response_product_delete_at,
)

RPC_TIMEOUT = 30.0

_UPLOAD_DIR = "uploads/products"


def normalize_pagination(page: int, page_size: int) -> tuple[int, int]:
    """Gateway-side clamping."""
    if page <= 0:
        page = 1
    if page_size <= 0:
        page_size = 10
    return page, page_size


class ProductHandler:
    def __init__(self, connections: ServiceConnections, upload: ImageUpload) -> None:
        channel = connections.channel("product")
        self._query = product_query_pb2_grpc.ProductQueryServiceStub(channel)
        self._command = product_command_pb2_grpc.ProductCommandServiceStub(channel)
        self._upload = upload

    async def _resolve_image(self, image: Any) -> str:
        """Uploaded file path, or "" when no file (discards the form field)."""
        if image is not None:
            return await self._upload.process_image_upload(_UPLOAD_DIR, image, False)
        return ""

    # ---- query ----

    async def find_all(
        self, page: int, page_size: int, search: str
    ) -> APIResponsePagination[list[ProductResponse]]:
        page, page_size = normalize_pagination(page, page_size)
        request = product_query_pb2.FindAllProductRequest(page=page, page_size=page_size, search=search or "")
        try:
            response = await self._query.FindAll(request, timeout=RPC_TIMEOUT)
        except grpc.aio.AioRpcError as exc:
            raise parse_grpc_error(exc) from exc
        return to_api_response_pagination_product(response)

    async def find_by_id(self, product_id: int) -> ApiResponse[ProductResponse]:
        if product_id <= 0:
            raise new_bad_request_error("Invalid Product ID")
        request = product_common_pb2.FindByIdProductRequest(id=product_id)
        try:
            response = await self._query.FindById(request, timeout=RPC_TIMEOUT)
        except grpc.aio.AioRpcError as exc:
            raise parse_grpc_error(exc) from exc
        return to_api_response_product(response)

    async def find_by_merchant(
        self, merchant_id: int, page: int, page_size: int, search: str
    ) -> APIResponsePagination[list[ProductResponse]]:
        if merchant_id <= 0:
            raise new_bad_request_error("Invalid Merchant ID")
        page, page_size = normalize_pagination(page, page_size)
        request = product_query_pb2.FindAllProductMerchantRequest(
            merchant_id=merchant_id,
            page=page,
            page_size=page_size,
            search=search or "",
        )
        try:
            response = await self._query.FindByMerchant(request, timeout=RPC_TIMEOUT)
        except grpc.aio.AioRpcError as exc:
            raise parse_grpc_error(exc) from exc
        return to_api_response_pagination_product(response)

    async def find_by_category(
        self, category_name: str, page: int, page_size: int, search: str
    ) -> APIResponsePagination[list[ProductResponse]]:
        if not category_name:
            raise new_bad_request_error("Category Name is required")
        page, page_size = normalize_pagination(page, page_size)
        request = product_query_pb2.FindAllProductCategoryRequest(
            category_name=category_name,
            page=page,
            page_size=page_size,
            search=search or "",
        )
        try:
            response = await self._query.FindByCategory(request, timeout=RPC_TIMEOUT)
        except grpc.aio.AioRpcError as exc:
            raise parse_grpc_error(exc) from exc
        return to_api_response_pagination_product(response)

    async def find_by_active(
        self, page: int, page_size: int, search: str
    ) -> APIResponsePagination[list[ProductResponseDeleteAt]]:
        page, page_size = normalize_pagination(page, page_size)
        request = product_query_pb2.FindAllProductRequest(page=page, page_size=page_size, search=search or "")
        try:
            response = await self._query.FindByActive(request, timeout=RPC_TIMEOUT)
        except grpc.aio.AioRpcError as exc:
            raise parse_grpc_error(exc) from exc
        return to_api_response_pagination_product_delete_at(response)

    async def find_by_trashed(
        self, page: int, page_size: int, search: str
    ) -> APIResponsePagination[list[ProductResponseDeleteAt]]:
        page, page_size = normalize_pagination(page, page_size)
        request = product_query_pb2.FindAllProductRequest(page=page, page_size=page_size, search=search or "")
        try:
            response = await self._query.FindByTrashed(request, timeout=RPC_TIMEOUT)
        except grpc.aio.AioRpcError as exc:
            raise parse_grpc_error(exc) from exc
        return to_api_response_pagination_product_delete_at(response)

    # ---- command ----

    async def create(
        self,
        merchant_id: int,
        category_id: int,
        name: str,
        description: str,
        price: int,
        count_in_stock: int,
        brand: str,
        weight: int,
        rating: int,
        slug_product: str,
        image: Any,
    ) -> ApiResponse[ProductResponse]:
        image_path = await self._resolve_image(image)
        request = product_command_pb2.CreateProductRequest(
            merchant_id=merchant_id,
            category_id=category_id,
            name=name,
            description=description,
            price=price,
            count_in_stock=count_in_stock,
            brand=brand,
            weight=weight,
            rating=rating,
            slug_product=slug_product,
            image_product=image_path,
        )
        try:
            response = await self._command.Create(request, timeout=RPC_TIMEOUT)
        except grpc.aio.AioRpcError as exc:
            if image_path:
                self._upload.cleanup_image_on_failure(image_path)
            raise parse_grpc_error(exc) from exc
        return to_api_response_product(response)

    async def update(
        self,
        product_id: int,
        merchant_id: int,
        category_id: int,
        name: str,
        description: str,
        price: int,
        count_in_stock: int,
        brand: str,
        weight: int,
        rating: int,
        slug_product: str,
        image: Any,
    ) -> ApiResponse[ProductResponse]:
        if product_id <= 0:
            raise new_bad_request_error("Invalid ID")
        image_path = await self._resolve_image(image)
        request = product_command_pb2.UpdateProductRequest(
            product_id=product_id,
            merchant_id=merchant_id,
            category_id=category_id,
            name=name,
            description=description,
            price=price,
            count_in_stock=count_in_stock,
            brand=brand,
            weight=weight,
            rating=rating,
            slug_product=slug_product,
            image_product=image_path,
        )
        try:
            response = await self._command.Update(request, timeout=RPC_TIMEOUT)
        except grpc.aio.AioRpcError as exc:
            if image_path:
                self._upload.cleanup_image_on_failure(image_path)
            raise parse_grpc_error(exc) from exc
        return to_api_response_product(response)

    async def trash(self, product_id: int) -> ApiResponse[ProductResponseDeleteAt]:
        if product_id <= 0:
            raise new_bad_request_error("Invalid ID")
        request = product_common_pb2.FindByIdProductRequest(id=product_id)
        try:
            response = await self._command.TrashedProduct(request, timeout=RPC_TIMEOUT)
        except grpc.aio.AioRpcError as exc:
            raise parse_grpc_error(exc) from exc
        return to_api_response_product_delete_at(response)

    async def restore(self, product_id: int) -> ApiResponse[ProductResponseDeleteAt]:
        if product_id <= 0:
            raise new_bad_request_error("Invalid ID")
        request = product_common_pb2.FindByIdProductRequest(id=product_id)
        try:
            response = await self._command.RestoreProduct(request, timeout=RPC_TIMEOUT)
        except grpc.aio.AioRpcError as exc:
            raise parse_grpc_error(exc) from exc
        return to_api_response_product_delete_at(response)

    async def delete_permanent(self, product_id: int) -> ApiResponse[None]:
        if product_id <= 0:
            raise new_bad_request_error("Invalid ID")
        request = product_common_pb2.FindByIdProductRequest(id=product_id)
        try:
            response = await self._command.DeleteProductPermanent(request, timeout=RPC_TIMEOUT)
        except grpc.aio.AioRpcError as exc:
            raise parse_grpc_error(exc) from exc
        return to_api_response_product_delete(response)

    async def restore_all(self) -> ApiResponse[None]:
        try:
            response = await self._command.RestoreAllProduct(empty_pb2.Empty(), timeout=RPC_TIMEOUT)
        except grpc.aio.AioRpcError as exc:
            raise parse_grpc_error(exc) from exc
        return to_api_response_product_all(response)

    async def delete_all_permanent(self) -> ApiResponse[None]:
        try:
            response = await self._command.DeleteAllProductPermanent(empty_pb2.Empty(), timeout=RPC_TIMEOUT)
        except grpc.aio.AioRpcError as exc:
            raise parse_grpc_error(exc) from exc
        return to_api_response_product_all(response)


__all__ = ["ProductHandler", "normalize_pagination"]

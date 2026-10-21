"""Gateway category handler: REST <-> category gRPC. Only transport concerns live here: build the proto request, call the domain over gRPC, convert a gRPC failure back to its original AppError, and map the proto response to the shared response envelope. No SQL, no business rules. Deliberate deviation from (recorded in Planning.md): the gateway wraps every response in its own per-domain Redis cache (`apigateway/cache/category`); this code keeps caching inside the domain service only, matching the banner precedent. `create`/`update` accept a multipart `image` file (`FormFile("image")` -> `uploads/category`) through `pkg.upload_image`. When a file is present its stored path is sent as `image_category`; otherwise falls back to the `image_category` form field. *discards* `image_category` and always sends the uploaded path (empty when no file) — a source defect documents and fixes. The three stats servicers share one `CategoryHandler` because wires them into a single `categoryStatsHandlerApi`."""

from __future__ import annotations

from typing import Any

import grpc
from google.protobuf import empty_pb2

from pb.category import (
    category_command_pb2,
    category_command_pb2_grpc,
    category_common_pb2,
    category_query_pb2,
    category_query_pb2_grpc,
)
from pb.category.stats import (
    category_stats_byid_pb2_grpc,
    category_stats_bymerchant_pb2_grpc,
    category_stats_pb2_grpc,
)
from pkg.upload_image import ImageUpload
from service.apigateway.app.client import ServiceConnections
from shared.domain.response.category import (
    CategoriesMonthlyTotalPriceResponse,
    CategoriesYearlyTotalPriceResponse,
    CategoryMonthPriceResponse,
    CategoryResponse,
    CategoryResponseDeleteAt,
    CategoryYearPriceResponse,
)
from shared.domain.response.responses import ApiResponse, APIResponsePagination
from shared.errors import parse_grpc_error
from shared.mapper.category import (
    to_api_response_category,
    to_api_response_category_all,
    to_api_response_category_delete,
    to_api_response_category_delete_at,
    to_api_response_category_month_price,
    to_api_response_category_monthly_total_price,
    to_api_response_category_year_price,
    to_api_response_category_yearly_total_price,
    to_api_response_pagination_category,
    to_api_response_pagination_category_delete_at,
)

RPC_TIMEOUT = 30.0

_UPLOAD_DIR = "uploads/category"


def normalize_pagination(page: int, page_size: int) -> tuple[int, int]:
    """Gateway-side clamping."""
    if page <= 0:
        page = 1
    if page_size <= 0:
        page_size = 10
    return page, page_size


class CategoryHandler:
    def __init__(self, connections: ServiceConnections, upload: ImageUpload) -> None:
        channel = connections.channel("category")
        self._query = category_query_pb2_grpc.CategoryQueryServiceStub(channel)
        self._command = category_command_pb2_grpc.CategoryCommandServiceStub(channel)
        self._stats = category_stats_pb2_grpc.CategoryStatsServiceStub(channel)
        self._stats_by_id = category_stats_byid_pb2_grpc.CategoryStatsByIdServiceStub(
            channel
        )
        self._stats_by_merchant = (
            category_stats_bymerchant_pb2_grpc.CategoryStatsByMerchantServiceStub(
                channel
            )
        )
        self._upload = upload

    async def _resolve_image(self, image: Any, image_category: str) -> str:
        """Resolve the stored image path: uploaded file wins, else the field. sends only the uploaded path (empty when no file), discarding the validated `image_category` field — see the module docstring."""
        if image is not None:
            return await self._upload.process_image_upload(_UPLOAD_DIR, image, False)
        return image_category or ""

    # ---- query ----

    async def find_all(
        self, page: int, page_size: int, search: str
    ) -> APIResponsePagination[list[CategoryResponse]]:
        page, page_size = normalize_pagination(page, page_size)
        request = category_query_pb2.FindAllCategoryRequest(
            page=page, page_size=page_size, search=search or ""
        )
        try:
            response = await self._query.FindAll(request, timeout=RPC_TIMEOUT)
        except grpc.aio.AioRpcError as exc:
            raise parse_grpc_error(exc) from exc
        return to_api_response_pagination_category(response)

    async def find_by_id(self, category_id: int) -> ApiResponse[CategoryResponse]:
        request = category_common_pb2.FindByIdCategoryRequest(id=category_id)
        try:
            response = await self._query.FindById(request, timeout=RPC_TIMEOUT)
        except grpc.aio.AioRpcError as exc:
            raise parse_grpc_error(exc) from exc
        return to_api_response_category(response)

    async def find_by_active(
        self, page: int, page_size: int, search: str
    ) -> APIResponsePagination[list[CategoryResponseDeleteAt]]:
        page, page_size = normalize_pagination(page, page_size)
        request = category_query_pb2.FindAllCategoryRequest(
            page=page, page_size=page_size, search=search or ""
        )
        try:
            response = await self._query.FindByActive(request, timeout=RPC_TIMEOUT)
        except grpc.aio.AioRpcError as exc:
            raise parse_grpc_error(exc) from exc
        return to_api_response_pagination_category_delete_at(response)

    async def find_by_trashed(
        self, page: int, page_size: int, search: str
    ) -> APIResponsePagination[list[CategoryResponseDeleteAt]]:
        page, page_size = normalize_pagination(page, page_size)
        request = category_query_pb2.FindAllCategoryRequest(
            page=page, page_size=page_size, search=search or ""
        )
        try:
            response = await self._query.FindByTrashed(request, timeout=RPC_TIMEOUT)
        except grpc.aio.AioRpcError as exc:
            raise parse_grpc_error(exc) from exc
        return to_api_response_pagination_category_delete_at(response)

    # ---- command ----

    async def create(
        self,
        name: str,
        description: str,
        slug_category: str,
        image_category: str,
        image: Any,
    ) -> ApiResponse[CategoryResponse]:
        image_url = await self._resolve_image(image, image_category)
        request = category_command_pb2.CreateCategoryRequest(
            name=name,
            description=description,
            slug_category=slug_category,
            image_category=image_url,
        )
        try:
            response = await self._command.Create(request, timeout=RPC_TIMEOUT)
        except grpc.aio.AioRpcError as exc:
            raise parse_grpc_error(exc) from exc
        return to_api_response_category(response)

    async def update(
        self,
        category_id: int,
        name: str,
        description: str,
        slug_category: str,
        image_category: str,
        image: Any,
    ) -> ApiResponse[CategoryResponse]:
        image_url = await self._resolve_image(image, image_category)
        request = category_command_pb2.UpdateCategoryRequest(
            category_id=category_id,
            name=name,
            description=description,
            slug_category=slug_category,
            image_category=image_url,
        )
        try:
            response = await self._command.Update(request, timeout=RPC_TIMEOUT)
        except grpc.aio.AioRpcError as exc:
            raise parse_grpc_error(exc) from exc
        return to_api_response_category(response)

    async def trash(self, category_id: int) -> ApiResponse[CategoryResponseDeleteAt]:
        request = category_common_pb2.FindByIdCategoryRequest(id=category_id)
        try:
            response = await self._command.TrashedCategory(request, timeout=RPC_TIMEOUT)
        except grpc.aio.AioRpcError as exc:
            raise parse_grpc_error(exc) from exc
        return to_api_response_category_delete_at(response)

    async def restore(self, category_id: int) -> ApiResponse[CategoryResponseDeleteAt]:
        request = category_common_pb2.FindByIdCategoryRequest(id=category_id)
        try:
            response = await self._command.RestoreCategory(request, timeout=RPC_TIMEOUT)
        except grpc.aio.AioRpcError as exc:
            raise parse_grpc_error(exc) from exc
        return to_api_response_category_delete_at(response)

    async def delete_permanent(self, category_id: int) -> ApiResponse[None]:
        request = category_common_pb2.FindByIdCategoryRequest(id=category_id)
        try:
            response = await self._command.DeleteCategoryPermanent(
                request, timeout=RPC_TIMEOUT
            )
        except grpc.aio.AioRpcError as exc:
            raise parse_grpc_error(exc) from exc
        return to_api_response_category_delete(response)

    async def restore_all(self) -> ApiResponse[None]:
        try:
            response = await self._command.RestoreAllCategory(
                empty_pb2.Empty(), timeout=RPC_TIMEOUT
            )
        except grpc.aio.AioRpcError as exc:
            raise parse_grpc_error(exc) from exc
        return to_api_response_category_all(response)

    async def delete_all_permanent(self) -> ApiResponse[None]:
        try:
            response = await self._command.DeleteAllCategoryPermanent(
                empty_pb2.Empty(), timeout=RPC_TIMEOUT
            )
        except grpc.aio.AioRpcError as exc:
            raise parse_grpc_error(exc) from exc
        return to_api_response_category_all(response)

    # ---- stats ----

    async def find_month_total_price(
        self, year: int, month: int
    ) -> ApiResponse[list[CategoriesMonthlyTotalPriceResponse]]:
        request = category_common_pb2.FindYearMonthTotalPrices(year=year, month=month)
        try:
            response = await self._stats.FindMonthlyTotalPrices(
                request, timeout=RPC_TIMEOUT
            )
        except grpc.aio.AioRpcError as exc:
            raise parse_grpc_error(exc) from exc
        return to_api_response_category_monthly_total_price(response)

    async def find_year_total_price(
        self, year: int
    ) -> ApiResponse[list[CategoriesYearlyTotalPriceResponse]]:
        request = category_common_pb2.FindYearTotalPrices(year=year)
        try:
            response = await self._stats.FindYearlyTotalPrices(
                request, timeout=RPC_TIMEOUT
            )
        except grpc.aio.AioRpcError as exc:
            raise parse_grpc_error(exc) from exc
        return to_api_response_category_yearly_total_price(response)

    async def find_month_total_price_by_merchant(
        self, year: int, month: int, merchant_id: int
    ) -> ApiResponse[list[CategoriesMonthlyTotalPriceResponse]]:
        request = category_common_pb2.FindYearMonthTotalPriceByMerchant(
            year=year, month=month, merchant_id=merchant_id
        )
        try:
            response = await self._stats_by_merchant.FindMonthlyTotalPricesByMerchant(
                request, timeout=RPC_TIMEOUT
            )
        except grpc.aio.AioRpcError as exc:
            raise parse_grpc_error(exc) from exc
        return to_api_response_category_monthly_total_price(response)

    async def find_year_total_price_by_merchant(
        self, year: int, merchant_id: int
    ) -> ApiResponse[list[CategoriesYearlyTotalPriceResponse]]:
        request = category_common_pb2.FindYearTotalPriceByMerchant(
            year=year, merchant_id=merchant_id
        )
        try:
            response = await self._stats_by_merchant.FindYearlyTotalPricesByMerchant(
                request, timeout=RPC_TIMEOUT
            )
        except grpc.aio.AioRpcError as exc:
            raise parse_grpc_error(exc) from exc
        return to_api_response_category_yearly_total_price(response)

    async def find_month_total_price_by_id(
        self, year: int, month: int, category_id: int
    ) -> ApiResponse[list[CategoriesMonthlyTotalPriceResponse]]:
        request = category_common_pb2.FindYearMonthTotalPriceById(
            year=year, month=month, category_id=category_id
        )
        try:
            response = await self._stats_by_id.FindMonthlyTotalPricesById(
                request, timeout=RPC_TIMEOUT
            )
        except grpc.aio.AioRpcError as exc:
            raise parse_grpc_error(exc) from exc
        return to_api_response_category_monthly_total_price(response)

    async def find_year_total_price_by_id(
        self, year: int, category_id: int
    ) -> ApiResponse[list[CategoriesYearlyTotalPriceResponse]]:
        request = category_common_pb2.FindYearTotalPriceById(
            year=year, category_id=category_id
        )
        try:
            response = await self._stats_by_id.FindYearlyTotalPricesById(
                request, timeout=RPC_TIMEOUT
            )
        except grpc.aio.AioRpcError as exc:
            raise parse_grpc_error(exc) from exc
        return to_api_response_category_yearly_total_price(response)

    async def find_month_price(
        self, year: int
    ) -> ApiResponse[list[CategoryMonthPriceResponse]]:
        # reads `month` from the query string but only uses it for its
        # (skipped) gateway cache key; the domain call takes `year` alone.
        request = category_common_pb2.FindYearCategory(year=year)
        try:
            response = await self._stats.FindMonthPrice(request, timeout=RPC_TIMEOUT)
        except grpc.aio.AioRpcError as exc:
            raise parse_grpc_error(exc) from exc
        return to_api_response_category_month_price(response)

    async def find_year_price(
        self, year: int
    ) -> ApiResponse[list[CategoryYearPriceResponse]]:
        request = category_common_pb2.FindYearCategory(year=year)
        try:
            response = await self._stats.FindYearPrice(request, timeout=RPC_TIMEOUT)
        except grpc.aio.AioRpcError as exc:
            raise parse_grpc_error(exc) from exc
        return to_api_response_category_year_price(response)

    async def find_month_price_by_merchant(
        self, year: int, merchant_id: int
    ) -> ApiResponse[list[CategoryMonthPriceResponse]]:
        request = category_common_pb2.FindYearCategoryByMerchant(
            year=year, merchant_id=merchant_id
        )
        try:
            response = await self._stats_by_merchant.FindMonthPriceByMerchant(
                request, timeout=RPC_TIMEOUT
            )
        except grpc.aio.AioRpcError as exc:
            raise parse_grpc_error(exc) from exc
        return to_api_response_category_month_price(response)

    async def find_year_price_by_merchant(
        self, year: int, merchant_id: int
    ) -> ApiResponse[list[CategoryYearPriceResponse]]:
        request = category_common_pb2.FindYearCategoryByMerchant(
            year=year, merchant_id=merchant_id
        )
        try:
            response = await self._stats_by_merchant.FindYearPriceByMerchant(
                request, timeout=RPC_TIMEOUT
            )
        except grpc.aio.AioRpcError as exc:
            raise parse_grpc_error(exc) from exc
        return to_api_response_category_year_price(response)

    async def find_month_price_by_id(
        self, year: int, category_id: int
    ) -> ApiResponse[list[CategoryMonthPriceResponse]]:
        request = category_common_pb2.FindYearCategoryById(
            year=year, category_id=category_id
        )
        try:
            response = await self._stats_by_id.FindMonthPriceById(
                request, timeout=RPC_TIMEOUT
            )
        except grpc.aio.AioRpcError as exc:
            raise parse_grpc_error(exc) from exc
        return to_api_response_category_month_price(response)

    async def find_year_price_by_id(
        self, year: int, category_id: int
    ) -> ApiResponse[list[CategoryYearPriceResponse]]:
        request = category_common_pb2.FindYearCategoryById(
            year=year, category_id=category_id
        )
        try:
            response = await self._stats_by_id.FindYearPriceById(
                request, timeout=RPC_TIMEOUT
            )
        except grpc.aio.AioRpcError as exc:
            raise parse_grpc_error(exc) from exc
        return to_api_response_category_year_price(response)


__all__ = ["CategoryHandler", "normalize_pagination"]

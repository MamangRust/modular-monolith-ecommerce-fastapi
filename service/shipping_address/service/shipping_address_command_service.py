"""Shipping address command service. Every mutation invalidates the `shipping_address:*` cache after the write commits — except `RestoreAll`, which in forgets to call the invalidator. That omission is preserved here for wire."""

from __future__ import annotations

from pkg.database.schema.shipping_address import (
    CreateShippingAddressRow,
    ShippingAddress,
    UpdateShippingAddressRow,
)
from pkg.logger.logger import Logger
from service.shipping_address.redis.interfaces import ShippingAddressCommandCache
from service.shipping_address.repository.interfaces import (
    ShippingAddressCommandRepository,
)
from shared.domain.requests.shipping_address import (
    CreateShippingAddressRequest,
    UpdateShippingAddressRequest,
)
from shared.errors import (
    err_failed_create_shipping_address,
    err_failed_delete_shipping_address_permanent,
    err_failed_restore_all_shipping_addresses,
    err_failed_update_shipping_address,
)
from shared.observability import Observability


class ShippingAddressCommandServiceImpl:
    def __init__(
        self,
        repo: ShippingAddressCommandRepository,
        cache: ShippingAddressCommandCache,
        logger: Logger,
        obs: Observability,
    ) -> None:
        self._repo = repo
        self._cache = cache
        self._logger = logger
        self._obs = obs

    async def create(
        self, request: CreateShippingAddressRequest
    ) -> CreateShippingAddressRow:
        with self._obs.span(
            "shipping_address.command.create",
            order_id=request.order_id,
            kota=request.kota,
        ):
            try:
                row = await self._repo.create(request)
            except Exception as exc:  # noqa: BLE001 - collapses to one sentinel
                self._logger.error(f"Failed to create shipping address: {exc}")
                raise err_failed_create_shipping_address from exc
            await self._cache.invalidate_shipping_address_cache()
            self._logger.info(
                "shipping address created",
                shipping_address_id=row.shipping_address_id,
            )
            return row

    async def update(
        self, request: UpdateShippingAddressRequest
    ) -> UpdateShippingAddressRow:
        with self._obs.span(
            "shipping_address.command.update", shipping_id=request.shipping_id
        ):
            try:
                row = await self._repo.update(request)
            except Exception as exc:  # noqa: BLE001 - collapses to one sentinel
                self._logger.error(f"Failed to update shipping address: {exc}")
                raise err_failed_update_shipping_address from exc
            await self._cache.invalidate_shipping_address_cache()
            self._logger.info(
                "shipping address updated", shipping_id=request.shipping_id
            )
            return row

    async def trash(self, shipping_id: int) -> ShippingAddress:
        with self._obs.span(
            "shipping_address.command.trash", shipping_id=shipping_id
        ):
            row = await self._repo.trash(shipping_id)
            await self._cache.invalidate_shipping_address_cache()
            self._logger.info("shipping address trashed", shipping_id=shipping_id)
            return row

    async def restore(self, shipping_id: int) -> ShippingAddress:
        with self._obs.span(
            "shipping_address.command.restore", shipping_id=shipping_id
        ):
            row = await self._repo.restore(shipping_id)
            await self._cache.invalidate_shipping_address_cache()
            self._logger.info("shipping address restored", shipping_id=shipping_id)
            return row

    async def delete_permanent(self, shipping_id: int) -> bool:
        with self._obs.span(
            "shipping_address.command.delete_permanent", shipping_id=shipping_id
        ):
            success = await self._repo.delete_permanent(shipping_id)
            await self._cache.invalidate_shipping_address_cache()
            self._logger.info(
                "shipping address deleted permanently", shipping_id=shipping_id
            )
            return success

    async def delete_by_order_id_permanent(self, order_id: int) -> bool:
        with self._obs.span(
            "shipping_address.command.delete_by_order_id_permanent",
            order_id=order_id,
        ):
            try:
                success = await self._repo.delete_by_order_id_permanent(order_id)
            except Exception as exc:  # noqa: BLE001 - collapses to one sentinel
                self._logger.error(
                    f"Failed to permanently delete shipping addresses by order: {exc}"
                )
                raise err_failed_delete_shipping_address_permanent from exc
            await self._cache.invalidate_shipping_address_cache()
            self._logger.info(
                "shipping addresses deleted by order permanently", order_id=order_id
            )
            return success

    async def restore_all(self) -> bool:
        with self._obs.span("shipping_address.command.restore_all"):
            try:
                success = await self._repo.restore_all()
            except Exception as exc:  # noqa: BLE001 - collapses to one sentinel
                self._logger.error(f"Failed to restore all shipping addresses: {exc}")
                raise err_failed_restore_all_shipping_addresses from exc
            # RestoreAll never invalidates the cache here.
            self._logger.info("all shipping addresses restored")
            return success

    async def delete_all(self) -> bool:
        with self._obs.span("shipping_address.command.delete_all"):
            success = await self._repo.delete_all()
            await self._cache.invalidate_shipping_address_cache()
            self._logger.info("all shipping addresses deleted permanently")
            return success


__all__ = ["ShippingAddressCommandServiceImpl"]

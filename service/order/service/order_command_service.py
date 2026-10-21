"""order command service. `Create` runs a multi-service saga with best-effort compensation: it reserves stock through the atomic delta RPC, writes the reservation ledger and order items, creates the shipping address remotely, computes the total and finalises the order. Any failure unwinds the reservations, stock and child rows. `Update` diffs each item against the persisted order, moving stock by the quantity delta and registering an inverse operation per successful mutation. Shipping is resolved through the query adapter (by supplied id, else by order), then updated remotely. `Trash`/`Restore` drive the reservation ledger's conditional transitions (`reserved -> released`, `released -> reserved`) and adjust stock around them; the conditional SQL is the concurrency guard. `DeletePermanent` purges the trashed order and all children in one atomic CTE. `ReconcileStockReservations` and `CleanupIdempotencyRecords` are the internal maintenance entry points (no RPC), per the approved plan. The service itself only raises `err_bad_request.WithMessage(.)` for its own validation and `err_insufficient_product_stock` when the guarded stock UPDATE loses a race. `pgx.ErrNoRows` is the `NoRowsError`: the ledger transitions surface it when a conditional UPDATE matches no row, which the compensation logic treats as "another worker already claimed it" (skip, not fail)."""

from __future__ import annotations

from collections.abc import Awaitable, Callable
from datetime import UTC, datetime, timedelta
from typing import NoReturn

from pkg.database.errors import NoRowsError
from pkg.database.schema.order import Order, OrderRow, OrderStockReservation
from pkg.logger.logger import Logger
from service.order.redis.interfaces import OrderCommandCache
from service.order.repository.interfaces import (
    MerchantQueryRepository,
    OrderCommandRepository,
    OrderItemCommandRepository,
    OrderItemQueryRepository,
    OrderQueryRepository,
    ProductCommandRepository,
    ProductQueryRepository,
    ShippingAddressCommandRepository,
    ShippingQueryRepository,
    StockReservationRepository,
    TransactionCommandRepository,
    UserQueryRepository,
)
from service.order.service.interfaces import CleanupResult, ReconcileResult
from shared.domain.requests.order import (
    CreateOrderRecordRequest,
    CreateOrderRequest,
    UpdateOrderRecordRequest,
    UpdateOrderRequest,
)
from shared.domain.requests.order_item import (
    CreateOrderItemRecordRequest,
    UpdateOrderItemRecordRequest,
)
from shared.domain.requests.shipping_address import (
    CreateShippingAddressRequest,
    UpdateShippingAddressRequest,
)
from shared.errors.core import AppError, err_bad_request
from shared.errors.order_errors import err_insufficient_product_stock, err_order_not_found
from shared.observability import Observability


class OrderCommandServiceImpl:
    def __init__(
        self,
        *,
        user_query: UserQueryRepository,
        merchant_query: MerchantQueryRepository,
        product_query: ProductQueryRepository,
        product_command: ProductCommandRepository,
        order_query: OrderQueryRepository,
        order_command: OrderCommandRepository,
        order_item_query: OrderItemQueryRepository,
        order_item_command: OrderItemCommandRepository,
        shipping_address: ShippingAddressCommandRepository,
        transaction_command: TransactionCommandRepository,
        shipping_query: ShippingQueryRepository,
        stock_reservation: StockReservationRepository,
        cache: OrderCommandCache,
        logger: Logger,
        obs: Observability,
    ) -> None:
        # `user_query`/`merchant_query`/`transaction_command` are held for
        # wiring with struct but never invoked (dead wiring).
        self._user_query = user_query
        self._merchant_query = merchant_query
        self._product_query = product_query
        self._product_command = product_command
        self._order_query = order_query
        self._order_command = order_command
        self._order_item_query = order_item_query
        self._order_item_command = order_item_command
        self._shipping_address = shipping_address
        self._transaction_command = transaction_command
        self._shipping_query = shipping_query
        self._stock = stock_reservation
        self._cache = cache
        self._logger = logger
        self._obs = obs

    # ------------------------------------------------------------------ create

    async def create(self, request: CreateOrderRequest) -> OrderRow:
        if request is None:
            raise err_bad_request.with_message("order request is required")

        with self._obs.span(
            "order.command.create",
            merchant_id=request.merchant_id,
            user_id=request.user_id,
        ):
            order = await self._order_command.create(
                CreateOrderRecordRequest(
                    merchant_id=request.merchant_id,
                    user_id=request.user_id,
                    total_price=0,
                )
            )
            order_id = int(order.order_id)
            adjusted: list[tuple[int, int]] = []

            async def rollback() -> None:
                for product_id, quantity in reversed(adjusted):
                    released = False
                    try:
                        await self._stock.release(order_id, product_id)
                        released = True
                    except NoRowsError:
                        released = True
                    except Exception as exc:
                        self._logger.error(
                            "failed to release compensated stock reservation",
                            error=str(exc),
                            product_id=product_id,
                        )
                        continue
                    if released:
                        try:
                            await self._product_command.adjust_product_stock(
                                product_id,
                                quantity,
                                f"order-create-rollback-{order_id}-{product_id}",
                            )
                        except Exception as exc:
                            self._logger.error(
                                "failed to compensate reserved product stock",
                                error=str(exc),
                                product_id=product_id,
                                quantity=quantity,
                            )
                try:
                    await self._order_command.trash(order_id)
                except Exception as exc:
                    self._logger.error(
                        "failed to trash incomplete order",
                        error=str(exc),
                        order_id=order_id,
                    )
                    return
                try:
                    await self._order_command.delete_permanent_with_children(order_id)
                except Exception as exc:
                    self._logger.error(
                        "failed to permanently delete incomplete order",
                        error=str(exc),
                        order_id=order_id,
                    )

            async def fail(err: BaseException) -> NoReturn:
                await rollback()
                raise err

            async def guard[T](coro: Awaitable[T]) -> T:
                try:
                    return await coro
                except Exception as exc:
                    await fail(exc)
                    raise

            for item in request.items:
                product = await guard(self._product_query.find_by_id(item.product_id))

                # Reserve first through the atomic delta RPC; the database guard
                # is the final authority against overselling.
                operation_id = (
                    f"order-create-{order_id}-item-{len(adjusted)}"
                    f"-product-{product.product_id}-quantity-{item.quantity}"
                )
                try:
                    await self._product_command.adjust_product_stock(
                        int(product.product_id), -item.quantity, operation_id
                    )
                except Exception as exc:
                    current = None
                    try:
                        current = await self._product_query.find_by_id(item.product_id)
                    except Exception:
                        current = None
                    if current is not None and current.count_in_stock < item.quantity:
                        await fail(err_insufficient_product_stock)
                    await fail(exc)

                adjusted.append((int(product.product_id), item.quantity))
                await guard(
                    self._stock.upsert(order_id, int(product.product_id), item.quantity)
                )
                await guard(
                    self._order_item_command.create(
                        CreateOrderItemRecordRequest(
                            order_id=order_id,
                            product_id=item.product_id,
                            quantity=item.quantity,
                            price=int(product.price),
                        )
                    )
                )

            await guard(
                self._shipping_address.create(
                    CreateShippingAddressRequest(
                        order_id=order_id,
                        alamat=request.shipping_address.alamat,
                        provinsi=request.shipping_address.provinsi,
                        kota=request.shipping_address.kota,
                        courier=request.shipping_address.courier,
                        shipping_method=request.shipping_address.shipping_method,
                        shipping_cost=request.shipping_address.shipping_cost,
                        negara=request.shipping_address.negara,
                    )
                )
            )

            total_price = await guard(
                self._order_item_query.calculate_total_price(order_id)
            )
            return await guard(
                self._order_command.update(
                    UpdateOrderRecordRequest(
                        order_id=order_id,
                        merchant_id=0,
                        user_id=request.user_id,
                        total_price=total_price + request.shipping_address.shipping_cost,
                    )
                )
            )

    # ------------------------------------------------------------------ update

    async def update(self, request: UpdateOrderRequest) -> OrderRow:
        if request is None or request.order_id is None or request.order_id <= 0:
            raise err_bad_request.with_message("order id is required")
        order_id = request.order_id

        with self._obs.span(
            "order.command.update",
            order_id=order_id,
            user_id=request.user_id,
        ):
            # Pre-flight reads have nothing to roll back yet, so their errors
            # propagate directly (returns HandleError without compensation).
            existing_order = await self._order_query.find_by_id(order_id)
            existing_items = await self._order_item_query.find_order_item_by_order(
                order_id
            )
            items_by_id = {item.order_item_id: item for item in existing_items}
            reservation_rows = await self._stock.get_by_order(order_id)
            reservation_qty = {
                int(row.product_id): int(row.quantity) for row in reservation_rows
            }

            compensations: list[Callable[[], Awaitable[None]]] = []

            async def rollback() -> None:
                for compensation in reversed(compensations):
                    await compensation()

            async def fail(err: BaseException) -> NoReturn:
                await rollback()
                raise err

            async def guard[T](coro: Awaitable[T]) -> T:
                try:
                    return await coro
                except Exception as exc:
                    await fail(exc)
                    raise

            for item_index, item in enumerate(request.items):
                if item.quantity <= 0:
                    await fail(
                        err_bad_request.with_message(
                            "order item quantity must be greater than zero"
                        )
                    )

                if item.order_item_id > 0:
                    existing_item = items_by_id.get(item.order_item_id)
                    if existing_item is None:
                        await fail(
                            err_bad_request.with_message(
                                "order item does not belong to order"
                            )
                        )
                    if int(existing_item.product_id) != item.product_id:
                        await fail(
                            err_bad_request.with_message(
                                "changing an order item's product is not supported"
                            )
                        )

                    product = await guard(
                        self._product_query.find_by_id(item.product_id)
                    )
                    delta = int(existing_item.quantity) - item.quantity
                    if delta != 0:
                        operation_id = (
                            f"order-update-{order_id}-item-{item.order_item_id}"
                            f"-from-{existing_item.quantity}-to-{item.quantity}"
                        )
                        await guard(
                            self._product_command.adjust_product_stock(
                                item.product_id, delta, operation_id
                            )
                        )

                    try:
                        await self._stock.update_quantity(
                            order_id, item.product_id, item.quantity
                        )
                    except Exception as exc:
                        if delta != 0:
                            await self._adjust_stock_quiet(
                                item.product_id,
                                -delta,
                                f"order-update-reservation-rollback-{order_id}"
                                f"-item-{item.order_item_id}",
                            )
                        await fail(exc)

                    try:
                        await self._order_item_command.update(
                            UpdateOrderItemRecordRequest(
                                order_item_id=item.order_item_id,
                                order_id=order_id,
                                product_id=item.product_id,
                                quantity=item.quantity,
                                price=int(product.price),
                            )
                        )
                    except Exception as exc:
                        if delta != 0:
                            await self._adjust_stock_quiet(
                                item.product_id,
                                -delta,
                                f"order-update-rollback-{order_id}"
                                f"-item-{item.order_item_id}",
                            )
                        await self._update_reservation_quiet(
                            order_id, item.product_id, int(existing_item.quantity)
                        )
                        await fail(exc)

                    compensations.append(
                        self._compensate_existing_item(
                            order_id=order_id,
                            product_id=item.product_id,
                            order_item_id=item.order_item_id,
                            old_quantity=int(existing_item.quantity),
                            old_price=int(existing_item.price),
                            delta=delta,
                        )
                    )
                    continue

                product = await guard(
                    self._product_query.find_by_id(item.product_id)
                )
                operation_id = (
                    f"order-update-new-{order_id}-index-{item_index}"
                    f"-product-{item.product_id}-quantity-{item.quantity}"
                )
                try:
                    await self._product_command.adjust_product_stock(
                        item.product_id, -item.quantity, operation_id
                    )
                except Exception as exc:
                    await fail(exc)

                try:
                    created_item = await self._order_item_command.create(
                        CreateOrderItemRecordRequest(
                            order_id=order_id,
                            product_id=item.product_id,
                            quantity=item.quantity,
                            price=int(product.price),
                        )
                    )
                except Exception as exc:
                    await self._adjust_stock_quiet(
                        item.product_id,
                        item.quantity,
                        f"order-update-new-rollback-{order_id}"
                        f"-product-{item.product_id}",
                    )
                    await fail(exc)

                compensations.append(
                    self._compensate_new_item(
                        order_id=order_id,
                        product_id=item.product_id,
                        quantity=item.quantity,
                        created_item_id=int(created_item.order_item_id),
                        had_reservation=item.product_id in reservation_qty,
                        old_reservation_quantity=reservation_qty.get(
                            item.product_id, 0
                        ),
                    )
                )
                await guard(
                    self._stock.upsert(order_id, item.product_id, item.quantity)
                )

            if self._shipping_query is None:
                await fail(
                    err_bad_request.with_message(
                        "shipping query dependency is required"
                    )
                )

            previous_shipping = None
            shipping_id: int | None = None
            if (
                request.shipping_address is not None
                and request.shipping_address.shipping_id is not None
            ):
                shipping_id = request.shipping_address.shipping_id
                shipping_res = await guard(
                    self._shipping_query.find_by_id(shipping_id)
                )
                if shipping_res is None:
                    await fail(
                        err_bad_request.with_message("shipping address is required")
                    )
                previous_shipping = shipping_res
            else:
                shipping_res = await guard(
                    self._shipping_query.find_by_order(order_id)
                )
                if shipping_res is None:
                    await fail(
                        err_bad_request.with_message("shipping address is required")
                    )
                shipping_id = int(shipping_res.id)
                previous_shipping = shipping_res

            if int(previous_shipping.order_id) != int(existing_order.order_id):
                await fail(
                    err_bad_request.with_message(
                        "shipping address does not belong to order"
                    )
                )

            shipping_cost = int(previous_shipping.shippingCost)
            if request.shipping_address is not None:
                try:
                    shipping_update = await self._shipping_address.update(
                        UpdateShippingAddressRequest(
                            shipping_id=shipping_id,
                            order_id=int(existing_order.order_id),
                            alamat=request.shipping_address.alamat,
                            provinsi=request.shipping_address.provinsi,
                            kota=request.shipping_address.kota,
                            courier=request.shipping_address.courier,
                            shipping_method=request.shipping_address.shipping_method,
                            shipping_cost=request.shipping_address.shipping_cost,
                            negara=request.shipping_address.negara,
                        )
                    )
                except Exception as exc:
                    await fail(exc)
                if shipping_update is None:
                    await fail(
                        err_bad_request.with_message(
                            "shipping address update returned no data"
                        )
                    )
                shipping_cost = int(shipping_update.shipping_cost)

                compensations.append(
                    self._compensate_shipping(
                        shipping_id=int(shipping_id),
                        order_id=int(previous_shipping.order_id),
                        alamat=previous_shipping.alamat,
                        provinsi=previous_shipping.provinsi,
                        kota=previous_shipping.kota,
                        courier=previous_shipping.courier,
                        shipping_method=previous_shipping.shippingMethod,
                        shipping_cost=int(previous_shipping.shippingCost),
                        negara=previous_shipping.negara,
                    )
                )

            total_price = await guard(
                self._order_item_query.calculate_total_price(order_id)
            )
            try:
                res = await self._order_command.update(
                    UpdateOrderRecordRequest(
                        order_id=order_id,
                        merchant_id=0,
                        user_id=request.user_id,
                        total_price=total_price + shipping_cost,
                    )
                )
            except Exception as exc:
                await fail(exc)

            await self._cache.delete_order_cache(order_id)
            return res

    # ------------------------------------------------------------------- trash

    async def trash(self, order_id: int) -> Order:
        with self._obs.span("order.command.trash", order_id=order_id):
            reservations = await self._stock.get_by_order(order_id)
            released: list[OrderStockReservation] = []

            async def restore_released_stock() -> None:
                for reservation in released:
                    try:
                        await self._product_command.adjust_product_stock(
                            int(reservation.product_id),
                            -int(reservation.quantity),
                            self._reservation_operation_id(
                                "order-trash-rollback", reservation
                            ),
                        )
                    except Exception as exc:
                        self._logger.error(
                            "failed to compensate trashed order stock",
                            error=str(exc),
                            product_id=reservation.product_id,
                        )
                    try:
                        await self._stock.reserve(
                            order_id, int(reservation.product_id)
                        )
                    except Exception as exc:
                        self._logger.error(
                            "failed to compensate trashed order reservation",
                            error=str(exc),
                            product_id=reservation.product_id,
                        )

            for reservation in reservations:
                if reservation.status != "reserved":
                    continue
                try:
                    await self._stock.release(order_id, int(reservation.product_id))
                except NoRowsError:
                    continue
                except Exception as exc:
                    await restore_released_stock()
                    raise exc

                try:
                    await self._product_command.adjust_product_stock(
                        int(reservation.product_id),
                        int(reservation.quantity),
                        self._reservation_operation_id(
                            "order-trash-release", reservation
                        ),
                    )
                except Exception as exc:
                    try:
                        await self._stock.reserve(
                            order_id, int(reservation.product_id)
                        )
                    except Exception as status_exc:
                        self._logger.error(
                            "failed to compensate current trashed order reservation",
                            error=str(status_exc),
                            product_id=reservation.product_id,
                        )
                    await restore_released_stock()
                    raise exc
                released.append(reservation)

            try:
                order = await self._order_command.trash(order_id)
            except Exception as exc:
                await restore_released_stock()
                raise exc

            await self._cache.delete_order_cache(order_id)
            return order

    # ----------------------------------------------------------------- restore

    async def restore(self, order_id: int) -> Order:
        with self._obs.span("order.command.restore", order_id=order_id):
            try:
                reservations = await self._stock.get_by_order(order_id)
            except Exception as exc:
                # re-trashes on a failed reservation read, then reports.
                try:
                    await self._order_command.trash(order_id)
                except Exception:
                    pass
                raise exc

            reserved: list[OrderStockReservation] = []

            async def rollback_reservations() -> None:
                for reservation in reserved:
                    try:
                        await self._product_command.adjust_product_stock(
                            int(reservation.product_id),
                            int(reservation.quantity),
                            self._reservation_operation_id(
                                "order-restore-rollback", reservation
                            ),
                        )
                    except Exception as exc:
                        self._logger.error(
                            "failed to compensate restored stock",
                            error=str(exc),
                            product_id=reservation.product_id,
                        )
                    try:
                        await self._stock.release(
                            order_id, int(reservation.product_id)
                        )
                    except Exception as exc:
                        self._logger.error(
                            "failed to compensate restored reservation",
                            error=str(exc),
                            product_id=reservation.product_id,
                        )

            for reservation in reservations:
                if reservation.status != "released":
                    continue
                try:
                    await self._stock.reserve(order_id, int(reservation.product_id))
                except NoRowsError:
                    continue
                except Exception as exc:
                    await rollback_reservations()
                    raise exc

                try:
                    await self._product_command.adjust_product_stock(
                        int(reservation.product_id),
                        -int(reservation.quantity),
                        self._reservation_operation_id(
                            "order-restore-reserve", reservation
                        ),
                    )
                except Exception as exc:
                    try:
                        await self._stock.release(
                            order_id, int(reservation.product_id)
                        )
                    except Exception as status_exc:
                        self._logger.error(
                            "failed to compensate current restored reservation",
                            error=str(status_exc),
                            product_id=reservation.product_id,
                        )
                    await rollback_reservations()
                    raise exc
                reserved.append(reservation)

            try:
                order = await self._order_command.restore(order_id)
            except Exception as exc:
                await rollback_reservations()
                raise exc

            await self._cache.delete_order_cache(order_id)
            return order

    # -------------------------------------------------------- delete permanent

    async def delete_permanent(self, order_id: int) -> bool:
        with self._obs.span("order.command.delete_permanent", order_id=order_id):
            success = await self._order_command.delete_permanent_with_children(
                order_id
            )
            await self._cache.delete_order_cache(order_id)
            return success

    # ----------------------------------------------------------- bulk restore

    async def restore_all(self) -> bool:
        with self._obs.span("order.command.restore_all"):
            trashed_orders = await self._order_command.find_trashed()
            for trashed_order in trashed_orders:
                try:
                    await self.restore(int(trashed_order.order_id))
                except NoRowsError:
                    # A concurrent restore already claimed this order.
                    continue
                except AppError as exc:
                    if exc.is_(err_order_not_found):
                        continue
                    raise

            await self._cache.invalidate_order_cache()
            return True

    async def delete_all(self) -> bool:
        with self._obs.span("order.command.delete_all"):
            trashed_orders = await self._order_command.find_trashed()
            for trashed_order in trashed_orders:
                await self.delete_permanent(int(trashed_order.order_id))

            await self._cache.invalidate_order_cache()
            return True

    # -------------------------------------------------------------- reconcile

    async def reconcile_stock_reservations(self) -> ReconcileResult:
        with self._obs.span("order.command.reconcile_stock_reservations"):
            re_reserved = 0
            released = 0

            released_on_active = await self._stock.get_released_for_active_orders()
            for reservation in released_on_active:
                order_id = int(reservation.order_id)
                product_id = int(reservation.product_id)
                try:
                    await self._stock.reserve(order_id, product_id)
                except NoRowsError:
                    continue
                except Exception as exc:
                    self._logger.error(
                        "failed to claim reservation during reconciliation",
                        error=str(exc),
                        order_id=order_id,
                        product_id=product_id,
                    )
                    continue
                try:
                    await self._product_command.adjust_product_stock(
                        product_id,
                        -int(reservation.quantity),
                        self._reservation_operation_id(
                            "order-reconcile-reserve", reservation
                        ),
                    )
                except Exception as exc:
                    try:
                        await self._stock.release(order_id, product_id)
                    except Exception:
                        pass
                    self._logger.error(
                        "failed to re-reserve stock during reconciliation",
                        error=str(exc),
                        order_id=order_id,
                        product_id=product_id,
                    )
                    continue
                re_reserved += 1

            reserved_on_trashed = (
                await self._stock.get_reserved_for_trashed_orders()
            )
            for reservation in reserved_on_trashed:
                order_id = int(reservation.order_id)
                product_id = int(reservation.product_id)
                try:
                    await self._stock.release(order_id, product_id)
                except NoRowsError:
                    continue
                except Exception as exc:
                    self._logger.error(
                        "failed to claim release during reconciliation",
                        error=str(exc),
                        order_id=order_id,
                        product_id=product_id,
                    )
                    continue
                try:
                    await self._product_command.adjust_product_stock(
                        product_id,
                        int(reservation.quantity),
                        self._reservation_operation_id(
                            "order-reconcile-release", reservation
                        ),
                    )
                except Exception as exc:
                    try:
                        await self._stock.reserve(order_id, product_id)
                    except Exception:
                        pass
                    self._logger.error(
                        "failed to release stock during reconciliation",
                        error=str(exc),
                        order_id=order_id,
                        product_id=product_id,
                    )
                    continue
                released += 1

            return ReconcileResult(re_reserved=re_reserved, released=released)

    # ---------------------------------------------------------------- cleanup

    async def cleanup_idempotency_records(self, retention_days: int) -> CleanupResult:
        with self._obs.span(
            "order.command.cleanup_idempotency_records",
            retention_days=retention_days,
        ):
            if retention_days <= 0:
                retention_days = 7
            cutoff = datetime.now() - timedelta(days=retention_days)

            released_removed = await self._stock.delete_old_released_reservations(
                cutoff
            )
            adjustments_removed = (
                await self._stock.delete_old_product_stock_adjustments(cutoff)
            )

            return CleanupResult(
                released_reservations_removed=released_removed,
                adjustments_removed=adjustments_removed,
            )

    # ---------------------------------------------------------------- helpers

    @staticmethod
    def _reservation_operation_id(
        prefix: str, reservation: OrderStockReservation
    ) -> str:
        updated = reservation.updated_at
        if updated.tzinfo is None:
            updated = updated.replace(tzinfo=UTC)
        nanos = int(updated.timestamp() * 1_000_000_000)
        return (
            f"{prefix}-order-{reservation.order_id}"
            f"-product-{reservation.product_id}"
            f"-reservation-{reservation.reservation_id}-at-{nanos}"
        )

    async def _adjust_stock_quiet(
        self, product_id: int, delta: int, operation_id: str
    ) -> None:
        try:
            await self._product_command.adjust_product_stock(
                product_id, delta, operation_id
            )
        except Exception:
            pass

    async def _update_reservation_quiet(
        self, order_id: int, product_id: int, quantity: int
    ) -> None:
        try:
            await self._stock.update_quantity(order_id, product_id, quantity)
        except Exception:
            pass

    def _compensate_existing_item(
        self,
        *,
        order_id: int,
        product_id: int,
        order_item_id: int,
        old_quantity: int,
        old_price: int,
        delta: int,
    ) -> Callable[[], Awaitable[None]]:
        async def compensate() -> None:
            try:
                await self._stock.update_quantity(
                    order_id, product_id, old_quantity
                )
            except Exception as exc:
                self._logger.error(
                    "failed to compensate stock reservation update",
                    error=str(exc),
                    product_id=product_id,
                )
            try:
                await self._order_item_command.update(
                    UpdateOrderItemRecordRequest(
                        order_item_id=order_item_id,
                        order_id=order_id,
                        product_id=product_id,
                        quantity=old_quantity,
                        price=old_price,
                    )
                )
            except Exception as exc:
                self._logger.error(
                    "failed to compensate order item update",
                    error=str(exc),
                    order_item_id=order_item_id,
                )
            if delta != 0:
                try:
                    await self._product_command.adjust_product_stock(
                        product_id,
                        -delta,
                        f"order-update-compensate-{order_id}-item-{order_item_id}",
                    )
                except Exception as exc:
                    self._logger.error(
                        "failed to compensate order stock update",
                        error=str(exc),
                        product_id=product_id,
                    )

        return compensate

    def _compensate_new_item(
        self,
        *,
        order_id: int,
        product_id: int,
        quantity: int,
        created_item_id: int,
        had_reservation: bool,
        old_reservation_quantity: int,
    ) -> Callable[[], Awaitable[None]]:
        async def compensate() -> None:
            try:
                if had_reservation:
                    await self._stock.update_quantity(
                        order_id, product_id, old_reservation_quantity
                    )
                else:
                    await self._stock.delete_by_order_product(order_id, product_id)
            except Exception as exc:
                self._logger.error(
                    "failed to restore compensated stock reservation",
                    error=str(exc),
                    product_id=product_id,
                )
            try:
                await self._order_item_command.trash(created_item_id)
            except Exception as exc:
                self._logger.error(
                    "failed to trash compensated order item",
                    error=str(exc),
                    order_item_id=created_item_id,
                )
            else:
                try:
                    await self._order_item_command.delete_permanent(created_item_id)
                except Exception as exc:
                    self._logger.error(
                        "failed to permanently delete compensated order item",
                        error=str(exc),
                        order_item_id=created_item_id,
                    )
            try:
                await self._product_command.adjust_product_stock(
                    product_id,
                    quantity,
                    f"order-update-new-compensate-{order_id}-product-{product_id}",
                )
            except Exception as exc:
                self._logger.error(
                    "failed to compensate new order item stock",
                    error=str(exc),
                    product_id=product_id,
                )

        return compensate

    def _compensate_shipping(
        self,
        *,
        shipping_id: int,
        order_id: int,
        alamat: str,
        provinsi: str,
        kota: str,
        courier: str,
        shipping_method: str,
        shipping_cost: int,
        negara: str,
    ) -> Callable[[], Awaitable[None]]:
        async def compensate() -> None:
            try:
                await self._shipping_address.update(
                    UpdateShippingAddressRequest(
                        shipping_id=shipping_id,
                        order_id=order_id,
                        alamat=alamat,
                        provinsi=provinsi,
                        kota=kota,
                        courier=courier,
                        shipping_method=shipping_method,
                        shipping_cost=shipping_cost,
                        negara=negara,
                    )
                )
            except Exception as exc:
                self._logger.error(
                    "failed to compensate shipping address update",
                    error=str(exc),
                    shipping_id=shipping_id,
                )

        return compensate


__all__ = ["OrderCommandServiceImpl"]

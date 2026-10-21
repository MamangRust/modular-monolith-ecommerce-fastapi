"""order: order_stock_reservations (+ transactions created early, deferred FKs) Revision ID: 20261002_0017 Revises: 20261002_0016 Create Date: 2026-10-02 DDL Matches the expected reference migrations `20250807000000_create_order_stock_reservations.sql` (only the reservation half — `product_stock_adjustments` already exists from the `product` stage) and `20250213033219_create_transactions.sql`. Three gaps are closed here: - `order_stock_reservations` was deferred from the `product` stage (that migration created only `product_stock_adjustments` and noted the reservation table would arrive with the `order` stage); - `transactions` is created **early** because the order `DeleteOrderPermanentlyWithChildren` CTE purges `transactions`, and the `transaction` stage lands after `order`. Same precedent as `orders` being created early in the `order_item` migration; the `transaction` stage reuses it. - the two FKs the `order_item` migration deliberately deferred (`orders.merchant_id -> merchants.merchant_id`, `order_items.product_id -> products.product_id`) are added now that both parent tables exist. Deviations kept consistent with the other domain migrations: timestamps are `TIMESTAMP WITH TIME ZONE` (uses bare `TIMESTAMP`)."""

from __future__ import annotations

from alembic import op

revision = "20261002_0017"
down_revision = "20261002_0016"
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Created early: the order purge CTE deletes from it (see module docstring).
    op.execute(
        """
        CREATE TABLE IF NOT EXISTS transactions (
            transaction_id SERIAL PRIMARY KEY,
            order_id INT NOT NULL REFERENCES orders (order_id),
            merchant_id INT NOT NULL REFERENCES merchants (merchant_id),
            payment_method VARCHAR(50) NOT NULL,
            amount INT NOT NULL,
            payment_status VARCHAR(20) NOT NULL DEFAULT 'completed',
            created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
            deleted_at TIMESTAMP WITH TIME ZONE DEFAULT NULL
        )
        """
    )
    op.execute(
        "CREATE INDEX IF NOT EXISTS idx_transactions_order_id "
        "ON transactions (order_id)"
    )
    op.execute(
        "CREATE INDEX IF NOT EXISTS idx_transactions_merchant_id "
        "ON transactions (merchant_id)"
    )
    op.execute(
        "CREATE INDEX IF NOT EXISTS idx_transactions_payment_status "
        "ON transactions (payment_status)"
    )

    op.execute(
        """
        CREATE TABLE IF NOT EXISTS order_stock_reservations (
            reservation_id SERIAL PRIMARY KEY,
            order_id INT NOT NULL REFERENCES orders (order_id),
            product_id INT NOT NULL REFERENCES products (product_id),
            quantity INT NOT NULL CHECK (quantity > 0),
            status VARCHAR(20) NOT NULL DEFAULT 'reserved'
                CHECK (status IN ('reserved', 'released')),
            created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
            CONSTRAINT uq_order_stock_reservation UNIQUE (order_id, product_id)
        )
        """
    )
    op.execute(
        "CREATE INDEX IF NOT EXISTS idx_order_stock_reservations_order_id "
        "ON order_stock_reservations (order_id)"
    )
    op.execute(
        "CREATE INDEX IF NOT EXISTS idx_order_stock_reservations_status "
        "ON order_stock_reservations (status)"
    )

    # Deferred from the order_item stage (see module docstring).
    op.execute(
        """
        DO $$
        BEGIN
            IF NOT EXISTS (
                SELECT 1 FROM pg_constraint WHERE conname = 'fk_orders_merchant'
            ) THEN
                ALTER TABLE orders
                    ADD CONSTRAINT fk_orders_merchant
                    FOREIGN KEY (merchant_id) REFERENCES merchants (merchant_id);
            END IF;
        END $$;
        """
    )
    op.execute(
        """
        DO $$
        BEGIN
            IF NOT EXISTS (
                SELECT 1 FROM pg_constraint
                WHERE conname = 'fk_order_items_product'
            ) THEN
                ALTER TABLE order_items
                    ADD CONSTRAINT fk_order_items_product
                    FOREIGN KEY (product_id) REFERENCES products (product_id);
            END IF;
        END $$;
        """
    )


def downgrade() -> None:
    op.execute(
        "ALTER TABLE order_items DROP CONSTRAINT IF EXISTS fk_order_items_product"
    )
    op.execute("ALTER TABLE orders DROP CONSTRAINT IF EXISTS fk_orders_merchant")
    op.execute(
        "DROP INDEX IF EXISTS idx_order_stock_reservations_status"
    )
    op.execute(
        "DROP INDEX IF EXISTS idx_order_stock_reservations_order_id"
    )
    op.execute("DROP TABLE IF EXISTS order_stock_reservations")
    op.execute("DROP INDEX IF EXISTS idx_transactions_payment_status")
    op.execute("DROP INDEX IF EXISTS idx_transactions_merchant_id")
    op.execute("DROP INDEX IF EXISTS idx_transactions_order_id")
    op.execute("DROP TABLE IF EXISTS transactions")

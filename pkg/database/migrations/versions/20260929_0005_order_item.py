"""order_item: order_items (+ orders, created early) Revision ID: 20260929_0005 Revises: 20260929_0004 Create Date: 2026-09-29 DDL Matches the expected reference migrations `20250213032912_create_order_items.sql` and (for the parent table) `20250213032628_create_orders.sql`. `orders` is created here, ahead of the `order` stage, for the same reason the foundation migration creates `users` ahead of the user stage: `order_items` carries a foreign key to `orders` and the order_item `DeleteAll` statement reads `orders.deleted_at` directly, so the parent must exist before the leaf can be exercised. Its full column set already matches the DDL. Two foreign keys are deliberately deferred because their parent tables do not exist yet, and will be added by the owning stage: - `orders.merchant_id -> merchants.merchant_id` (arrives with the `merchant` stage); - `order_items.product_id -> products.product_id` (arrives with the `product` stage). The indexes on both tables are created here exactly as declares them."""

from __future__ import annotations

from alembic import op

revision = "20260929_0005"
down_revision = "20260929_0004"
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Parent table, created early (see module docstring). `merchant_id` has no
    # FK yet because `merchants` lands in a later stage.
    op.execute(
        """
        CREATE TABLE IF NOT EXISTS orders (
            order_id SERIAL PRIMARY KEY,
            user_id INT NOT NULL REFERENCES users (user_id),
            merchant_id INT NOT NULL,
            total_price INT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            deleted_at TIMESTAMP DEFAULT NULL
        )
        """
    )
    op.execute("CREATE INDEX IF NOT EXISTS idx_orders_user_id ON orders (user_id)")
    op.execute(
        "CREATE INDEX IF NOT EXISTS idx_orders_merchant_id ON orders (merchant_id)"
    )
    op.execute(
        "CREATE INDEX IF NOT EXISTS idx_orders_total_price ON orders (total_price)"
    )

    # `product_id` has no FK yet because `products` lands in a later stage.
    op.execute(
        """
        CREATE TABLE IF NOT EXISTS order_items (
            order_item_id SERIAL PRIMARY KEY,
            order_id INT NOT NULL REFERENCES orders (order_id),
            product_id INT NOT NULL,
            quantity INT NOT NULL CHECK (quantity > 0),
            price INT NOT NULL CHECK (price >= 0),
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            deleted_at TIMESTAMP DEFAULT NULL
        )
        """
    )
    op.execute(
        "CREATE INDEX IF NOT EXISTS idx_order_items_order_id "
        "ON order_items (order_id)"
    )


def downgrade() -> None:
    op.execute("DROP INDEX IF EXISTS idx_order_items_order_id")
    op.execute("DROP TABLE IF EXISTS order_items")
    op.execute("DROP INDEX IF EXISTS idx_orders_total_price")
    op.execute("DROP INDEX IF EXISTS idx_orders_merchant_id")
    op.execute("DROP INDEX IF EXISTS idx_orders_user_id")
    op.execute("DROP TABLE IF EXISTS orders")

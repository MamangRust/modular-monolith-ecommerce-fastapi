"""cart: carts table Revision ID: 20261002_0015 Revises: 20261002_0014 Create Date: 2026-10-02 DDL Matches the expected reference migration `20250213031705_create_carts.sql`: - `carts` with `user_id`/`product_id` FKs and three indexes (`idx_carts_user_id`/`idx_carts_product_id`/`idx_carts_name`); - `quantity > 0` and `weight >= 0` CHECKs; - `deleted_at` column is present in but never written by any query (the cart repository hard-deletes), so it stays for schema. Deviations kept consistent with the other domain migrations: - timestamps are `TIMESTAMP WITH TIME ZONE` (the SQL uses bare `TIMESTAMP`); - `product_id` gets `ON DELETE CASCADE` (the convention for child rows of a domain entity, matching `product_stock_adjustments`), while the `user_id` FK stays plain like `merchants.user_id`/`orders.user_id`."""

from __future__ import annotations

from alembic import op

revision = "20261002_0015"
down_revision = "20261002_0014"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.execute(
        """
        CREATE TABLE IF NOT EXISTS carts (
            cart_id SERIAL PRIMARY KEY,
            user_id INTEGER NOT NULL REFERENCES users (user_id),
            product_id INTEGER NOT NULL
                REFERENCES products (product_id) ON DELETE CASCADE,
            name VARCHAR(255) NOT NULL,
            price INTEGER NOT NULL,
            image VARCHAR(255) NOT NULL,
            quantity INTEGER NOT NULL CHECK (quantity > 0),
            weight INTEGER NOT NULL CHECK (weight >= 0),
            created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
            deleted_at TIMESTAMP WITH TIME ZONE DEFAULT NULL
        )
        """
    )
    op.execute("CREATE INDEX IF NOT EXISTS idx_carts_user_id ON carts (user_id)")
    op.execute("CREATE INDEX IF NOT EXISTS idx_carts_product_id ON carts (product_id)")
    op.execute("CREATE INDEX IF NOT EXISTS idx_carts_name ON carts (name)")


def downgrade() -> None:
    op.execute("DROP INDEX IF EXISTS idx_carts_name")
    op.execute("DROP INDEX IF EXISTS idx_carts_product_id")
    op.execute("DROP INDEX IF EXISTS idx_carts_user_id")
    op.execute("DROP TABLE IF EXISTS carts")

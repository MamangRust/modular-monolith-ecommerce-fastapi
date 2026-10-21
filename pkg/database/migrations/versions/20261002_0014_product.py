"""product: products + product_stock_adjustments Revision ID: 20261002_0014 Revises: 20261002_0013 Create Date: 2026-10-02 DDL Matches the expected reference migrations: - `20250213031451_create_products.sql` — the `products` table plus its five indexes; - `20250807000000_create_order_stock_reservations.sql` — the `product_stock_adjustments` table (used by `AdjustProductStock` for idempotent stock deltas). DELIBERATE SPLIT: the migration bundles `product_stock_adjustments` and `order_stock_reservations` in one file. creates only `product_stock_adjustments` here; `order_stock_reservations` belongs to the `order_item` domain and lands in its stage (T12'), keeping the one-domain-per-migration convention and the leaf-first ordering. Deviations kept consistent with the other domain migrations: - timestamps are `TIMESTAMP WITH TIME ZONE` (the SQL uses bare `TIMESTAMP`); - the FKs keep their `ON DELETE CASCADE` where has adopted it."""

from __future__ import annotations

from alembic import op

revision = "20261002_0014"
down_revision = "20261002_0013"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.execute(
        """
        CREATE TABLE IF NOT EXISTS products (
            product_id SERIAL PRIMARY KEY,
            merchant_id INTEGER NOT NULL
                REFERENCES merchants (merchant_id) ON DELETE CASCADE,
            category_id INTEGER NOT NULL
                REFERENCES categories (category_id) ON DELETE CASCADE,
            name VARCHAR(255) NOT NULL,
            description TEXT,
            price INTEGER NOT NULL CHECK (price >= 0),
            count_in_stock INTEGER NOT NULL DEFAULT 0 CHECK (count_in_stock >= 0),
            brand VARCHAR(100),
            weight INTEGER,
            rating FLOAT DEFAULT 0.0 NULL,
            slug_product VARCHAR(100) UNIQUE,
            image_product TEXT,
            created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
            deleted_at TIMESTAMP WITH TIME ZONE DEFAULT NULL
        )
        """
    )
    op.execute(
        "CREATE INDEX IF NOT EXISTS idx_products_merchant_id ON products (merchant_id)"
    )
    op.execute(
        "CREATE INDEX IF NOT EXISTS idx_products_category_id ON products (category_id)"
    )
    op.execute(
        "CREATE INDEX IF NOT EXISTS idx_products_slug ON products (slug_product)"
    )
    op.execute("CREATE INDEX IF NOT EXISTS idx_products_price ON products (price)")
    op.execute(
        "CREATE INDEX IF NOT EXISTS idx_products_created_at ON products (created_at)"
    )

    op.execute(
        """
        CREATE TABLE IF NOT EXISTS product_stock_adjustments (
            operation_id VARCHAR(255) PRIMARY KEY,
            product_id INTEGER NOT NULL
                REFERENCES products (product_id) ON DELETE CASCADE,
            delta INTEGER NOT NULL CHECK (delta <> 0),
            created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
        )
        """
    )
    op.execute(
        "CREATE INDEX IF NOT EXISTS idx_product_stock_adjustments_product_id "
        "ON product_stock_adjustments (product_id)"
    )


def downgrade() -> None:
    op.execute("DROP INDEX IF EXISTS idx_product_stock_adjustments_product_id")
    op.execute("DROP TABLE IF EXISTS product_stock_adjustments")
    op.execute("DROP INDEX IF EXISTS idx_products_created_at")
    op.execute("DROP INDEX IF EXISTS idx_products_price")
    op.execute("DROP INDEX IF EXISTS idx_products_slug")
    op.execute("DROP INDEX IF EXISTS idx_products_category_id")
    op.execute("DROP INDEX IF EXISTS idx_products_merchant_id")
    op.execute("DROP TABLE IF EXISTS products")

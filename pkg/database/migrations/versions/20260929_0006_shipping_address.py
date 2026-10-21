"""shipping_address: shipping_addresses

Revision ID: 20260929_0006
Revises: 20260929_0005
Create Date: 2026-09-29

DDL Matches the expected reference migration
`20250213033046_create_shipping_address.sql` verbatim: the table plus its five
indexes. `shipping_cost` is `DECIMAL(10,2)`.

`order_id` references `orders`, which the previous revision
(`20260929_0005_order_item`) created ahead of the `order` stage, so the
foreign key can be declared here."""

from __future__ import annotations

from alembic import op

revision = "20260929_0006"
down_revision = "20260929_0005"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.execute(
        """
        CREATE TABLE IF NOT EXISTS shipping_addresses (
            shipping_address_id SERIAL PRIMARY KEY,
            order_id INT NOT NULL REFERENCES orders (order_id),
            alamat TEXT NOT NULL,
            provinsi VARCHAR(255) NOT NULL,
            negara VARCHAR(255) NOT NULL,
            kota VARCHAR(255) NOT NULL,
            courier VARCHAR(100) NOT NULL,
            shipping_method VARCHAR(255) NOT NULL,
            shipping_cost DECIMAL(10,2) NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            deleted_at TIMESTAMP DEFAULT NULL
        )
        """
    )
    op.execute(
        "CREATE INDEX IF NOT EXISTS idx_shipping_addresses_order_id "
        "ON shipping_addresses (order_id)"
    )
    op.execute(
        "CREATE INDEX IF NOT EXISTS idx_shipping_addresses_provinsi "
        "ON shipping_addresses (provinsi)"
    )
    op.execute(
        "CREATE INDEX IF NOT EXISTS idx_shipping_addresses_negara "
        "ON shipping_addresses (negara)"
    )
    op.execute(
        "CREATE INDEX IF NOT EXISTS idx_shipping_addresses_kota "
        "ON shipping_addresses (kota)"
    )
    op.execute(
        "CREATE INDEX IF NOT EXISTS idx_shipping_addresses_method "
        "ON shipping_addresses (shipping_method)"
    )


def downgrade() -> None:
    op.execute("DROP INDEX IF EXISTS idx_shipping_addresses_method")
    op.execute("DROP INDEX IF EXISTS idx_shipping_addresses_kota")
    op.execute("DROP INDEX IF EXISTS idx_shipping_addresses_negara")
    op.execute("DROP INDEX IF EXISTS idx_shipping_addresses_provinsi")
    op.execute("DROP INDEX IF EXISTS idx_shipping_addresses_order_id")
    op.execute("DROP TABLE IF EXISTS shipping_addresses")

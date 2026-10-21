"""merchant_business: merchant_business_information Revision ID: 20261002_0012 Revises: 20261002_0011 Create Date: 2026-10-02 DDL Matches the expected reference migration (`20250213033314_create_merchant_bussiness_information.sql`): the table plus its single index. Deviations from the DDL, kept consistent with the other domain migrations: - timestamps are `TIMESTAMP WITH TIME ZONE` (the SQL uses bare `TIMESTAMP`); - the FK keeps its `ON DELETE CASCADE` (`merchant_id` -> `merchants`)."""

from __future__ import annotations

from alembic import op

revision = "20261002_0012"
down_revision = "20261002_0011"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.execute(
        """
        CREATE TABLE IF NOT EXISTS merchant_business_information (
            merchant_business_info_id SERIAL PRIMARY KEY,
            merchant_id INTEGER NOT NULL
                REFERENCES merchants (merchant_id) ON DELETE CASCADE,
            business_type VARCHAR(100),
            tax_id VARCHAR(50),
            established_year INTEGER,
            number_of_employees INTEGER,
            website_url VARCHAR(255),
            created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
            deleted_at TIMESTAMP WITH TIME ZONE DEFAULT NULL
        )
        """
    )
    op.execute(
        "CREATE INDEX IF NOT EXISTS idx_merchant_business_info_merchant_id "
        "ON merchant_business_information (merchant_id)"
    )


def downgrade() -> None:
    op.execute("DROP INDEX IF EXISTS idx_merchant_business_info_merchant_id")
    op.execute("DROP TABLE IF EXISTS merchant_business_information")

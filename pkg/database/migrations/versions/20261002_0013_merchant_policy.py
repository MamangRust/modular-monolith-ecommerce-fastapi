"""merchant_policy: merchant_policies Revision ID: 20261002_0013 Revises: 20261002_0012 Create Date: 2026-10-02 DDL Matches the expected reference migration (`20250213033316_create_merchant_policy.sql`): the table plus its two indexes. Deviations from the DDL, kept consistent with the other domain migrations: - timestamps are `TIMESTAMP WITH TIME ZONE` (the SQL uses bare `TIMESTAMP`); - the FK keeps its `ON DELETE CASCADE` (`merchant_id` -> `merchants`)."""

from __future__ import annotations

from alembic import op

revision = "20261002_0013"
down_revision = "20261002_0012"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.execute(
        """
        CREATE TABLE IF NOT EXISTS merchant_policies (
            merchant_policy_id SERIAL PRIMARY KEY,
            merchant_id INTEGER NOT NULL
                REFERENCES merchants (merchant_id) ON DELETE CASCADE,
            policy_type VARCHAR(100) NOT NULL,
            title VARCHAR(255) NOT NULL,
            description TEXT NOT NULL,
            created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
            deleted_at TIMESTAMP WITH TIME ZONE DEFAULT NULL
        )
        """
    )
    op.execute(
        "CREATE INDEX IF NOT EXISTS idx_policies_merchant_id "
        "ON merchant_policies (merchant_id)"
    )
    op.execute(
        "CREATE INDEX IF NOT EXISTS idx_policies_policy_type "
        "ON merchant_policies (policy_type)"
    )


def downgrade() -> None:
    op.execute("DROP INDEX IF EXISTS idx_policies_policy_type")
    op.execute("DROP INDEX IF EXISTS idx_policies_merchant_id")
    op.execute("DROP TABLE IF EXISTS merchant_policies")

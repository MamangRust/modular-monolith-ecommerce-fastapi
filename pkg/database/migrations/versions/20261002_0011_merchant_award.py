"""merchant_award: merchant_certifications_and_awards Revision ID: 20261002_0011 Revises: 20261001_0010 Create Date: 2026-10-02 DDL Matches the expected reference migration (`20250213033315_create_merchant_certification_awards.sql`): the table plus its two indexes. Deviations from the DDL, kept consistent with the other domain migrations: - timestamps are `TIMESTAMP WITH TIME ZONE` (the SQL uses bare `TIMESTAMP`); - `issue_date`/`expiry_date` stay plain `DATE` (uses `DATE` too), because the handler formats them as date-only strings; - the FK keeps its `ON DELETE CASCADE` (`merchant_id` -> `merchants`)."""

from __future__ import annotations

from alembic import op

revision = "20261002_0011"
down_revision = "20261001_0010"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.execute(
        """
        CREATE TABLE IF NOT EXISTS merchant_certifications_and_awards (
            merchant_certification_id SERIAL PRIMARY KEY,
            merchant_id INTEGER NOT NULL
                REFERENCES merchants (merchant_id) ON DELETE CASCADE,
            title VARCHAR(255) NOT NULL,
            description TEXT,
            issued_by VARCHAR(255),
            issue_date DATE,
            expiry_date DATE,
            certificate_url VARCHAR(255),
            created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
            deleted_at TIMESTAMP WITH TIME ZONE DEFAULT NULL
        )
        """
    )
    op.execute(
        "CREATE INDEX IF NOT EXISTS idx_certifications_merchant_id "
        "ON merchant_certifications_and_awards (merchant_id)"
    )
    op.execute(
        "CREATE INDEX IF NOT EXISTS idx_certifications_issue_date "
        "ON merchant_certifications_and_awards (issue_date)"
    )


def downgrade() -> None:
    op.execute("DROP INDEX IF EXISTS idx_certifications_issue_date")
    op.execute("DROP INDEX IF EXISTS idx_certifications_merchant_id")
    op.execute("DROP TABLE IF EXISTS merchant_certifications_and_awards")

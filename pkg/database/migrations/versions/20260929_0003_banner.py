"""banner: banners

Revision ID: 20260929_0003
Revises: 20260819_0002
Create Date: 2026-09-29

DDL Matches the expected reference migration
(`20250213033318_create_banner.sql`): the table plus its five indexes,
including the two partial indexes. Date/time range constraints are kept
verbatim."""

from __future__ import annotations

from alembic import op

revision = "20260929_0003"
down_revision = "20260819_0002"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.execute(
        """
        CREATE TABLE IF NOT EXISTS banners (
            banner_id SERIAL PRIMARY KEY,
            name VARCHAR(255) NOT NULL,
            start_date DATE NOT NULL,
            end_date DATE NOT NULL,
            start_time TIME NOT NULL,
            end_time TIME NOT NULL,
            is_active BOOLEAN DEFAULT TRUE,
            created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
            deleted_at TIMESTAMP WITH TIME ZONE NULL,
            CONSTRAINT valid_date_range CHECK (
                end_date IS NULL OR
                start_date IS NULL OR
                end_date >= start_date
            ),
            CONSTRAINT valid_time_range CHECK (
                end_time IS NULL OR
                start_time IS NULL OR
                end_time > start_time
            )
        )
        """
    )
    op.execute(
        "CREATE INDEX IF NOT EXISTS idx_banners_active "
        "ON banners (is_active) WHERE deleted_at IS NULL"
    )
    op.execute(
        "CREATE INDEX IF NOT EXISTS idx_banners_date_range "
        "ON banners (start_date, end_date)"
    )
    op.execute(
        "CREATE INDEX IF NOT EXISTS idx_banners_time_range "
        "ON banners (start_time, end_time)"
    )
    op.execute(
        "CREATE INDEX IF NOT EXISTS idx_banners_created_at ON banners (created_at)"
    )
    op.execute(
        "CREATE INDEX IF NOT EXISTS idx_banners_deleted_at "
        "ON banners (deleted_at) WHERE deleted_at IS NOT NULL"
    )


def downgrade() -> None:
    op.execute("DROP INDEX IF EXISTS idx_banners_deleted_at")
    op.execute("DROP INDEX IF EXISTS idx_banners_created_at")
    op.execute("DROP INDEX IF EXISTS idx_banners_time_range")
    op.execute("DROP INDEX IF EXISTS idx_banners_date_range")
    op.execute("DROP INDEX IF EXISTS idx_banners_active")
    op.execute("DROP TABLE IF EXISTS banners")

"""slider: sliders

Revision ID: 20260929_0007
Revises: 20260929_0006
Create Date: 2026-09-29

DDL Matches the expected reference migration
(`20250213032318_create_sliders.sql`): the table plus its single name index."""

from __future__ import annotations

from alembic import op

revision = "20260929_0007"
down_revision = "20260929_0006"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.execute(
        """
        CREATE TABLE IF NOT EXISTS sliders (
            slider_id SERIAL PRIMARY KEY,
            name VARCHAR(255) NOT NULL,
            image VARCHAR(255) NOT NULL,
            created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
            deleted_at TIMESTAMP WITH TIME ZONE NULL
        )
        """
    )
    op.execute(
        "CREATE INDEX IF NOT EXISTS idx_sliders_name ON sliders (name)"
    )


def downgrade() -> None:
    op.execute("DROP INDEX IF EXISTS idx_sliders_name")
    op.execute("DROP TABLE IF EXISTS sliders")

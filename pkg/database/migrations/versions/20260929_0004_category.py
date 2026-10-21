"""category: categories Revision ID: 20260929_0004 Revises: 20260929_0003 Create Date: 2026-09-29 DDL Matches the expected reference migration (`20250213031222_create_categories.sql`): the table plus its two indexes. `slug_category` keeps its UNIQUE constraint (used by the seeder for idempotency). Timestamps are plain `TIMESTAMP` in the source, so they are kept without a time zone."""

from __future__ import annotations

from alembic import op

revision = "20260929_0004"
down_revision = "20260929_0003"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.execute(
        """
        CREATE TABLE IF NOT EXISTS categories (
            category_id SERIAL PRIMARY KEY,
            name VARCHAR(100) NOT NULL,
            description TEXT,
            slug_category VARCHAR(100) UNIQUE,
            image_category TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            deleted_at TIMESTAMP DEFAULT NULL
        )
        """
    )
    op.execute(
        "CREATE INDEX IF NOT EXISTS idx_categories_slug "
        "ON categories (slug_category)"
    )
    op.execute(
        "CREATE INDEX IF NOT EXISTS idx_categories_created_at "
        "ON categories (created_at)"
    )


def downgrade() -> None:
    op.execute("DROP INDEX IF EXISTS idx_categories_created_at")
    op.execute("DROP INDEX IF EXISTS idx_categories_slug")
    op.execute("DROP TABLE IF EXISTS categories")

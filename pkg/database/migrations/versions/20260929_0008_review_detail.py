"""review_detail: review_details Revision ID: 20260929_0008 Revises: 20260929_0007 Create Date: 2026-09-29 DDL Matches the expected reference migration (`20250213033317_create_review_details.sql`): the table plus its review_id index. NOTE: the migration declares a FK `review_id REFERENCES reviews(review_id) ON DELETE CASCADE`. The `reviews` table is not yet (the `review` domain is a later stage), so this code deliberately omits the FK to keep the migration applicable now. Revisit when `reviews` lands."""

from __future__ import annotations

from alembic import op

revision = "20260929_0008"
down_revision = "20260929_0007"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.execute(
        """
        CREATE TABLE IF NOT EXISTS review_details (
            review_detail_id SERIAL PRIMARY KEY,
            review_id INTEGER NOT NULL,
            type VARCHAR(20) NOT NULL CHECK (type IN ('photo', 'video')),
            url TEXT NOT NULL,
            caption TEXT,
            created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
            deleted_at TIMESTAMP WITH TIME ZONE NULL
        )
        """
    )
    op.execute(
        "CREATE INDEX IF NOT EXISTS idx_review_details_review_id "
        "ON review_details (review_id)"
    )


def downgrade() -> None:
    op.execute("DROP INDEX IF EXISTS idx_review_details_review_id")
    op.execute("DROP TABLE IF EXISTS review_details")

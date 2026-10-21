"""merchant_detail: merchant_details + merchant_social_media_links Revision ID: 20261001_0010 Revises: 20260929_0009 Create Date: 2026-10-01 DDL two reference migrations (`20250213033319_create_merchant_detail.sql` and `20250213033320_create_merchant_social_link.sql`): both tables plus their indexes, created in one revision because the merchant_detail service owns both (`merchant_social_media_links` is hosted by the same process — note #5). Deviations from the DDL, kept consistent with the other domain migrations: - timestamps are `TIMESTAMP WITH TIME ZONE` (the SQL uses bare `TIMESTAMP`; standardised on timestamptz for domain tables); - FKs keep their `ON DELETE CASCADE` (`merchant_details.merchant_id` -> `merchants`, `merchant_social_media_links.merchant_detail_id` -> `merchant_details`)."""

from __future__ import annotations

from alembic import op

revision = "20261001_0010"
down_revision = "20260929_0009"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.execute(
        """
        CREATE TABLE IF NOT EXISTS merchant_details (
            merchant_detail_id SERIAL PRIMARY KEY,
            merchant_id INTEGER NOT NULL
                REFERENCES merchants (merchant_id) ON DELETE CASCADE,
            display_name VARCHAR(255),
            cover_image_url VARCHAR(255),
            logo_url VARCHAR(255),
            short_description TEXT,
            website_url VARCHAR(255),
            created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
            deleted_at TIMESTAMP WITH TIME ZONE DEFAULT NULL
        )
        """
    )
    op.execute(
        "CREATE INDEX IF NOT EXISTS idx_merchant_details_merchant "
        "ON merchant_details (merchant_id)"
    )

    op.execute(
        """
        CREATE TABLE IF NOT EXISTS merchant_social_media_links (
            merchant_social_id SERIAL PRIMARY KEY,
            merchant_detail_id INTEGER NOT NULL
                REFERENCES merchant_details (merchant_detail_id)
                ON DELETE CASCADE,
            platform VARCHAR(100) NOT NULL,
            url TEXT NOT NULL,
            created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
            deleted_at TIMESTAMP WITH TIME ZONE DEFAULT NULL
        )
        """
    )
    op.execute(
        "CREATE INDEX IF NOT EXISTS "
        "idx_merchant_social_media_links_merchant_detail_id "
        "ON merchant_social_media_links (merchant_detail_id)"
    )


def downgrade() -> None:
    op.execute(
        "DROP INDEX IF EXISTS "
        "idx_merchant_social_media_links_merchant_detail_id"
    )
    op.execute("DROP TABLE IF EXISTS merchant_social_media_links")

    op.execute("DROP INDEX IF EXISTS idx_merchant_details_merchant")
    op.execute("DROP TABLE IF EXISTS merchant_details")

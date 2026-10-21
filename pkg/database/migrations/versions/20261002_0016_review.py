"""review: reviews table (+ the deferred review_details FK) Revision ID: 20261002_0016 Revises: 20261002_0015 Create Date: 2026-10-02 DDL Matches the expected reference migration `20250213033313_create_reviews.sql`: - `reviews` with `user_id`/`product_id` FKs and three indexes (`idx_reviews_user_id`/`idx_reviews_product_id`/`idx_reviews_rating`); - `name VARCHAR(255) NOT NULL`, `comment TEXT NOT NULL`, `rating INT NOT NULL`, `deleted_at` nullable. It also closes the gap left by the `review_detail` stage: that migration deliberately omitted the FK `review_id REFERENCES reviews(review_id) ON DELETE CASCADE` because `reviews` did not exist yet ("revisit when `reviews` lands"). Now it does, so the constraint is added here — the DDL matches and a permanently deleted review cascades to its details. Deviations kept consistent with the other domain migrations: - timestamps are `TIMESTAMP WITH TIME ZONE` (the SQL uses bare `TIMESTAMP`); - `product_id` gets `ON DELETE CASCADE` (the convention for a child row of a domain entity, matching `carts.product_id`/`product_stock_adjustments`), while the `user_id` FK stays plain like `carts.user_id`."""

from __future__ import annotations

from alembic import op

revision = "20261002_0016"
down_revision = "20261002_0015"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.execute(
        """
        CREATE TABLE IF NOT EXISTS reviews (
            review_id SERIAL PRIMARY KEY,
            user_id INTEGER NOT NULL REFERENCES users (user_id),
            product_id INTEGER NOT NULL
                REFERENCES products (product_id) ON DELETE CASCADE,
            name VARCHAR(255) NOT NULL,
            comment TEXT NOT NULL,
            rating INTEGER NOT NULL,
            created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
            deleted_at TIMESTAMP WITH TIME ZONE DEFAULT NULL
        )
        """
    )
    op.execute("CREATE INDEX IF NOT EXISTS idx_reviews_user_id ON reviews (user_id)")
    op.execute(
        "CREATE INDEX IF NOT EXISTS idx_reviews_product_id ON reviews (product_id)"
    )
    op.execute("CREATE INDEX IF NOT EXISTS idx_reviews_rating ON reviews (rating)")

    # Deferred from the review_detail stage (see the module docstring).
    op.execute(
        """
        DO $$
        BEGIN
            IF NOT EXISTS (
                SELECT 1 FROM pg_constraint
                WHERE conname = 'fk_review_details_review'
            ) THEN
                ALTER TABLE review_details
                    ADD CONSTRAINT fk_review_details_review
                    FOREIGN KEY (review_id) REFERENCES reviews (review_id)
                    ON DELETE CASCADE;
            END IF;
        END $$;
        """
    )


def downgrade() -> None:
    op.execute(
        "ALTER TABLE review_details DROP CONSTRAINT IF EXISTS fk_review_details_review"
    )
    op.execute("DROP INDEX IF EXISTS idx_reviews_rating")
    op.execute("DROP INDEX IF EXISTS idx_reviews_product_id")
    op.execute("DROP INDEX IF EXISTS idx_reviews_user_id")
    op.execute("DROP TABLE IF EXISTS reviews")

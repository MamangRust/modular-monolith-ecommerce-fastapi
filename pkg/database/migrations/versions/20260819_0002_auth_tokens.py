"""auth: reset_tokens, refresh_tokens Revision ID: 20260819_0002 Revises: 20260818_0001 Create Date: 2026-08-19 DDL Matches the expected reference migrations (`20240205133624_create_reset_token`, `20241231194859_create_refreshtoken`). Both tables reference `users(user_id)` created by the foundation revision and cascade on delete. Column names/types follow the SQL verbatim — note the two tables use different id column names (`id` vs `refresh_token_id`) and the reset-token table has no `created_at`/`updated_at`/`deleted_at`."""

from __future__ import annotations

from alembic import op

revision = "20260819_0002"
down_revision = "20260818_0001"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.execute(
        """
        CREATE TABLE IF NOT EXISTS reset_tokens (
            id SERIAL PRIMARY KEY,
            user_id BIGINT NOT NULL UNIQUE REFERENCES users (user_id) ON DELETE CASCADE,
            token TEXT NOT NULL UNIQUE,
            expiry_date TIMESTAMP NOT NULL
        )
        """
    )
    op.execute(
        "CREATE INDEX IF NOT EXISTS idx_reset_token_token ON reset_tokens (token)"
    )
    op.execute(
        "CREATE INDEX IF NOT EXISTS idx_reset_token_user_id ON reset_tokens (user_id)"
    )

    op.execute(
        """
        CREATE TABLE IF NOT EXISTS refresh_tokens (
            refresh_token_id SERIAL PRIMARY KEY,
            user_id INT NOT NULL REFERENCES users (user_id) ON DELETE CASCADE,
            token VARCHAR(255) NOT NULL UNIQUE,
            expiration TIMESTAMP NOT NULL,
            created_at TIMESTAMP DEFAULT current_timestamp,
            updated_at TIMESTAMP DEFAULT current_timestamp,
            deleted_at TIMESTAMP DEFAULT NULL
        )
        """
    )
    op.execute(
        "CREATE INDEX IF NOT EXISTS idx_refresh_tokens_user_id ON refresh_tokens (user_id)"
    )
    op.execute(
        "CREATE INDEX IF NOT EXISTS idx_refresh_tokens_token ON refresh_tokens (token)"
    )
    op.execute(
        "CREATE INDEX IF NOT EXISTS idx_refresh_tokens_expiration ON refresh_tokens (expiration)"
    )


def downgrade() -> None:
    op.execute("DROP INDEX IF EXISTS idx_refresh_tokens_expiration")
    op.execute("DROP INDEX IF EXISTS idx_refresh_tokens_token")
    op.execute("DROP INDEX IF EXISTS idx_refresh_tokens_user_id")
    op.execute("DROP TABLE IF EXISTS refresh_tokens")

    op.execute("DROP INDEX IF EXISTS idx_reset_token_user_id")
    op.execute("DROP INDEX IF EXISTS idx_reset_token_token")
    op.execute("DROP TABLE IF EXISTS reset_tokens")

"""foundation: roles, users, user_roles, outbox_events, consumer_inbox

Revision ID: 20260818_0001
Revises:
Create Date: 2026-08-18

DDL Matches the expected reference migrations (`20241231190107_create_role`,
`20240205133622_create_users`, `20241231190118_create_user_role`,
`20260806010000_create_outbox_and_consumer_inbox`,
`20260811000000_add_outbox_inbox_fencing`).

The `users` / `user_roles` tables are created here only because `roles`
needs the FK and the role query-by-user path needs the join; the user
domain's own columns arrive with the user service stage."""

from __future__ import annotations

from alembic import op

revision = "20260818_0001"
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.execute(
        """
        CREATE TABLE IF NOT EXISTS roles (
            role_id SERIAL PRIMARY KEY,
            role_name VARCHAR(50) UNIQUE NOT NULL,
            created_at TIMESTAMP DEFAULT current_timestamp,
            updated_at TIMESTAMP DEFAULT current_timestamp,
            deleted_at TIMESTAMP NULL
        )
        """
    )
    op.execute("CREATE INDEX IF NOT EXISTS idx_roles_role_name ON roles (role_name)")
    op.execute("CREATE INDEX IF NOT EXISTS idx_roles_created_at ON roles (created_at)")
    op.execute("CREATE INDEX IF NOT EXISTS idx_roles_updated_at ON roles (updated_at)")

    op.execute(
        """
        CREATE TABLE IF NOT EXISTS users (
            user_id SERIAL PRIMARY KEY,
            firstname VARCHAR(100) NOT NULL,
            lastname VARCHAR(100) NOT NULL,
            email VARCHAR(100) UNIQUE NOT NULL,
            password VARCHAR(100) NOT NULL,
            verification_code VARCHAR(100) NOT NULL,
            is_verified BOOLEAN DEFAULT false,
            created_at TIMESTAMP DEFAULT current_timestamp,
            updated_at TIMESTAMP DEFAULT current_timestamp,
            deleted_at TIMESTAMP NULL
        )
        """
    )
    op.execute("CREATE INDEX IF NOT EXISTS idx_users_email ON users (email)")
    op.execute("CREATE INDEX IF NOT EXISTS idx_users_firstname ON users (firstname)")
    op.execute("CREATE INDEX IF NOT EXISTS idx_users_lastname ON users (lastname)")
    op.execute(
        "CREATE INDEX IF NOT EXISTS idx_users_firstname_lastname ON users (firstname, lastname)"
    )
    op.execute("CREATE INDEX IF NOT EXISTS idx_users_created_at ON users (created_at)")

    op.execute(
        """
        CREATE TABLE IF NOT EXISTS user_roles (
            user_role_id SERIAL PRIMARY KEY,
            user_id INT NOT NULL REFERENCES users (user_id) ON DELETE CASCADE,
            role_id INT NOT NULL REFERENCES roles (role_id) ON DELETE CASCADE,
            created_at TIMESTAMP DEFAULT current_timestamp,
            updated_at TIMESTAMP DEFAULT current_timestamp,
            deleted_at TIMESTAMP NULL
        )
        """
    )
    op.execute("CREATE INDEX IF NOT EXISTS idx_user_roles_user_id ON user_roles (user_id)")
    op.execute("CREATE INDEX IF NOT EXISTS idx_user_roles_role_id ON user_roles (role_id)")
    op.execute(
        "CREATE INDEX IF NOT EXISTS idx_user_roles_user_id_role_id ON user_roles (user_id, role_id)"
    )
    op.execute("CREATE INDEX IF NOT EXISTS idx_user_roles_created_at ON user_roles (created_at)")
    op.execute("CREATE INDEX IF NOT EXISTS idx_user_roles_updated_at ON user_roles (updated_at)")

    op.execute(
        """
        CREATE TABLE IF NOT EXISTS outbox_events (
            id BIGSERIAL PRIMARY KEY,
            event_key VARCHAR(128) NOT NULL,
            topic VARCHAR(255) NOT NULL,
            message_key VARCHAR(255) NOT NULL DEFAULT '',
            payload JSONB NOT NULL,
            status VARCHAR(16) NOT NULL DEFAULT 'pending'
                CHECK (status IN ('pending', 'publishing', 'published', 'failed')),
            attempts INTEGER NOT NULL DEFAULT 0 CHECK (attempts >= 0),
            next_attempt_at TIMESTAMPTZ NOT NULL DEFAULT current_timestamp,
            last_error TEXT NOT NULL DEFAULT '',
            created_at TIMESTAMPTZ NOT NULL DEFAULT current_timestamp,
            updated_at TIMESTAMPTZ NOT NULL DEFAULT current_timestamp,
            published_at TIMESTAMPTZ NULL,
            claim_version BIGINT NOT NULL DEFAULT 0,
            CONSTRAINT outbox_events_event_key_unique UNIQUE (event_key)
        )
        """
    )
    op.execute(
        """
        CREATE INDEX IF NOT EXISTS idx_outbox_events_pending
        ON outbox_events (next_attempt_at, id) WHERE status = 'pending'
        """
    )
    op.execute(
        """
        CREATE INDEX IF NOT EXISTS idx_outbox_events_stale_publishing
        ON outbox_events (updated_at, id) WHERE status = 'publishing'
        """
    )

    op.execute(
        """
        CREATE TABLE IF NOT EXISTS consumer_inbox (
            consumer_name VARCHAR(128) NOT NULL,
            event_key VARCHAR(255) NOT NULL,
            topic VARCHAR(255) NOT NULL DEFAULT '',
            partition_id INTEGER NOT NULL DEFAULT -1,
            message_offset BIGINT NOT NULL DEFAULT -1,
            status VARCHAR(16) NOT NULL DEFAULT 'processing'
                CHECK (status IN ('processing', 'processed', 'pending')),
            attempts INTEGER NOT NULL DEFAULT 1 CHECK (attempts >= 0),
            reservation_version BIGINT NOT NULL DEFAULT 0,
            lease_until TIMESTAMPTZ NOT NULL DEFAULT current_timestamp + interval '1 minute',
            last_error TEXT NOT NULL DEFAULT '',
            processed_at TIMESTAMPTZ NULL,
            PRIMARY KEY (consumer_name, event_key)
        )
        """
    )
    op.execute(
        """
        CREATE INDEX IF NOT EXISTS idx_consumer_inbox_lease
        ON consumer_inbox (status, lease_until)
        """
    )


def downgrade() -> None:
    op.execute("DROP TABLE IF EXISTS consumer_inbox")
    op.execute("DROP TABLE IF EXISTS outbox_events")
    op.execute("DROP TABLE IF EXISTS user_roles")
    op.execute("DROP TABLE IF EXISTS users")
    op.execute("DROP TABLE IF EXISTS roles")

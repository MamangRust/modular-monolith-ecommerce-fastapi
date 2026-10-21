"""merchant: merchants + merchant_documents Revision ID: 20260929_0009 Revises: 20260929_0008 Create Date: 2026-09-29 DDL two reference migrations (`20250213031139_create_merchants.sql` and `20250213031140_create_merchant_documents.sql`): both tables plus their indexes, created in one revision because the merchant service owns both. Deviations from the DDL, kept consistent with the other domain migrations: - timestamps are `TIMESTAMP WITH TIME ZONE` (the SQL uses bare `TIMESTAMP`; standardised on timestamptz for domain tables); - `merchants.user_id` keeps its `REFERENCES users(user_id)` FK (the users table is), and `merchant_documents.merchant_id` its `ON DELETE CASCADE` FK to `merchants`."""

from __future__ import annotations

from alembic import op

revision = "20260929_0009"
down_revision = "20260929_0008"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.execute(
        """
        CREATE TABLE IF NOT EXISTS merchants (
            merchant_id SERIAL PRIMARY KEY,
            user_id INTEGER NOT NULL REFERENCES users (user_id),
            name VARCHAR(255) NOT NULL,
            description TEXT,
            address TEXT,
            contact_email VARCHAR(100),
            contact_phone VARCHAR(20),
            status VARCHAR(20) NOT NULL DEFAULT 'active',
            created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
            deleted_at TIMESTAMP WITH TIME ZONE DEFAULT NULL
        )
        """
    )
    op.execute("CREATE INDEX IF NOT EXISTS idx_merchants_user_id ON merchants (user_id)")
    op.execute("CREATE INDEX IF NOT EXISTS idx_merchants_status ON merchants (status)")
    op.execute(
        "CREATE INDEX IF NOT EXISTS idx_merchants_created_at ON merchants (created_at)"
    )

    op.execute(
        """
        CREATE TABLE IF NOT EXISTS merchant_documents (
            document_id SERIAL PRIMARY KEY,
            merchant_id INTEGER NOT NULL
                REFERENCES merchants (merchant_id) ON DELETE CASCADE,
            document_type VARCHAR(50) NOT NULL,
            document_url TEXT NOT NULL,
            status VARCHAR(20) NOT NULL DEFAULT 'pending',
            note TEXT DEFAULT NULL,
            uploaded_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
            created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
            deleted_at TIMESTAMP WITH TIME ZONE DEFAULT NULL
        )
        """
    )
    op.execute(
        "CREATE INDEX IF NOT EXISTS idx_merchant_documents_merchant_id "
        "ON merchant_documents (merchant_id)"
    )
    op.execute(
        "CREATE INDEX IF NOT EXISTS idx_merchant_documents_document_type "
        "ON merchant_documents (document_type)"
    )
    op.execute(
        "CREATE INDEX IF NOT EXISTS idx_merchant_documents_status "
        "ON merchant_documents (status)"
    )
    op.execute(
        "CREATE INDEX IF NOT EXISTS idx_merchant_documents_merchant_type "
        "ON merchant_documents (merchant_id, document_type)"
    )


def downgrade() -> None:
    op.execute("DROP INDEX IF EXISTS idx_merchant_documents_merchant_type")
    op.execute("DROP INDEX IF EXISTS idx_merchant_documents_status")
    op.execute("DROP INDEX IF EXISTS idx_merchant_documents_document_type")
    op.execute("DROP INDEX IF EXISTS idx_merchant_documents_merchant_id")
    op.execute("DROP TABLE IF EXISTS merchant_documents")

    op.execute("DROP INDEX IF EXISTS idx_merchants_created_at")
    op.execute("DROP INDEX IF EXISTS idx_merchants_status")
    op.execute("DROP INDEX IF EXISTS idx_merchants_user_id")
    op.execute("DROP TABLE IF EXISTS merchants")

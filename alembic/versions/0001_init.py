"""Initial tables."""

from __future__ import annotations

import sqlalchemy as sa
from alembic import op  # type: ignore[attr-defined]

revision = "0001"
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "accounts",
        sa.Column("id", sa.dialects.postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("username", sa.String, unique=True, nullable=False),
        sa.Column("ig_pk", sa.String),
        sa.Column("name", sa.String),
        sa.Column("category", sa.String),
        sa.Column("bio", sa.Text),
        sa.Column("website", sa.String),
        sa.Column("metrics_json", sa.dialects.postgresql.JSONB),
        sa.Column("profile_pic_url", sa.String),
        sa.Column("is_professional", sa.Boolean),
        sa.Column("last_post_at", sa.DateTime(timezone=True)),
        sa.Column("source", sa.String),
        sa.Column("source_details", sa.dialects.postgresql.JSONB),
        sa.Column("status", sa.String),
        sa.Column(
            "created_at", sa.DateTime(timezone=True), server_default=sa.func.now()
        ),
        sa.Column(
            "updated_at", sa.DateTime(timezone=True), server_default=sa.func.now()
        ),
    )
    op.create_table(
        "leads",
        sa.Column("id", sa.dialects.postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column(
            "account_id",
            sa.dialects.postgresql.UUID(as_uuid=True),
            sa.ForeignKey("accounts.id"),
        ),
        sa.Column("confidence", sa.Numeric(3, 2)),
        sa.Column("reason", sa.Text),
        sa.Column("tags", sa.JSON),
        sa.Column("stage", sa.String, server_default="NEW"),
        sa.Column("notes", sa.Text),
        sa.Column(
            "created_at", sa.DateTime(timezone=True), server_default=sa.func.now()
        ),
        sa.Column(
            "updated_at", sa.DateTime(timezone=True), server_default=sa.func.now()
        ),
    )
    op.create_check_constraint(
        "leads_stage_check", "leads", "stage IN ('NEW','VETTED','REJECTED','CONTACTED')"
    )
    op.create_table(
        "media",
        sa.Column("id", sa.dialects.postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column(
            "account_id",
            sa.dialects.postgresql.UUID(as_uuid=True),
            sa.ForeignKey("accounts.id"),
        ),
        sa.Column("ig_media_id", sa.String, nullable=False),
        sa.Column("caption", sa.Text),
        sa.Column("media_type", sa.String),
        sa.Column("permalink", sa.String),
        sa.Column("taken_at", sa.DateTime(timezone=True)),
    )
    op.create_unique_constraint(
        "media_account_media_id", "media", ["account_id", "ig_media_id"]
    )
    op.create_table(
        "jobs",
        sa.Column("id", sa.dialects.postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("type", sa.String),
        sa.Column("payload_json", sa.dialects.postgresql.JSONB),
        sa.Column("status", sa.String),
        sa.Column("attempts", sa.Integer, server_default="0"),
        sa.Column("error", sa.Text),
        sa.Column("scheduled_for", sa.DateTime(timezone=True)),
        sa.Column(
            "created_at", sa.DateTime(timezone=True), server_default=sa.func.now()
        ),
        sa.Column(
            "updated_at", sa.DateTime(timezone=True), server_default=sa.func.now()
        ),
    )
    op.create_table(
        "audit",
        sa.Column("id", sa.dialects.postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("action", sa.String),
        sa.Column("entity", sa.String),
        sa.Column("entity_id", sa.String),
        sa.Column("payload_json", sa.dialects.postgresql.JSONB),
        sa.Column(
            "created_at", sa.DateTime(timezone=True), server_default=sa.func.now()
        ),
    )


def downgrade() -> None:
    op.drop_table("audit")
    op.drop_table("jobs")
    op.drop_constraint("media_account_media_id", "media", type_="unique")
    op.drop_table("media")
    op.drop_constraint("leads_stage_check", "leads", type_="check")
    op.drop_table("leads")
    op.drop_table("accounts")

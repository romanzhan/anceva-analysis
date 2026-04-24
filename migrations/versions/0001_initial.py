"""Initial schema — все таблицы MVP.

Revision ID: 0001_initial
Revises:
Create Date: 2026-04-24

"""
from __future__ import annotations

from collections.abc import Sequence

import sqlalchemy as sa

from alembic import op

revision: str = "0001_initial"
down_revision: str | None = None
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    # ---------------- admins -------------------------------------------------
    op.create_table(
        "admins",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("tg_user_id", sa.BigInteger(), nullable=False),
        sa.Column("tg_username", sa.String(64), nullable=True),
        sa.Column("name", sa.String(128), nullable=False),
        sa.Column("role", sa.String(16), nullable=False, server_default="admin"),
        sa.Column("active", sa.Boolean(), nullable=False, server_default=sa.true()),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.UniqueConstraint("tg_user_id", name="uq_admins_tg_user_id"),
    )
    op.create_index("ix_admins_tg_user_id", "admins", ["tg_user_id"])

    # ---------------- specialists --------------------------------------------
    op.create_table(
        "specialists",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("name", sa.String(128), nullable=False),
        sa.Column("title", sa.String(128), nullable=True),
        sa.Column("language", sa.String(8), nullable=False, server_default="ru"),
        sa.Column("directions", sa.JSON(), nullable=False, server_default="[]"),
        sa.Column("timetable", sa.JSON(), nullable=False, server_default="{}"),
        sa.Column("active", sa.Boolean(), nullable=False, server_default=sa.true()),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
    )

    # ---------------- clients ------------------------------------------------
    op.create_table(
        "clients",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("tg_user_id", sa.BigInteger(), nullable=False),
        sa.Column("tg_username", sa.String(64), nullable=True),
        sa.Column("phone", sa.String(32), nullable=True),
        sa.Column("name", sa.String(128), nullable=True),
        sa.Column("state", sa.String(32), nullable=False, server_default="new"),
        sa.Column("source", sa.String(32), nullable=False, server_default="unknown"),
        sa.Column("locale", sa.String(8), nullable=False, server_default="ru"),
        sa.Column("referrer_client_id", sa.Integer(), nullable=True),
        sa.Column("pd_consent_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("pd_consent_version", sa.String(16), nullable=True),
        sa.Column("last_seen_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.ForeignKeyConstraint(["referrer_client_id"], ["clients.id"], ondelete="SET NULL"),
        sa.UniqueConstraint("tg_user_id", name="uq_clients_tg_user_id"),
    )
    op.create_index("ix_clients_tg_user_id", "clients", ["tg_user_id"])
    op.create_index("ix_clients_phone", "clients", ["phone"])
    op.create_index("ix_clients_state", "clients", ["state"])
    op.create_index("ix_clients_last_seen_at", "clients", ["last_seen_at"])
    op.create_index("ix_clients_state_last_seen", "clients", ["state", "last_seen_at"])

    # ---------------- children -----------------------------------------------
    op.create_table(
        "children",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("client_id", sa.Integer(), nullable=False),
        sa.Column("full_name", sa.String(256), nullable=True),
        sa.Column("dob", sa.Date(), nullable=True),
        sa.Column("gender", sa.String(1), nullable=True),
        sa.Column("home_language", sa.String(8), nullable=False, server_default="ru"),
        sa.Column("main_direction", sa.String(32), nullable=True),
        sa.Column("assigned_specialist_id", sa.Integer(), nullable=True),
        sa.Column("notes", sa.String(2000), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.ForeignKeyConstraint(["client_id"], ["clients.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["assigned_specialist_id"], ["specialists.id"], ondelete="SET NULL"),
    )
    op.create_index("ix_children_client_id", "children", ["client_id"])
    op.create_index("ix_children_dob", "children", ["dob"])
    op.create_index("ix_children_main_direction", "children", ["main_direction"])

    # ---------------- anketas ------------------------------------------------
    op.create_table(
        "anketas",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("child_id", sa.Integer(), nullable=False),
        sa.Column("answers", sa.JSON(), nullable=False, server_default="{}"),
        sa.Column("video_refs", sa.JSON(), nullable=False, server_default="[]"),
        sa.Column("doc_refs", sa.JSON(), nullable=False, server_default="[]"),
        sa.Column("filled_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.ForeignKeyConstraint(["child_id"], ["children.id"], ondelete="CASCADE"),
        sa.UniqueConstraint("child_id", name="uq_anketas_child_id"),
    )
    op.create_index("ix_anketas_child_id", "anketas", ["child_id"])

    # ---------------- dialogs ------------------------------------------------
    op.create_table(
        "dialogs",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("client_id", sa.Integer(), nullable=False),
        sa.Column("mode", sa.String(8), nullable=False, server_default="bot"),
        sa.Column("current_stage", sa.String(32), nullable=False, server_default="greeting"),
        sa.Column("taken_by_admin_id", sa.Integer(), nullable=True),
        sa.Column("taken_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("facts", sa.JSON(), nullable=False, server_default="{}"),
        sa.Column("started_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("last_activity_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.ForeignKeyConstraint(["client_id"], ["clients.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["taken_by_admin_id"], ["admins.id"], ondelete="SET NULL"),
    )
    op.create_index("ix_dialogs_client_id", "dialogs", ["client_id"])
    op.create_index("ix_dialogs_mode", "dialogs", ["mode"])
    op.create_index("ix_dialogs_current_stage", "dialogs", ["current_stage"])
    op.create_index("ix_dialogs_last_activity_at", "dialogs", ["last_activity_at"])

    # ---------------- messages -----------------------------------------------
    op.create_table(
        "messages",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("dialog_id", sa.Integer(), nullable=False),
        sa.Column("direction", sa.String(8), nullable=False),
        sa.Column("sender", sa.String(16), nullable=False),
        sa.Column("type", sa.String(16), nullable=False, server_default="text"),
        sa.Column("tg_message_id", sa.BigInteger(), nullable=True),
        sa.Column("content", sa.Text(), nullable=True),
        sa.Column("media_file_id", sa.String(256), nullable=True),
        sa.Column("media_transcript", sa.Text(), nullable=True),
        sa.Column("extracted", sa.JSON(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.ForeignKeyConstraint(["dialog_id"], ["dialogs.id"], ondelete="CASCADE"),
    )
    op.create_index("ix_messages_dialog_id", "messages", ["dialog_id"])
    op.create_index("ix_messages_created_at", "messages", ["created_at"])

    # ---------------- diagnostics --------------------------------------------
    op.create_table(
        "diagnostics",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("child_id", sa.Integer(), nullable=False),
        sa.Column("specialist_id", sa.Integer(), nullable=True),
        sa.Column("direction", sa.String(32), nullable=False),
        sa.Column("scheduled_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("status", sa.String(16), nullable=False, server_default="booked"),
        sa.Column("price", sa.Numeric(10, 2), nullable=False),
        sa.Column("payment_status", sa.String(16), nullable=False, server_default="invoiced"),
        sa.Column("transfer_count", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("anketa_received", sa.Boolean(), nullable=False, server_default=sa.false()),
        sa.Column("videos_received", sa.Boolean(), nullable=False, server_default=sa.false()),
        sa.Column("result_note", sa.Text(), nullable=True),
        sa.Column("room", sa.String(16), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.ForeignKeyConstraint(["child_id"], ["children.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["specialist_id"], ["specialists.id"], ondelete="SET NULL"),
    )
    op.create_index("ix_diagnostics_child_id", "diagnostics", ["child_id"])
    op.create_index("ix_diagnostics_scheduled_at", "diagnostics", ["scheduled_at"])
    op.create_index("ix_diagnostics_status", "diagnostics", ["status"])

    # ---------------- lessons ------------------------------------------------
    op.create_table(
        "lessons",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("child_id", sa.Integer(), nullable=False),
        sa.Column("specialist_id", sa.Integer(), nullable=True),
        sa.Column("scheduled_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("duration_min", sa.Integer(), nullable=False, server_default="30"),
        sa.Column("room", sa.String(16), nullable=True),
        sa.Column("price", sa.Numeric(10, 2), nullable=False),
        sa.Column("status", sa.String(24), nullable=False, server_default="planned"),
        sa.Column("rescheduled_to_id", sa.Integer(), nullable=True),
        sa.Column("notified_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.ForeignKeyConstraint(["child_id"], ["children.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["specialist_id"], ["specialists.id"], ondelete="SET NULL"),
        sa.ForeignKeyConstraint(["rescheduled_to_id"], ["lessons.id"], ondelete="SET NULL"),
    )
    op.create_index("ix_lessons_child_id", "lessons", ["child_id"])
    op.create_index("ix_lessons_scheduled_at", "lessons", ["scheduled_at"])
    op.create_index("ix_lessons_status", "lessons", ["status"])

    # ---------------- payments -----------------------------------------------
    op.create_table(
        "payments",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("client_id", sa.Integer(), nullable=False),
        sa.Column("child_id", sa.Integer(), nullable=True),
        sa.Column("period", sa.String(7), nullable=True),
        sa.Column("amount", sa.Numeric(10, 2), nullable=False),
        sa.Column("method", sa.String(16), nullable=False, server_default="cash"),
        sa.Column("status", sa.String(16), nullable=False, server_default="draft"),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column("kaspi_check_file_id", sa.String(256), nullable=True),
        sa.Column("invoiced_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("paid_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.ForeignKeyConstraint(["client_id"], ["clients.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["child_id"], ["children.id"], ondelete="SET NULL"),
    )
    op.create_index("ix_payments_client_id", "payments", ["client_id"])
    op.create_index("ix_payments_period", "payments", ["period"])
    op.create_index("ix_payments_status", "payments", ["status"])

    # ---------------- tasks --------------------------------------------------
    op.create_table(
        "tasks",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("client_id", sa.Integer(), nullable=True),
        sa.Column("kind", sa.String(32), nullable=False),
        sa.Column("status", sa.String(16), nullable=False, server_default="pending"),
        sa.Column("fire_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("payload", sa.JSON(), nullable=False, server_default="{}"),
        sa.Column("done_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("error", sa.Text(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.ForeignKeyConstraint(["client_id"], ["clients.id"], ondelete="CASCADE"),
    )
    op.create_index("ix_tasks_client_id", "tasks", ["client_id"])
    op.create_index("ix_tasks_kind", "tasks", ["kind"])
    op.create_index("ix_tasks_status", "tasks", ["status"])
    op.create_index("ix_tasks_fire_at", "tasks", ["fire_at"])

    # ---------------- templates ----------------------------------------------
    op.create_table(
        "templates",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("slug", sa.String(64), nullable=False),
        sa.Column("title", sa.String(128), nullable=False),
        sa.Column("category", sa.String(64), nullable=False),
        sa.Column("body", sa.Text(), nullable=False),
        sa.Column("placeholders", sa.JSON(), nullable=False, server_default="[]"),
        sa.Column("version", sa.Integer(), nullable=False, server_default="1"),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.UniqueConstraint("slug", name="uq_templates_slug"),
    )
    op.create_index("ix_templates_slug", "templates", ["slug"])
    op.create_index("ix_templates_category", "templates", ["category"])

    # ---------------- broadcasts ---------------------------------------------
    op.create_table(
        "broadcasts",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("title", sa.String(256), nullable=False),
        sa.Column("body", sa.Text(), nullable=False),
        sa.Column("segment_filter", sa.JSON(), nullable=False, server_default="{}"),
        sa.Column("created_by_admin_id", sa.Integer(), nullable=True),
        sa.Column("scheduled_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("sent_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("stats", sa.JSON(), nullable=False, server_default="{}"),
        sa.Column("status", sa.String(16), nullable=False, server_default="draft"),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.ForeignKeyConstraint(["created_by_admin_id"], ["admins.id"], ondelete="SET NULL"),
    )

    # ---------------- audit_log ----------------------------------------------
    op.create_table(
        "audit_log",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("admin_id", sa.Integer(), nullable=True),
        sa.Column("action", sa.String(64), nullable=False),
        sa.Column("target_type", sa.String(32), nullable=True),
        sa.Column("target_id", sa.Integer(), nullable=True),
        sa.Column("payload", sa.JSON(), nullable=False, server_default="{}"),
        sa.Column("at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.ForeignKeyConstraint(["admin_id"], ["admins.id"], ondelete="SET NULL"),
    )
    op.create_index("ix_audit_log_admin_id", "audit_log", ["admin_id"])
    op.create_index("ix_audit_log_action", "audit_log", ["action"])
    op.create_index("ix_audit_log_at", "audit_log", ["at"])


def downgrade() -> None:
    for t in [
        "audit_log", "broadcasts", "templates", "tasks",
        "payments", "lessons", "diagnostics", "messages",
        "dialogs", "anketas", "children", "clients",
        "specialists", "admins",
    ]:
        op.drop_table(t)

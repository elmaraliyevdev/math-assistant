"""Simulation collaboration tables.

Revision ID: 20260618_0007
Revises: 20260617_0006
Create Date: 2026-06-18 10:00:00.000000
"""

from __future__ import annotations

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

revision: str = "20260618_0007"
down_revision: str | Sequence[str] | None = "20260617_0006"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.add_column(
        "simulations",
        sa.Column(
            "workflow_status",
            sa.Enum(
                "draft",
                "under_review",
                "approved",
                "certification_ready",
                "released",
                name="simulation_workflow_status",
                native_enum=False,
            ),
            nullable=False,
            server_default="draft",
        ),
    )

    op.create_table(
        "simulation_reviews",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("simulation_id", sa.Uuid(), nullable=False),
        sa.Column("reviewer_id", sa.Uuid(), nullable=False),
        sa.Column(
            "status",
            sa.Enum(
                "pending",
                "approved",
                "rejected",
                "changes_requested",
                name="simulation_review_status",
                native_enum=False,
            ),
            nullable=False,
        ),
        sa.Column("decision_reason", sa.Text(), nullable=True),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.ForeignKeyConstraint(["reviewer_id"], ["users.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["simulation_id"], ["simulations.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_simulation_reviews_simulation_id", "simulation_reviews", ["simulation_id"])
    op.create_index("ix_simulation_reviews_reviewer_id", "simulation_reviews", ["reviewer_id"])

    op.create_table(
        "simulation_comments",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("simulation_id", sa.Uuid(), nullable=False),
        sa.Column("user_id", sa.Uuid(), nullable=False),
        sa.Column("content", sa.Text(), nullable=False),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.ForeignKeyConstraint(["simulation_id"], ["simulations.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_simulation_comments_simulation_id", "simulation_comments", ["simulation_id"])
    op.create_index("ix_simulation_comments_user_id", "simulation_comments", ["user_id"])

    op.create_table(
        "simulation_approvals",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("simulation_id", sa.Uuid(), nullable=False),
        sa.Column("approved_by", sa.Uuid(), nullable=False),
        sa.Column(
            "approval_stage",
            sa.Enum(
                "mathematician",
                "senior_mathematician",
                "product_owner",
                "producer",
                name="simulation_approval_stage",
                native_enum=False,
            ),
            nullable=False,
        ),
        sa.Column("approved_at", sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(["approved_by"], ["users.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["simulation_id"], ["simulations.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_simulation_approvals_simulation_id", "simulation_approvals", ["simulation_id"])
    op.create_index("ix_simulation_approvals_approved_by", "simulation_approvals", ["approved_by"])

    op.create_table(
        "simulation_activity_log",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("simulation_id", sa.Uuid(), nullable=False),
        sa.Column("actor_id", sa.Uuid(), nullable=False),
        sa.Column("action", sa.String(length=128), nullable=False),
        sa.Column("metadata", sa.JSON(), nullable=True),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.ForeignKeyConstraint(["actor_id"], ["users.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["simulation_id"], ["simulations.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(
        "ix_simulation_activity_log_simulation_id",
        "simulation_activity_log",
        ["simulation_id"],
    )
    op.create_index("ix_simulation_activity_log_actor_id", "simulation_activity_log", ["actor_id"])


def downgrade() -> None:
    op.drop_index("ix_simulation_activity_log_actor_id", table_name="simulation_activity_log")
    op.drop_index("ix_simulation_activity_log_simulation_id", table_name="simulation_activity_log")
    op.drop_table("simulation_activity_log")
    op.drop_index("ix_simulation_approvals_approved_by", table_name="simulation_approvals")
    op.drop_index("ix_simulation_approvals_simulation_id", table_name="simulation_approvals")
    op.drop_table("simulation_approvals")
    op.drop_index("ix_simulation_comments_user_id", table_name="simulation_comments")
    op.drop_index("ix_simulation_comments_simulation_id", table_name="simulation_comments")
    op.drop_table("simulation_comments")
    op.drop_index("ix_simulation_reviews_reviewer_id", table_name="simulation_reviews")
    op.drop_index("ix_simulation_reviews_simulation_id", table_name="simulation_reviews")
    op.drop_table("simulation_reviews")
    op.drop_column("simulations", "workflow_status")

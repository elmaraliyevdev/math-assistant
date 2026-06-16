"""Auth and organization schema.

Revision ID: 20260615_0004
Revises: 20260614_0003
Create Date: 2026-06-15 10:00:00.000000
"""

from __future__ import annotations

import uuid
from collections.abc import Sequence
from datetime import UTC, datetime

import sqlalchemy as sa
from alembic import op

revision: str = "20260615_0004"
down_revision: str | Sequence[str] | None = "20260614_0003"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None

organization_role = sa.Enum(
    "owner",
    "admin",
    "developer",
    "viewer",
    name="organization_role",
    native_enum=False,
)


def upgrade() -> None:
    op.create_table(
        "organizations",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("name", sa.String(length=255), nullable=False),
        sa.Column("slug", sa.String(length=255), nullable=False),
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
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("slug", name="uq_organizations_slug"),
    )
    op.create_table(
        "users",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("email", sa.String(length=255), nullable=False),
        sa.Column("password_hash", sa.Text(), nullable=False),
        sa.Column("full_name", sa.String(length=255), nullable=False),
        sa.Column("is_active", sa.Boolean(), nullable=False, server_default=sa.true()),
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
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("email", name="uq_users_email"),
    )
    organization_role.create(op.get_bind(), checkfirst=True)
    op.create_table(
        "organization_members",
        sa.Column("organization_id", sa.Uuid(), nullable=False),
        sa.Column("user_id", sa.Uuid(), nullable=False),
        sa.Column("role", organization_role, nullable=False),
        sa.ForeignKeyConstraint(
            ["organization_id"],
            ["organizations.id"],
            ondelete="CASCADE",
        ),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("organization_id", "user_id"),
        sa.UniqueConstraint(
            "organization_id",
            "user_id",
            name="uq_organization_members_org_user",
        ),
    )
    op.create_table(
        "refresh_tokens",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("user_id", sa.Uuid(), nullable=False),
        sa.Column("jti", sa.String(length=64), nullable=False),
        sa.Column("expires_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("revoked_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("jti", name="uq_refresh_tokens_jti"),
    )
    op.create_index(
        op.f("ix_refresh_tokens_user_id"),
        "refresh_tokens",
        ["user_id"],
        unique=False,
    )

    op.add_column(
        "games",
        sa.Column("organization_id", sa.Uuid(), nullable=True),
    )

    personal_org_id = uuid.uuid4()
    now = datetime.now(tz=UTC)
    op.execute(
        sa.text(
            "INSERT INTO organizations (id, name, slug, created_at, updated_at) "
            "VALUES (:id, :name, :slug, :created_at, :updated_at)",
        ).bindparams(
            id=personal_org_id,
            name="Personal Workspace",
            slug="personal-workspace",
            created_at=now,
            updated_at=now,
        ),
    )
    op.execute(
        sa.text(
            "UPDATE games SET organization_id = :org_id WHERE organization_id IS NULL",
        ).bindparams(org_id=personal_org_id),
    )

    op.alter_column("games", "organization_id", nullable=False)
    op.create_index(
        op.f("ix_games_organization_id"),
        "games",
        ["organization_id"],
        unique=False,
    )
    op.create_foreign_key(
        "fk_games_organization_id_organizations",
        "games",
        "organizations",
        ["organization_id"],
        ["id"],
        ondelete="CASCADE",
    )


def downgrade() -> None:
    op.drop_constraint(
        "fk_games_organization_id_organizations",
        "games",
        type_="foreignkey",
    )
    op.drop_index(op.f("ix_games_organization_id"), table_name="games")
    op.drop_column("games", "organization_id")
    op.drop_index(op.f("ix_refresh_tokens_user_id"), table_name="refresh_tokens")
    op.drop_table("refresh_tokens")
    op.drop_table("organization_members")
    op.drop_table("users")
    op.drop_table("organizations")
    organization_role.drop(op.get_bind(), checkfirst=True)

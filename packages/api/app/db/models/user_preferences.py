"""User preferences ORM model."""

from __future__ import annotations

import uuid
from typing import TYPE_CHECKING

from sqlalchemy import Boolean, ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base, TimestampMixin

if TYPE_CHECKING:
    from app.db.models.user import User


class UserPreferences(Base, TimestampMixin):
    __tablename__ = "user_preferences"

    user_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"),
        primary_key=True,
    )
    theme: Mapped[str] = mapped_column(String(16), nullable=False, default="system")
    notify_simulation_completed: Mapped[bool] = mapped_column(
        Boolean,
        nullable=False,
        default=True,
    )
    notify_simulation_failed: Mapped[bool] = mapped_column(
        Boolean,
        nullable=False,
        default=True,
    )
    notify_validation_failed: Mapped[bool] = mapped_column(
        Boolean,
        nullable=False,
        default=True,
    )
    notify_organization_invitation: Mapped[bool] = mapped_column(
        Boolean,
        nullable=False,
        default=True,
    )

    user: Mapped[User] = relationship()

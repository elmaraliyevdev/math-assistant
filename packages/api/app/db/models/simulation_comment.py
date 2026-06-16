"""Simulation collaboration comment ORM model."""

from __future__ import annotations

import uuid
from typing import TYPE_CHECKING

from sqlalchemy import ForeignKey, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base, CreatedAtMixin, UUIDPrimaryKeyMixin

if TYPE_CHECKING:
    from app.db.models.simulation import Simulation
    from app.db.models.user import User


class SimulationComment(Base, UUIDPrimaryKeyMixin, CreatedAtMixin):
    __tablename__ = "simulation_comments"

    simulation_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("simulations.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    user_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    content: Mapped[str] = mapped_column(Text, nullable=False)

    simulation: Mapped[Simulation] = relationship(back_populates="comments")
    user: Mapped[User] = relationship()

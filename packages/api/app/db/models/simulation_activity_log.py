"""Simulation activity log ORM model."""

from __future__ import annotations

import uuid
from typing import TYPE_CHECKING, Any

from sqlalchemy import ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base, CreatedAtMixin, JsonDocument, UUIDPrimaryKeyMixin

if TYPE_CHECKING:
    from app.db.models.simulation import Simulation
    from app.db.models.user import User


class SimulationActivityLog(Base, UUIDPrimaryKeyMixin, CreatedAtMixin):
    __tablename__ = "simulation_activity_log"

    simulation_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("simulations.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    actor_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    action: Mapped[str] = mapped_column(String(128), nullable=False)
    metadata_json: Mapped[dict[str, Any] | None] = mapped_column(
        "metadata",
        JsonDocument,
        nullable=True,
    )

    simulation: Mapped[Simulation] = relationship(back_populates="activity_logs")
    actor: Mapped[User] = relationship()

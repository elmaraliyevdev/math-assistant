"""Simulation review ORM model."""

from __future__ import annotations

import uuid
from typing import TYPE_CHECKING

from sqlalchemy import Enum, ForeignKey, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base, TimestampMixin, UUIDPrimaryKeyMixin
from app.db.models.simulation_workflow import ReviewStatus

if TYPE_CHECKING:
    from app.db.models.simulation import Simulation
    from app.db.models.user import User


class SimulationReview(Base, UUIDPrimaryKeyMixin, TimestampMixin):
    __tablename__ = "simulation_reviews"

    simulation_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("simulations.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    reviewer_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    status: Mapped[ReviewStatus] = mapped_column(
        Enum(
            ReviewStatus,
            name="simulation_review_status",
            values_callable=lambda enum_cls: [member.value for member in enum_cls],
            native_enum=False,
        ),
        nullable=False,
        default=ReviewStatus.PENDING,
    )
    decision_reason: Mapped[str | None] = mapped_column(Text, nullable=True)

    simulation: Mapped[Simulation] = relationship(back_populates="reviews")
    reviewer: Mapped[User] = relationship()

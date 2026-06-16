"""Simulation approval ORM model."""

from __future__ import annotations

import uuid
from datetime import datetime
from typing import TYPE_CHECKING

from sqlalchemy import DateTime, Enum, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base, UUIDPrimaryKeyMixin
from app.db.models.simulation_workflow import ApprovalStage

if TYPE_CHECKING:
    from app.db.models.simulation import Simulation
    from app.db.models.user import User


class SimulationApproval(Base, UUIDPrimaryKeyMixin):
    __tablename__ = "simulation_approvals"

    simulation_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("simulations.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    approved_by: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    approval_stage: Mapped[ApprovalStage] = mapped_column(
        Enum(
            ApprovalStage,
            name="simulation_approval_stage",
            values_callable=lambda enum_cls: [member.value for member in enum_cls],
            native_enum=False,
        ),
        nullable=False,
    )
    approved_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
    )

    simulation: Mapped[Simulation] = relationship(back_populates="approvals")
    approver: Mapped[User] = relationship()

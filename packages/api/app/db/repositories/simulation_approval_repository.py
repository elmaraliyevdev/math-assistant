"""Simulation approval repository."""

from __future__ import annotations

import uuid

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.models.simulation_approval import SimulationApproval
from app.db.models.simulation_workflow import ApprovalStage
from app.db.repositories.base import BaseRepository


class SimulationApprovalRepository(BaseRepository[SimulationApproval]):
    def __init__(self, session: AsyncSession) -> None:
        super().__init__(session, SimulationApproval)

    async def list_by_simulation_id(
        self,
        simulation_id: uuid.UUID,
    ) -> list[SimulationApproval]:
        result = await self._session.scalars(
            select(SimulationApproval)
            .where(SimulationApproval.simulation_id == simulation_id)
            .order_by(SimulationApproval.approved_at.asc()),
        )
        return list(result.all())

    async def get_by_stage(
        self,
        simulation_id: uuid.UUID,
        stage: ApprovalStage,
    ) -> SimulationApproval | None:
        result = await self._session.scalars(
            select(SimulationApproval).where(
                SimulationApproval.simulation_id == simulation_id,
                SimulationApproval.approval_stage == stage,
            ),
        )
        return result.first()

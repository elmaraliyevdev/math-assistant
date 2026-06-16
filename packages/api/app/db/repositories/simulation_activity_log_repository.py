"""Simulation activity log repository."""

from __future__ import annotations

import uuid

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.models.simulation_activity_log import SimulationActivityLog
from app.db.repositories.base import BaseRepository


class SimulationActivityLogRepository(BaseRepository[SimulationActivityLog]):
    def __init__(self, session: AsyncSession) -> None:
        super().__init__(session, SimulationActivityLog)

    async def add(self, entity: SimulationActivityLog) -> SimulationActivityLog:
        self._session.add(entity)
        await self._session.flush()
        return entity

    async def list_by_simulation_id(
        self,
        simulation_id: uuid.UUID,
    ) -> list[SimulationActivityLog]:
        result = await self._session.scalars(
            select(SimulationActivityLog)
            .where(SimulationActivityLog.simulation_id == simulation_id)
            .order_by(SimulationActivityLog.created_at.desc()),
        )
        return list(result.all())

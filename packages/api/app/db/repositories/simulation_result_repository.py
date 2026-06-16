"""SimulationResult repository."""

from __future__ import annotations

import uuid

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.models.simulation_result import SimulationResult
from app.db.repositories.base import BaseRepository


class SimulationResultRepository(BaseRepository[SimulationResult]):
    def __init__(self, session: AsyncSession) -> None:
        super().__init__(session, SimulationResult)

    async def get_by_simulation_id(
        self,
        simulation_id: uuid.UUID,
    ) -> SimulationResult | None:
        result = await self._session.scalars(
            select(SimulationResult).where(
                SimulationResult.simulation_id == simulation_id,
            ),
        )
        return result.first()

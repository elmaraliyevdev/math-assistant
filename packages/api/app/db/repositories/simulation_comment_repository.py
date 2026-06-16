"""Simulation comment repository."""

from __future__ import annotations

import uuid

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.models.simulation_comment import SimulationComment
from app.db.repositories.base import BaseRepository


class SimulationCommentRepository(BaseRepository[SimulationComment]):
    def __init__(self, session: AsyncSession) -> None:
        super().__init__(session, SimulationComment)

    async def list_by_simulation_id(
        self,
        simulation_id: uuid.UUID,
    ) -> list[SimulationComment]:
        result = await self._session.scalars(
            select(SimulationComment)
            .where(SimulationComment.simulation_id == simulation_id)
            .order_by(SimulationComment.created_at.asc()),
        )
        return list(result.all())

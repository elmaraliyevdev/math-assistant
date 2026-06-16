"""Simulation review repository."""

from __future__ import annotations

import uuid

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.models.simulation_review import SimulationReview
from app.db.repositories.base import BaseRepository


class SimulationReviewRepository(BaseRepository[SimulationReview]):
    def __init__(self, session: AsyncSession) -> None:
        super().__init__(session, SimulationReview)

    async def list_by_simulation_id(
        self,
        simulation_id: uuid.UUID,
    ) -> list[SimulationReview]:
        result = await self._session.scalars(
            select(SimulationReview)
            .where(SimulationReview.simulation_id == simulation_id)
            .order_by(SimulationReview.created_at.desc()),
        )
        return list(result.all())

"""Simulation note repository."""

from __future__ import annotations

import uuid

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.models.simulation_note import SimulationNote
from app.db.repositories.base import BaseRepository


class SimulationNoteRepository(BaseRepository[SimulationNote]):
    def __init__(self, session: AsyncSession) -> None:
        super().__init__(session, SimulationNote)

    async def list_by_simulation_id(
        self,
        simulation_id: uuid.UUID,
    ) -> list[SimulationNote]:
        result = await self._session.scalars(
            select(SimulationNote)
            .where(SimulationNote.simulation_id == simulation_id)
            .order_by(SimulationNote.created_at.desc()),
        )
        return list(result.all())

    async def get_by_id_for_simulation(
        self,
        note_id: uuid.UUID,
        simulation_id: uuid.UUID,
    ) -> SimulationNote | None:
        result = await self._session.scalars(
            select(SimulationNote).where(
                SimulationNote.id == note_id,
                SimulationNote.simulation_id == simulation_id,
            ),
        )
        return result.first()

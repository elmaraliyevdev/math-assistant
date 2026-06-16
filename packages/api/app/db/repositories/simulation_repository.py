"""Simulation repository."""

from __future__ import annotations

import uuid

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.models.game import Game
from app.db.models.game_version import GameVersion
from app.db.models.simulation import Simulation, SimulationStatus
from app.db.repositories.base import BaseRepository


class SimulationRepository(BaseRepository[Simulation]):
    def __init__(self, session: AsyncSession) -> None:
        super().__init__(session, Simulation)

    def _filter_query(
        self,
        *,
        status: SimulationStatus | None,
        game_version_id: uuid.UUID | None,
        organization_ids: list[uuid.UUID] | None = None,
    ):
        stmt = select(Simulation)
        if organization_ids is not None:
            stmt = (
                stmt.join(GameVersion, Simulation.game_version_id == GameVersion.id)
                .join(Game, GameVersion.game_id == Game.id)
                .where(Game.organization_id.in_(organization_ids))
            )
        if status is not None:
            stmt = stmt.where(Simulation.status == status)
        if game_version_id is not None:
            stmt = stmt.where(Simulation.game_version_id == game_version_id)
        return stmt

    async def get_by_id_for_organizations(
        self,
        simulation_id: uuid.UUID,
        organization_ids: list[uuid.UUID],
    ) -> Simulation | None:
        if not organization_ids:
            return None
        stmt = (
            select(Simulation)
            .join(GameVersion, Simulation.game_version_id == GameVersion.id)
            .join(Game, GameVersion.game_id == Game.id)
            .where(
                Simulation.id == simulation_id,
                Game.organization_id.in_(organization_ids),
            )
        )
        result = await self._session.scalars(stmt)
        return result.first()

    async def count_filtered(
        self,
        *,
        status: SimulationStatus | None = None,
        game_version_id: uuid.UUID | None = None,
        organization_ids: list[uuid.UUID] | None = None,
    ) -> int:
        if organization_ids is not None and not organization_ids:
            return 0
        stmt = self._filter_query(
            status=status,
            game_version_id=game_version_id,
            organization_ids=organization_ids,
        )
        count_stmt = select(func.count()).select_from(stmt.subquery())
        result = await self._session.scalar(count_stmt)
        return int(result or 0)

    async def count_active(self) -> int:
        stmt = (
            select(func.count())
            .select_from(Simulation)
            .where(
                Simulation.status.in_(
                    (SimulationStatus.PENDING, SimulationStatus.RUNNING),
                ),
            )
        )
        result = await self._session.scalar(stmt)
        return int(result or 0)

    async def search_paginated(
        self,
        *,
        page: int,
        page_size: int,
        status: SimulationStatus | None = None,
        game_version_id: uuid.UUID | None = None,
        organization_ids: list[uuid.UUID] | None = None,
    ) -> list[Simulation]:
        if organization_ids is not None and not organization_ids:
            return []
        offset = (page - 1) * page_size
        stmt = (
            self._filter_query(
                status=status,
                game_version_id=game_version_id,
                organization_ids=organization_ids,
            )
            .order_by(Simulation.created_at.desc())
            .offset(offset)
            .limit(page_size)
        )
        result = await self._session.scalars(stmt)
        return list(result.all())

    async def list_by_game_version_id(
        self,
        game_version_id: uuid.UUID,
    ) -> list[Simulation]:
        result = await self._session.scalars(
            select(Simulation).where(
                Simulation.game_version_id == game_version_id,
            ),
        )
        return list(result.all())

    async def list_by_status(self, status: SimulationStatus) -> list[Simulation]:
        result = await self._session.scalars(
            select(Simulation).where(Simulation.status == status),
        )
        return list(result.all())

    async def get_organization_id(self, simulation_id: uuid.UUID) -> uuid.UUID | None:
        stmt = (
            select(Game.organization_id)
            .join(GameVersion, GameVersion.game_id == Game.id)
            .join(Simulation, Simulation.game_version_id == GameVersion.id)
            .where(Simulation.id == simulation_id)
        )
        return await self._session.scalar(stmt)

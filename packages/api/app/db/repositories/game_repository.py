"""Game repository."""

from __future__ import annotations

import uuid

from sqlalchemy import func, or_, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.models.game import Game
from app.db.repositories.base import BaseRepository


class GameRepository(BaseRepository[Game]):
    def __init__(self, session: AsyncSession) -> None:
        super().__init__(session, Game)

    async def get_by_id_for_organizations(
        self,
        game_id: uuid.UUID,
        organization_ids: list[uuid.UUID],
    ) -> Game | None:
        if not organization_ids:
            return None
        result = await self._session.scalars(
            select(Game).where(
                Game.id == game_id,
                Game.organization_id.in_(organization_ids),
            ),
        )
        return result.first()

    async def get_by_name_in_organization(
        self,
        *,
        name: str,
        organization_id: uuid.UUID,
    ) -> Game | None:
        result = await self._session.scalars(
            select(Game).where(
                Game.name == name,
                Game.organization_id == organization_id,
            ),
        )
        return result.first()

    def _search_filter(
        self,
        search: str | None,
        organization_ids: list[uuid.UUID],
    ):
        stmt = select(Game).where(Game.organization_id.in_(organization_ids))
        if search:
            pattern = f"%{search}%"
            stmt = stmt.where(
                or_(Game.name.ilike(pattern), Game.description.ilike(pattern)),
            )
        return stmt

    async def count_search(
        self,
        search: str | None = None,
        *,
        organization_ids: list[uuid.UUID],
    ) -> int:
        if not organization_ids:
            return 0
        stmt = self._search_filter(search, organization_ids)
        count_stmt = select(func.count()).select_from(stmt.subquery())
        result = await self._session.scalar(count_stmt)
        return int(result or 0)

    async def search_paginated(
        self,
        *,
        page: int,
        page_size: int,
        search: str | None = None,
        organization_ids: list[uuid.UUID],
    ) -> list[Game]:
        if not organization_ids:
            return []
        offset = (page - 1) * page_size
        stmt = (
            self._search_filter(search, organization_ids)
            .order_by(Game.created_at.desc())
            .offset(offset)
            .limit(page_size)
        )
        result = await self._session.scalars(stmt)
        return list(result.all())

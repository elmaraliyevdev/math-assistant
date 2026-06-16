"""GameVersion repository."""

from __future__ import annotations

import uuid

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.models.game_version import GameVersion
from app.db.repositories.base import BaseRepository


class GameVersionRepository(BaseRepository[GameVersion]):
    def __init__(self, session: AsyncSession) -> None:
        super().__init__(session, GameVersion)

    async def get_by_content_hash(self, content_hash: str) -> GameVersion | None:
        result = await self._session.scalars(
            select(GameVersion).where(GameVersion.content_hash == content_hash),
        )
        return result.first()

    async def list_by_game_id(self, game_id: uuid.UUID) -> list[GameVersion]:
        result = await self._session.scalars(
            select(GameVersion)
            .where(GameVersion.game_id == game_id)
            .order_by(GameVersion.version),
        )
        return list(result.all())

    async def get_by_id_for_game(
        self,
        version_id: uuid.UUID,
        game_id: uuid.UUID,
    ) -> GameVersion | None:
        result = await self._session.scalars(
            select(GameVersion).where(
                GameVersion.id == version_id,
                GameVersion.game_id == game_id,
            ),
        )
        return result.first()

    async def get_by_id_for_organizations(
        self,
        version_id: uuid.UUID,
        organization_ids: list[uuid.UUID],
    ) -> GameVersion | None:
        if not organization_ids:
            return None
        from app.db.models.game import Game

        result = await self._session.scalars(
            select(GameVersion)
            .join(Game, GameVersion.game_id == Game.id)
            .where(
                GameVersion.id == version_id,
                Game.organization_id.in_(organization_ids),
            ),
        )
        return result.first()

    async def get_max_version(self, game_id: uuid.UUID) -> int:
        result = await self._session.scalar(
            select(func.max(GameVersion.version)).where(
                GameVersion.game_id == game_id,
            ),
        )
        return int(result or 0)

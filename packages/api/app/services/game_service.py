"""Game management service."""

from __future__ import annotations

import uuid
from dataclasses import dataclass

from sqlalchemy.ext.asyncio import AsyncSession

from app.auth.context import AuthContext
from app.db.models.game import Game
from app.db.models.organization_member import OrganizationRole
from app.db.repositories.game_repository import GameRepository
from app.services.audit_service import AuditService
from app.exceptions.domain import ForbiddenError, GameNotFoundError
from app.schemas.games import (
    CreateGameRequest,
    GameListResponse,
    GameResponse,
    UpdateGameRequest,
)
from app.security.permissions import can_write_games


def _to_game_response(game: Game) -> GameResponse:
    return GameResponse(
        id=game.id,
        organization_id=game.organization_id,
        name=game.name,
        description=game.description,
        created_at=game.created_at,
        updated_at=game.updated_at,
    )


@dataclass(frozen=True, slots=True)
class GameService:
    games: GameRepository

    @classmethod
    def from_session(cls, session: AsyncSession) -> GameService:
        return cls(games=GameRepository(session))

    async def create_game(
        self,
        auth: AuthContext,
        body: CreateGameRequest,
    ) -> GameResponse:
        role = auth.require_role(body.organization_id, OrganizationRole.DEVELOPER)
        if not can_write_games(role):
            raise ForbiddenError(message="insufficient permissions to create games")

        game = Game(
            organization_id=body.organization_id,
            name=body.name,
            description=body.description,
        )
        created = await self.games.add(game)
        audit = AuditService.from_session(self.games._session)
        await audit.record(
            action="game.create",
            entity_type="game",
            entity_id=created.id,
            user_id=auth.user.id,
            organization_id=body.organization_id,
            metadata={"name": created.name},
        )
        return _to_game_response(created)

    async def list_games(
        self,
        auth: AuthContext,
        *,
        page: int,
        page_size: int,
        search: str | None,
    ) -> GameListResponse:
        organization_ids = auth.organization_ids
        total = await self.games.count_search(
            search,
            organization_ids=organization_ids,
        )
        items = await self.games.search_paginated(
            page=page,
            page_size=page_size,
            search=search,
            organization_ids=organization_ids,
        )
        return GameListResponse(
            items=[_to_game_response(game) for game in items],
            total=total,
            page=page,
            page_size=page_size,
        )

    async def get_game(self, auth: AuthContext, game_id: uuid.UUID) -> GameResponse:
        game = await self._require_game(auth, game_id)
        return _to_game_response(game)

    async def update_game(
        self,
        auth: AuthContext,
        game_id: uuid.UUID,
        body: UpdateGameRequest,
    ) -> GameResponse:
        game = await self._require_game(auth, game_id)
        auth.require_role(game.organization_id, OrganizationRole.DEVELOPER)
        if body.name is not None:
            game.name = body.name
        if body.description is not None:
            game.description = body.description
        updated = await self.games.save(game)
        return _to_game_response(updated)

    async def delete_game(self, auth: AuthContext, game_id: uuid.UUID) -> None:
        game = await self._require_game(auth, game_id)
        auth.require_role(game.organization_id, OrganizationRole.DEVELOPER)
        await self.games.delete(game)
        audit = AuditService.from_session(self.games._session)
        await audit.record(
            action="game.delete",
            entity_type="game",
            entity_id=game_id,
            user_id=auth.user.id,
            organization_id=game.organization_id,
            metadata={"name": game.name},
        )

    async def _require_game(self, auth: AuthContext, game_id: uuid.UUID) -> Game:
        game = await self.games.get_by_id_for_organizations(
            game_id,
            auth.organization_ids,
        )
        if game is None:
            raise GameNotFoundError(game_id=str(game_id))
        auth.require_membership(game.organization_id)
        return game

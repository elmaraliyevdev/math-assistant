"""Game version management router."""

from __future__ import annotations

import uuid

from fastapi import APIRouter, Depends, status

from app.auth.dependencies import get_auth_context
from app.auth.context import AuthContext
from app.dependencies import get_game_version_service
from app.schemas.game_versions import (
    CreateGameVersionRequest,
    CreateGameVersionResponse,
    GameVersionDetailResponse,
    GameVersionSummaryResponse,
)
from app.services.game_version_service import GameVersionService

router = APIRouter(prefix="/games/{game_id}/versions", tags=["game-versions"])


@router.post(
    "",
    response_model=CreateGameVersionResponse,
    status_code=status.HTTP_201_CREATED,
)
async def create_game_version(
    game_id: uuid.UUID,
    body: CreateGameVersionRequest,
    auth: AuthContext = Depends(get_auth_context),
    game_version_service: GameVersionService = Depends(get_game_version_service),
) -> CreateGameVersionResponse:
    return await game_version_service.create_version(auth, game_id, body)


@router.get("", response_model=list[GameVersionSummaryResponse])
async def list_game_versions(
    game_id: uuid.UUID,
    auth: AuthContext = Depends(get_auth_context),
    game_version_service: GameVersionService = Depends(get_game_version_service),
) -> list[GameVersionSummaryResponse]:
    return await game_version_service.list_versions(auth, game_id)


@router.get("/{version_id}", response_model=GameVersionDetailResponse)
async def get_game_version(
    game_id: uuid.UUID,
    version_id: uuid.UUID,
    auth: AuthContext = Depends(get_auth_context),
    game_version_service: GameVersionService = Depends(get_game_version_service),
) -> GameVersionDetailResponse:
    return await game_version_service.get_version(auth, game_id, version_id)

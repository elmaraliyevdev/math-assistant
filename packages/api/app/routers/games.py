"""Game management and validation router."""

from __future__ import annotations

import uuid

from fastapi import APIRouter, Depends, Query, Response, status

from app.auth.dependencies import get_auth_context
from app.auth.context import AuthContext
from app.dependencies import get_game_service, get_validation_service
from app.schemas.games import (
    CreateGameRequest,
    GameListResponse,
    GameResponse,
    ReadyResponse,
    UpdateGameRequest,
    ValidateGameFailureResponse,
    ValidateGameRequest,
    ValidateGameSuccessResponse,
)
from app.services.game_service import GameService
from app.services.validation_service import ValidationService

router = APIRouter(tags=["games"])


@router.get("/ready", response_model=ReadyResponse)
def get_ready(
    validation_service: ValidationService = Depends(get_validation_service),
) -> ReadyResponse:
    return validation_service.ready()


@router.post(
    "/games",
    response_model=GameResponse,
    status_code=status.HTTP_201_CREATED,
)
async def create_game(
    body: CreateGameRequest,
    auth: AuthContext = Depends(get_auth_context),
    game_service: GameService = Depends(get_game_service),
) -> GameResponse:
    return await game_service.create_game(auth, body)


@router.get("/games", response_model=GameListResponse)
async def list_games(
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=20, ge=1, le=100, alias="pageSize"),
    search: str | None = Query(default=None),
    auth: AuthContext = Depends(get_auth_context),
    game_service: GameService = Depends(get_game_service),
) -> GameListResponse:
    return await game_service.list_games(
        auth,
        page=page,
        page_size=page_size,
        search=search,
    )


@router.get("/games/{game_id}", response_model=GameResponse)
async def get_game(
    game_id: uuid.UUID,
    auth: AuthContext = Depends(get_auth_context),
    game_service: GameService = Depends(get_game_service),
) -> GameResponse:
    return await game_service.get_game(auth, game_id)


@router.patch("/games/{game_id}", response_model=GameResponse)
async def update_game(
    game_id: uuid.UUID,
    body: UpdateGameRequest,
    auth: AuthContext = Depends(get_auth_context),
    game_service: GameService = Depends(get_game_service),
) -> GameResponse:
    return await game_service.update_game(auth, game_id, body)


@router.delete("/games/{game_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_game(
    game_id: uuid.UUID,
    auth: AuthContext = Depends(get_auth_context),
    game_service: GameService = Depends(get_game_service),
) -> Response:
    await game_service.delete_game(auth, game_id)
    return Response(status_code=status.HTTP_204_NO_CONTENT)


@router.post(
    "/games/validate",
    response_model=ValidateGameSuccessResponse | ValidateGameFailureResponse,
    response_model_exclude_none=True,
    responses={
        200: {"model": ValidateGameSuccessResponse},
        422: {"model": ValidateGameFailureResponse},
    },
)
def validate_game(
    body: ValidateGameRequest,
    response: Response,
    validation_service: ValidationService = Depends(get_validation_service),
) -> ValidateGameSuccessResponse | ValidateGameFailureResponse:
    result = validation_service.validate(
        canonical_json=body.canonical_json,
        engine_version=body.engine_version,
    )
    if isinstance(result, ValidateGameFailureResponse):
        response.status_code = 422
    return result

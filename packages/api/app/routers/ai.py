"""AI Mathematics Assistant router."""

from __future__ import annotations

import uuid

from fastapi import APIRouter, Depends

from app.ai.service import AIService
from app.auth.context import AuthContext
from app.auth.dependencies import get_auth_context
from app.dependencies import get_ai_service
from app.schemas.ai import (
    GameVersionExplainResponse,
    SimulationAnalysisResponse,
    SimulationCompareAssistantResponse,
    SimulationCompareRequest,
    SimulationRecommendRequest,
    SimulationRecommendResponse,
)

router = APIRouter(prefix="/ai", tags=["ai"])


@router.post(
    "/simulations/{simulation_id}/analyze",
    response_model=SimulationAnalysisResponse,
)
async def analyze_simulation(
    simulation_id: uuid.UUID,
    auth: AuthContext = Depends(get_auth_context),
    ai_service: AIService = Depends(get_ai_service),
) -> SimulationAnalysisResponse:
    payload = await ai_service.analyze_simulation(auth, simulation_id)
    return SimulationAnalysisResponse.model_validate(payload)


@router.post(
    "/simulations/{simulation_id}/recommend",
    response_model=SimulationRecommendResponse,
)
async def recommend_simulation_tuning(
    simulation_id: uuid.UUID,
    body: SimulationRecommendRequest,
    auth: AuthContext = Depends(get_auth_context),
    ai_service: AIService = Depends(get_ai_service),
) -> SimulationRecommendResponse:
    payload = await ai_service.recommend_for_simulation(
        auth,
        simulation_id,
        target_rtp=body.target_rtp,
    )
    return SimulationRecommendResponse.model_validate(payload)


@router.post(
    "/simulations/compare",
    response_model=SimulationCompareAssistantResponse,
)
async def compare_simulations_assistant(
    body: SimulationCompareRequest,
    auth: AuthContext = Depends(get_auth_context),
    ai_service: AIService = Depends(get_ai_service),
) -> SimulationCompareAssistantResponse:
    payload = await ai_service.compare_simulations(auth, body.simulation_ids)
    return SimulationCompareAssistantResponse.model_validate(payload)


@router.post(
    "/game-versions/{game_version_id}/explain",
    response_model=GameVersionExplainResponse,
)
async def explain_game_version(
    game_version_id: uuid.UUID,
    auth: AuthContext = Depends(get_auth_context),
    ai_service: AIService = Depends(get_ai_service),
) -> GameVersionExplainResponse:
    payload = await ai_service.explain_game_version(auth, game_version_id)
    return GameVersionExplainResponse.model_validate(payload)

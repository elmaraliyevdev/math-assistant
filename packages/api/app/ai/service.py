"""AI Mathematics Assistant service — artifact-grounded only."""

from __future__ import annotations

import uuid
from dataclasses import dataclass

from sqlalchemy.ext.asyncio import AsyncSession

from app.ai.comparison_engine import explain_comparison, explain_game_version
from app.ai.context_builder import (
    ComparisonArtifactContext,
    GameVersionArtifactContext,
    SimulationArtifactContext,
)
from app.ai.explanation_engine import explain_simulation
from app.ai.recommendation_engine import recommend_calibration
from app.auth.context import AuthContext
from app.db.repositories.game_repository import GameRepository
from app.db.repositories.game_version_repository import GameVersionRepository
from app.exceptions.domain import GameVersionNotFoundError
from app.schemas.mathematics import CalibrateRequest
from app.services.mathematics_service import MathematicsService
from app.services.simulation_service import SimulationService


@dataclass(frozen=True, slots=True)
class AIService:
    simulations: SimulationService
    mathematics: MathematicsService
    game_versions: GameVersionRepository
    games: GameRepository

    @classmethod
    def from_session(
        cls,
        session: AsyncSession,
        *,
        queue=None,
    ) -> AIService:
        simulations = SimulationService.from_session(session, queue=queue)
        return cls(
            simulations=simulations,
            mathematics=MathematicsService.from_session(session, queue=queue),
            game_versions=GameVersionRepository(session),
            games=GameRepository(session),
        )

    async def analyze_simulation(
        self,
        auth: AuthContext,
        simulation_id: uuid.UUID,
    ) -> dict:
        context = await self._simulation_context(auth, simulation_id)
        return explain_simulation(context)

    async def recommend_for_simulation(
        self,
        auth: AuthContext,
        simulation_id: uuid.UUID,
        *,
        target_rtp: float | None = None,
    ) -> dict:
        context = await self._simulation_context(
            auth,
            simulation_id,
            include_calibration=True,
        )
        return recommend_calibration(context, target_rtp=target_rtp)

    async def compare_simulations(
        self,
        auth: AuthContext,
        simulation_ids: list[uuid.UUID],
    ) -> dict:
        comparison = await self.simulations.compare_simulations(auth, simulation_ids)
        canonical_by_version: dict[uuid.UUID, dict] = {}
        for entry in comparison.simulations:
            version_id = entry.detail.game_version_id
            if version_id not in canonical_by_version:
                canonical_by_version[version_id] = await self._load_canonical_json(
                    auth,
                    version_id,
                )
        context = ComparisonArtifactContext(
            comparison=comparison,
            canonical_by_version=canonical_by_version,
        )
        return explain_comparison(context)

    async def explain_game_version(
        self,
        auth: AuthContext,
        game_version_id: uuid.UUID,
    ) -> dict:
        canonical_json = await self._load_canonical_json(auth, game_version_id)
        theoretical = await self.mathematics.theoretical_analysis(
            auth,
            game_version_id,
        )
        title = str((canonical_json.get("metadata") or {}).get("title", "Game Version"))
        context = GameVersionArtifactContext(
            game_version_id=game_version_id,
            game_title=title,
            canonical_json=canonical_json,
            theoretical=theoretical,
        )
        return explain_game_version(context)

    async def _simulation_context(
        self,
        auth: AuthContext,
        simulation_id: uuid.UUID,
        *,
        include_calibration: bool = False,
    ) -> SimulationArtifactContext:
        detail = await self.simulations.get_simulation(auth, simulation_id)
        results = await self.simulations.get_simulation_results(auth, simulation_id)
        canonical_json = await self._load_canonical_json(auth, detail.game_version_id)

        theoretical = await self.mathematics.theoretical_analysis(
            auth,
            detail.game_version_id,
        )

        calibration = None
        if include_calibration:
            calibration = await self.mathematics.calibrate(
                auth,
                CalibrateRequest(
                    gameVersionId=detail.game_version_id,
                    simulationId=simulation_id,
                    tolerance=(
                        results.rtp_validation.tolerance
                        if results.rtp_validation is not None
                        else None
                    ),
                ),
            )

        return SimulationArtifactContext(
            simulation_id=simulation_id,
            game_version_id=detail.game_version_id,
            spin_count=detail.spin_count,
            bet_minor_units=detail.bet_minor_units,
            results=results,
            canonical_json=canonical_json,
            theoretical=theoretical,
            calibration=calibration,
        )

    async def _load_canonical_json(
        self,
        auth: AuthContext,
        game_version_id: uuid.UUID,
    ) -> dict:
        version = await self.game_versions.get_by_id_for_organizations(
            game_version_id,
            auth.organization_ids,
        )
        if version is None:
            raise GameVersionNotFoundError(
                game_id="unknown",
                version_id=str(game_version_id),
            )
        game = await self.games.get_by_id_for_organizations(
            version.game_id,
            auth.organization_ids,
        )
        if game is None:
            raise GameVersionNotFoundError(
                game_id=str(version.game_id),
                version_id=str(game_version_id),
            )
        auth.require_membership(game.organization_id)
        return dict(version.canonical_json)

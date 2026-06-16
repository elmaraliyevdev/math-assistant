"""Theoretical mathematics and calibration service."""

from __future__ import annotations

import uuid
from dataclasses import dataclass

from sqlalchemy.ext.asyncio import AsyncSession

from app.auth.context import AuthContext
from app.db.repositories.game_repository import GameRepository
from app.db.repositories.game_version_repository import GameVersionRepository
from app.exceptions.domain import GameVersionNotFoundError, SimulationNotFoundError
from app.schemas.mathematics import (
    CalibrateRequest,
    CalibrateResponse,
    CertificationReportRequest,
    CertificationReportResponse,
    TheoreticalAnalysisResponse,
)
from app.services.simulation_service import SimulationService
from runtime_core.domain.game_version import GameVersion
from runtime_core.theoretical.report import (
    build_calibration_report,
    build_theoretical_analysis,
    export_certification_json,
    export_certification_pdf,
)
from runtime_core.theoretical.certification import build_certification_report


@dataclass(frozen=True, slots=True)
class MathematicsService:
    games: GameRepository
    game_versions: GameVersionRepository
    simulations: SimulationService

    @classmethod
    def from_session(
        cls,
        session: AsyncSession,
        *,
        queue=None,
    ) -> MathematicsService:
        return cls(
            games=GameRepository(session),
            game_versions=GameVersionRepository(session),
            simulations=SimulationService.from_session(session, queue=queue),
        )

    async def theoretical_analysis(
        self,
        auth: AuthContext,
        game_version_id: uuid.UUID,
        *,
        reel_set_id: str | None = None,
        total_bet_minor_units: int | None = None,
    ) -> TheoreticalAnalysisResponse:
        game = await self._load_game(auth, game_version_id)
        analysis = build_theoretical_analysis(
            game,
            reel_set_id=reel_set_id,
            total_bet_minor_units=total_bet_minor_units,
        )
        return TheoreticalAnalysisResponse.model_validate(
            analysis.model_dump(mode="json", by_alias=True),
        )

    async def calibrate(
        self,
        auth: AuthContext,
        body: CalibrateRequest,
    ) -> CalibrateResponse:
        game = await self._load_game(auth, body.game_version_id)
        simulated_rtp, feature_frequencies, rtp_variance = await self._resolve_simulation_inputs(
            auth,
            body.simulation_id,
            body.simulated_rtp,
            None,
        )
        payload = build_calibration_report(
            game,
            simulated_rtp=simulated_rtp,
            rtp_variance=rtp_variance,
            simulated_feature_frequencies=feature_frequencies,
            total_bet_minor_units=body.total_bet_minor_units,
            reel_set_id=body.reel_set_id,
            tolerance=body.tolerance,
        )
        return CalibrateResponse.model_validate(payload)

    async def certification_report(
        self,
        auth: AuthContext,
        body: CertificationReportRequest,
    ) -> tuple[CertificationReportResponse | bytes, str, str]:
        game = await self._load_game(auth, body.game_version_id)
        simulated_rtp, feature_frequencies, rtp_variance = await self._resolve_simulation_inputs(
            auth,
            body.simulation_id,
            body.simulated_rtp,
            body.rtp_variance,
        )
        report = build_certification_report(
            game,
            simulated_rtp=simulated_rtp,
            rtp_variance=rtp_variance,
            simulated_feature_frequencies=feature_frequencies,
            total_bet_minor_units=body.total_bet_minor_units,
            reel_set_id=body.reel_set_id,
            tolerance=body.tolerance,
        )
        if body.export_format == "pdf":
            content = export_certification_pdf(report)
            filename = f"certification-{body.game_version_id}.pdf"
            return content, "application/pdf", filename

        if body.export_format == "json":
            content = export_certification_json(report)
            filename = f"certification-{body.game_version_id}.json"
            return content, "application/json", filename

        response = CertificationReportResponse.model_validate(
            report.model_dump(mode="json", by_alias=True),
        )
        return response, "application/json", f"certification-{body.game_version_id}.json"

    async def _load_game(
        self,
        auth: AuthContext,
        game_version_id: uuid.UUID,
    ) -> GameVersion:
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
        return GameVersion.model_validate(version.canonical_json)

    async def _resolve_simulation_inputs(
        self,
        auth: AuthContext,
        simulation_id: uuid.UUID | None,
        simulated_rtp: float | None,
        rtp_variance: float | None,
    ) -> tuple[float | None, dict[str, float] | None, float | None]:
        if simulation_id is None:
            return simulated_rtp, None, rtp_variance

        try:
            results = await self.simulations.get_simulation_results(auth, simulation_id)
        except SimulationNotFoundError:
            raise

        resolved_rtp = simulated_rtp if simulated_rtp is not None else results.summary.rtp
        feature_frequencies = {
            item.feature_name: item.frequency for item in results.feature_frequencies
        }
        for jackpot in results.jackpot_frequencies:
            feature_frequencies[f"JACKPOT_{jackpot.jackpot_tier.upper()}"] = (
                jackpot.frequency
            )

        resolved_variance = rtp_variance
        if resolved_variance is None and results.summary.volatility is not None:
            resolved_variance = results.summary.volatility**2

        return resolved_rtp, feature_frequencies, resolved_variance

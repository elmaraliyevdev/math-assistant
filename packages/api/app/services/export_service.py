"""Simulation and game version export helpers."""

from __future__ import annotations

import csv
import io
import json
import uuid
from dataclasses import dataclass

from sqlalchemy.ext.asyncio import AsyncSession

from app.auth.context import AuthContext
from app.db.repositories.game_version_repository import GameVersionRepository
from app.exports.pdf_reports import (
    build_simulation_comparison_pdf,
    build_simulation_results_pdf,
)
from app.services.simulation_service import SimulationService


@dataclass(frozen=True, slots=True)
class ExportService:
    simulations: SimulationService
    game_versions: GameVersionRepository

    @classmethod
    def from_session(
        cls,
        session: AsyncSession,
        *,
        queue=None,
    ) -> ExportService:
        return cls(
            simulations=SimulationService.from_session(session, queue=queue),
            game_versions=GameVersionRepository(session),
        )

    async def export_simulation_results(
        self,
        auth: AuthContext,
        simulation_id: uuid.UUID,
        export_format: str,
    ) -> tuple[bytes, str, str]:
        results = await self.simulations.get_simulation_results(auth, simulation_id)
        payload = results.model_dump(mode="json", by_alias=True)

        if export_format == "json":
            content = json.dumps(payload, indent=2).encode("utf-8")
            return content, "application/json", f"simulation-{simulation_id}.json"

        if export_format == "csv":
            buffer = io.StringIO()
            writer = csv.writer(buffer)
            writer.writerow(["section", "metric", "value"])
            summary = payload["summary"]
            for key, value in summary.items():
                writer.writerow(["summary", key, value])
            totals = payload["totals"]
            for key, value in totals.items():
                writer.writerow(["totals", key, value])
            exposure = payload["exposure"]
            for key, value in exposure.items():
                writer.writerow(["exposure", key, value])
            for feature in payload.get("featureFrequencies", []):
                writer.writerow(
                    ["feature", feature["featureName"], feature["frequency"]],
                )
            for jackpot in payload.get("jackpotFrequencies", []):
                writer.writerow(
                    ["jackpot", jackpot["jackpotTier"], jackpot["frequency"]],
                )
            return (
                buffer.getvalue().encode("utf-8"),
                "text/csv",
                f"simulation-{simulation_id}.csv",
            )

        if export_format == "pdf":
            content = build_simulation_results_pdf(payload)
            return content, "application/pdf", f"simulation-{simulation_id}.pdf"

        msg = f"unsupported export format: {export_format}"
        raise ValueError(msg)

    async def export_simulation_comparison(
        self,
        auth: AuthContext,
        simulation_ids: list[uuid.UUID],
        export_format: str,
    ) -> tuple[bytes, str, str]:
        comparison = await self.simulations.compare_simulations(auth, simulation_ids)
        payload = comparison.model_dump(mode="json", by_alias=True)

        if export_format == "json":
            content = json.dumps(payload, indent=2).encode("utf-8")
            return content, "application/json", "simulation-comparison.json"

        if export_format == "pdf":
            content = build_simulation_comparison_pdf(payload)
            return content, "application/pdf", "simulation-comparison.pdf"

        msg = f"unsupported export format: {export_format}"
        raise ValueError(msg)

    async def export_game_version_json(
        self,
        auth: AuthContext,
        game_id: uuid.UUID,
        version_id: uuid.UUID,
    ) -> tuple[bytes, str]:
        version = await self.game_versions.get_by_id_for_organizations(
            version_id,
            auth.organization_ids,
        )
        if version is None or version.game_id != game_id:
            msg = "game version not found"
            raise ValueError(msg)
        content = json.dumps(version.canonical_json, indent=2).encode("utf-8")
        filename = f"game-{game_id}-v{version.version}.json"
        return content, filename

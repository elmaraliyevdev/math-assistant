"""Build structured assistant context from stored platform artifacts."""

from __future__ import annotations

import uuid
from dataclasses import dataclass, field
from typing import Any

from app.schemas.mathematics import CalibrateResponse, TheoreticalAnalysisResponse
from app.schemas.simulations import SimulationCompareResponse, SimulationResultsResponse


@dataclass(frozen=True, slots=True)
class SimulationArtifactContext:
    simulation_id: uuid.UUID
    game_version_id: uuid.UUID
    spin_count: int
    bet_minor_units: int
    results: SimulationResultsResponse
    canonical_json: dict[str, Any]
    theoretical: TheoreticalAnalysisResponse | None = None
    calibration: CalibrateResponse | None = None


@dataclass(frozen=True, slots=True)
class ComparisonArtifactContext:
    comparison: SimulationCompareResponse
    canonical_by_version: dict[uuid.UUID, dict[str, Any]] = field(default_factory=dict)


@dataclass(frozen=True, slots=True)
class GameVersionArtifactContext:
    game_version_id: uuid.UUID
    game_title: str
    canonical_json: dict[str, Any]
    theoretical: TheoreticalAnalysisResponse


def extract_rtp_target(canonical_json: dict[str, Any]) -> float | None:
    metadata = canonical_json.get("metadata") or {}
    rtp_target = metadata.get("rtpTarget")
    if not isinstance(rtp_target, dict):
        return None
    percent = rtp_target.get("percent")
    return float(percent) if isinstance(percent, (int, float)) else None


def extract_scatter_triggers(canonical_json: dict[str, Any]) -> list[dict[str, Any]]:
    triggers: list[dict[str, Any]] = []
    machines = canonical_json.get("stateMachines") or {}
    main = machines.get("main") or {}
    states = main.get("states") or {}
    for state_id, state in states.items():
        if not isinstance(state, dict):
            continue
        config = state.get("pluginConfig") or {}
        for key in ("scatterTriggers", "bonusTriggers"):
            raw = config.get(key) or []
            if not isinstance(raw, list):
                continue
            for item in raw:
                if isinstance(item, dict):
                    triggers.append({**item, "state": state_id})
    return triggers


def extract_jackpot_tiers(canonical_json: dict[str, Any]) -> dict[str, int | float]:
    tiers: dict[str, int | float] = {}
    machines = canonical_json.get("stateMachines") or {}
    for machine in machines.values():
        if not isinstance(machine, dict):
            continue
        states = machine.get("states") or {}
        for state in states.values():
            if not isinstance(state, dict):
                continue
            config = state.get("pluginConfig") or {}
            raw = config.get("jackpotTiers")
            if not isinstance(raw, dict):
                continue
            for name, value in raw.items():
                if isinstance(value, (int, float)):
                    tiers[str(name)] = value
    return tiers


def extract_paytable_summary(canonical_json: dict[str, Any]) -> list[dict[str, Any]]:
    paytable = canonical_json.get("paytable") or {}
    pays = paytable.get("pays") or []
    if not isinstance(pays, list):
        return []
    return [item for item in pays if isinstance(item, dict)]


def exposure_from_canonical(canonical_json: dict[str, Any]) -> dict[str, Any]:
    exposure = canonical_json.get("exposure") or {}
    return exposure if isinstance(exposure, dict) else {}


def feature_frequency_map(results: SimulationResultsResponse) -> dict[str, float]:
    return {item.feature_name: item.frequency for item in results.feature_frequencies}


def decomposition_chart_dict(results: SimulationResultsResponse) -> dict[str, float]:
    chart = results.rtp_decomposition_chart
    return {
        "BASE": chart.base,
        "FREE_SPINS": chart.free_spins,
        "HOLD_AND_WIN": chart.hold_and_win,
        "JACKPOT": chart.jackpot,
        "totalRtp": chart.total_rtp,
    }

"""Historical simulation throughput estimation."""

from __future__ import annotations

from dataclasses import dataclass

from app.config import Settings
from app.db.models.simulation import Simulation, SimulationStatus

DEPLOYMENT_FALLBACK_SPINS_PER_SECOND: dict[str, float] = {
    "mvp": 50_000.0,
    "enterprise": 200_000.0,
}


@dataclass(frozen=True, slots=True)
class ThroughputEstimate:
    spins_per_second: float
    sample_count: int
    source: str


def estimate_runtime_seconds(
    *,
    spin_count: int,
    spins_per_second: float,
) -> float:
    if spins_per_second <= 0:
        return 0.0
    return spin_count / spins_per_second


def resolve_throughput(
    completed_simulations: list[Simulation],
    settings: Settings,
) -> ThroughputEstimate:
    total_spins = 0
    total_ms = 0
    samples = 0

    for simulation in completed_simulations:
        if simulation.status != SimulationStatus.COMPLETED:
            continue
        if simulation.started_at is None or simulation.completed_at is None:
            continue
        duration_ms = max(
            0,
            int((simulation.completed_at - simulation.started_at).total_seconds() * 1000),
        )
        if duration_ms <= 0:
            continue
        total_spins += simulation.completed_spin_count or simulation.spin_count
        total_ms += duration_ms
        samples += 1

    if samples > 0 and total_ms > 0:
        spins_per_second = total_spins / (total_ms / 1000)
        return ThroughputEstimate(
            spins_per_second=spins_per_second,
            sample_count=samples,
            source="historical",
        )

    mode = settings.deployment_mode.lower()
    fallback = DEPLOYMENT_FALLBACK_SPINS_PER_SECOND.get(mode, 50_000.0)
    return ThroughputEstimate(
        spins_per_second=fallback,
        sample_count=0,
        source="deployment_fallback",
    )

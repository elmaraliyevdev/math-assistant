"""Throughput estimation tests."""

from __future__ import annotations

from datetime import UTC, datetime, timedelta

from app.config import Settings
from app.db.models.simulation import Simulation, SimulationStatus
from app.workbench.throughput import (
    estimate_runtime_seconds,
    resolve_throughput,
)


def test_estimate_runtime_seconds() -> None:
    assert estimate_runtime_seconds(spin_count=100_000, spins_per_second=50_000) == 2.0


def test_resolve_throughput_uses_historical_samples() -> None:
    started = datetime.now(tz=UTC) - timedelta(seconds=2)
    completed = datetime.now(tz=UTC)
    simulations = [
        Simulation(
            status=SimulationStatus.COMPLETED,
            spin_count=100_000,
            completed_spin_count=100_000,
            started_at=started,
            completed_at=completed,
        ),
    ]
    estimate = resolve_throughput(simulations, Settings())
    assert estimate.source == "historical"
    assert estimate.sample_count == 1
    assert estimate.spins_per_second > 0


def test_resolve_throughput_falls_back_to_deployment_mode() -> None:
    estimate = resolve_throughput([], Settings(deployment_mode="mvp"))
    assert estimate.source == "deployment_fallback"
    assert estimate.sample_count == 0
    assert estimate.spins_per_second == 50_000.0


def test_resolve_throughput_uses_enterprise_fallback() -> None:
    estimate = resolve_throughput([], Settings(deployment_mode="enterprise"))
    assert estimate.spins_per_second == 200_000.0


def test_resolve_throughput_skips_invalid_samples() -> None:
    started = datetime.now(tz=UTC) - timedelta(seconds=2)
    completed = datetime.now(tz=UTC)
    simulations = [
        Simulation(status=SimulationStatus.RUNNING, spin_count=1000),
        Simulation(
            status=SimulationStatus.COMPLETED,
            spin_count=1000,
            started_at=started,
            completed_at=started,
        ),
        Simulation(
            status=SimulationStatus.COMPLETED,
            spin_count=100_000,
            completed_spin_count=100_000,
            started_at=started,
            completed_at=completed,
        ),
    ]
    estimate = resolve_throughput(simulations, Settings())
    assert estimate.source == "historical"
    assert estimate.sample_count == 1


def test_estimate_runtime_seconds_zero_throughput() -> None:
    assert estimate_runtime_seconds(spin_count=1000, spins_per_second=0) == 0.0

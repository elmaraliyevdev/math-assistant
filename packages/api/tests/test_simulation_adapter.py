"""Simulation adapter unit tests."""

from __future__ import annotations

import uuid

import pytest
from runtime_core.common.golden import load_golden_game_version
from runtime_core.runtime.events import EventLogMode

from app.adapters.simulation import (
    build_simulation_profile,
    execute_simulation_with_report,
)


def test_build_simulation_profile_defaults_master_seed() -> None:
    simulation_id = uuid.uuid4()
    profile = build_simulation_profile(
        simulation_id=simulation_id,
        spin_count=0,
        bet_minor_units=100,
        event_log_mode=EventLogMode.NONE,
        master_seed=None,
        engine_version="runtime-core@1.8.0",
    )
    assert profile.spin_count == 0
    assert profile.simulation_run_id == str(simulation_id)


def test_execute_simulation_with_report_zero_spins() -> None:
    game = load_golden_game_version("fixture-01-base-5x3")
    profile = build_simulation_profile(
        simulation_id=uuid.uuid4(),
        spin_count=0,
        bet_minor_units=100,
        event_log_mode=EventLogMode.NONE,
        master_seed="zero",
        engine_version="runtime-core@1.8.0",
    )
    outcome = execute_simulation_with_report(game, profile)
    assert outcome.engine_result.spin_count == 0
    assert outcome.mathematics_report.spin_count == 0


def test_execute_simulation_with_report_honors_cancel_callback() -> None:
    from app.exceptions.simulation import SimulationJobCancelledError

    game = load_golden_game_version("fixture-01-base-5x3")
    profile = build_simulation_profile(
        simulation_id=uuid.uuid4(),
        spin_count=5,
        bet_minor_units=100,
        event_log_mode=EventLogMode.NONE,
        master_seed="cancel",
        engine_version="runtime-core@1.8.0",
    )
    with pytest.raises(SimulationJobCancelledError):
        execute_simulation_with_report(game, profile, should_cancel=lambda: True)


def test_execute_simulation_with_report_reports_progress() -> None:
    game = load_golden_game_version("fixture-01-base-5x3")
    profile = build_simulation_profile(
        simulation_id=uuid.uuid4(),
        spin_count=3,
        bet_minor_units=100,
        event_log_mode=EventLogMode.NONE,
        master_seed="progress",
        engine_version="runtime-core@1.8.0",
    )
    progress: list[tuple[int, int]] = []

    def on_progress(completed: int, total: int) -> None:
        progress.append((completed, total))

    execute_simulation_with_report(game, profile, on_progress=on_progress)
    assert progress[-1] == (3, 3)

"""Shared fixtures for simulation job tests."""

from __future__ import annotations

import pytest

from app.config import Settings
from app.jobs.process_pool import SimulationProcessPool


@pytest.fixture
def simulation_settings() -> Settings:
    return Settings(
        simulation_worker_count=1,
        simulation_process_pool_workers=2,
        simulation_spin_wins_detail_limit=10_000,
    )


@pytest.fixture
def simulation_process_pool() -> SimulationProcessPool:
    pool = SimulationProcessPool(max_workers=2)
    pool.start()
    yield pool
    pool.shutdown(wait=True)

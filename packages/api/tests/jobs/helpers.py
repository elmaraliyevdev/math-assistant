"""Helpers for simulation job tests."""

from __future__ import annotations

import uuid
from collections.abc import Awaitable, Callable

from sqlalchemy.ext.asyncio import async_sessionmaker

from app.config import Settings
from app.jobs.process_pool import SimulationProcessPool
from app.jobs.simulation_jobs import process_simulation_job


async def run_process_simulation_job(
    session_factory: async_sessionmaker,
    simulation_id: uuid.UUID,
    *,
    process_pool: SimulationProcessPool,
    settings: Settings,
    worker_id: str = "worker-test",
) -> None:
    await process_simulation_job(
        session_factory,
        simulation_id=simulation_id,
        worker_id=worker_id,
        process_pool=process_pool,
        settings=settings,
    )

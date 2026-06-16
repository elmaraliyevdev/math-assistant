"""Simulation job queue abstraction."""

from __future__ import annotations

import asyncio
from typing import Protocol

from app.jobs.models import SimulationJob
from app.jobs.simulation_logging import log_simulation_event, log_simulation_message


class SimulationQueue(Protocol):
    """Pluggable queue for simulation jobs (in-process, Redis, Celery, SQS, …)."""

    async def enqueue(self, job: SimulationJob) -> None: ...

    async def dequeue(self) -> SimulationJob: ...


class InMemorySimulationQueue:
    """MVP in-process asyncio queue."""

    def __init__(self, *, maxsize: int = 0) -> None:
        self._queue: asyncio.Queue[SimulationJob] = asyncio.Queue(maxsize=maxsize)

    async def enqueue(self, job: SimulationJob) -> None:
        await self._queue.put(job)
        log_simulation_message(
            f"Job queued {job.simulation_id}",
            simulation_id=str(job.simulation_id),
            queue_id=id(self),
            pending_count=self.pending_count,
        )
        log_simulation_event(
            "simulation_job_queued",
            simulation_id=str(job.simulation_id),
            queue_id=id(self),
            pending_count=self.pending_count,
        )

    async def dequeue(self) -> SimulationJob:
        return await self._queue.get()

    def task_done(self) -> None:
        self._queue.task_done()

    @property
    def pending_count(self) -> int:
        return self._queue.qsize()

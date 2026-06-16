"""Simulation worker loop."""

from __future__ import annotations

import asyncio
import uuid

from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker

from app.config import Settings
from app.jobs.process_pool import SimulationProcessPool
from app.jobs.queue import InMemorySimulationQueue
from app.jobs.simulation_logging import log_simulation_event, log_simulation_message
from app.jobs.simulation_jobs import process_simulation_job


class SimulationWorker:
    def __init__(
        self,
        *,
        worker_id: str,
        queue: InMemorySimulationQueue,
        session_factory: async_sessionmaker[AsyncSession],
        process_pool: SimulationProcessPool,
        settings: Settings,
    ) -> None:
        self.worker_id = worker_id
        self._queue = queue
        self._session_factory = session_factory
        self._process_pool = process_pool
        self._settings = settings
        self._task: asyncio.Task[None] | None = None
        self._stopping = False

    async def start(self) -> None:
        if self._task is not None:
            return
        self._stopping = False
        log_simulation_message(
            f"Worker {self.worker_id} started",
            worker_id=self.worker_id,
            queue_id=id(self._queue),
        )
        self._task = asyncio.create_task(self._run())

    async def stop(self) -> None:
        """Stop accepting new jobs and wait for the current job to finish."""
        self._stopping = True
        if self._task is not None:
            await self._task
            self._task = None

    async def _run(self) -> None:
        log_simulation_message(
            "Worker waiting for jobs",
            worker_id=self.worker_id,
            queue_id=id(self._queue),
        )
        while True:
            if self._stopping:
                return
            try:
                job = await asyncio.wait_for(self._queue.dequeue(), timeout=0.25)
            except TimeoutError:
                continue
            log_simulation_message(
                f"Worker picked job {job.simulation_id}",
                worker_id=self.worker_id,
                simulation_id=str(job.simulation_id),
                queue_id=id(self._queue),
            )
            try:
                await process_simulation_job(
                    self._session_factory,
                    simulation_id=job.simulation_id,
                    worker_id=self.worker_id,
                    process_pool=self._process_pool,
                    settings=self._settings,
                )
            finally:
                self._queue.task_done()
            if self._stopping:
                return


def new_worker_id() -> str:
    return f"worker-{uuid.uuid4()}"

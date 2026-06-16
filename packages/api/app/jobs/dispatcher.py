"""Simulation worker dispatcher."""

from __future__ import annotations

from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker

from app.config import Settings
from app.db.models.simulation import SimulationStatus
from app.db.repositories.simulation_repository import SimulationRepository
from app.jobs.models import SimulationJob
from app.jobs.process_pool import SimulationProcessPool
from app.jobs.queue import InMemorySimulationQueue
from app.jobs.simulation_logging import log_simulation_event, log_simulation_message
from app.jobs.worker import SimulationWorker, new_worker_id


class SimulationDispatcher:
    """Starts and stops in-process simulation workers."""

    def __init__(
        self,
        *,
        session_factory: async_sessionmaker[AsyncSession],
        process_pool: SimulationProcessPool,
        settings: Settings,
    ) -> None:
        self._session_factory = session_factory
        self._process_pool = process_pool
        self._settings = settings
        self._worker_count = max(1, settings.simulation_worker_count)
        self.queue = InMemorySimulationQueue()
        self._workers: list[SimulationWorker] = []

    async def start(self) -> None:
        if self._workers:
            return
        log_simulation_message(
            "SimulationDispatcher started",
            queue_id=id(self.queue),
            configured_worker_count=self._settings.simulation_worker_count,
        )
        if self._worker_count <= 0:
            log_simulation_event(
                "simulation_dispatcher_misconfigured",
                configured_worker_count=self._worker_count,
            )
            msg = "API_SIMULATION_WORKER_COUNT must be greater than 0"
            raise RuntimeError(msg)
        if not self._process_pool.is_running:
            self._process_pool.start()
        await self._recover_orphaned_jobs()
        log_simulation_message(
            f"Starting {self._worker_count} workers",
            worker_count=self._worker_count,
            queue_id=id(self.queue),
        )
        for _ in range(self._worker_count):
            worker = SimulationWorker(
                worker_id=new_worker_id(),
                queue=self.queue,
                session_factory=self._session_factory,
                process_pool=self._process_pool,
                settings=self._settings,
            )
            await worker.start()
            self._workers.append(worker)
        log_simulation_event(
            "simulation_dispatcher_started",
            worker_count=len(self._workers),
            process_pool_workers=self._process_pool.max_workers,
            queue_id=id(self.queue),
        )

    async def _recover_orphaned_jobs(self) -> None:
        """Re-enqueue simulations left pending or running after an API restart."""
        async with self._session_factory() as session:
            simulations = SimulationRepository(session)
            pending = await simulations.list_by_status(SimulationStatus.PENDING)
            running = await simulations.list_by_status(SimulationStatus.RUNNING)

        recovered = 0
        for simulation in (*pending, *running):
            if simulation.cancel_requested:
                continue
            if simulation.status == SimulationStatus.RUNNING:
                async with self._session_factory() as session:
                    repo = SimulationRepository(session)
                    current = await repo.get_by_id(simulation.id)
                    if current is None or current.status != SimulationStatus.RUNNING:
                        continue
                    current.status = SimulationStatus.PENDING
                    current.worker_id = None
                    current.started_at = None
                    current.completed_spin_count = 0
                    await repo.save(current)
                    await session.commit()
            await self.queue.enqueue(SimulationJob(simulation_id=simulation.id))
            recovered += 1

        if recovered:
            log_simulation_event(
                "simulation_jobs_recovered",
                recovered_count=recovered,
            )

    async def stop(self) -> None:
        for worker in self._workers:
            await worker.stop()
        self._workers.clear()
        log_simulation_event("simulation_dispatcher_stopped")

"""Celery-backed simulation job queue."""

from __future__ import annotations

from app.jobs.models import SimulationJob
from app.jobs.simulation_logging import log_simulation_event


class DistributedSimulationQueue:
    """Enqueue simulations for Celery orchestration."""

    async def enqueue(self, job: SimulationJob) -> None:
        from app.distributed.tasks import orchestrate_simulation

        result = orchestrate_simulation.delay(str(job.simulation_id))
        log_simulation_event(
            "simulation_distributed_enqueue",
            simulation_id=str(job.simulation_id),
            celery_task_id=result.id,
        )

    async def dequeue(self) -> SimulationJob:
        msg = "DistributedSimulationQueue does not support dequeue"
        raise NotImplementedError(msg)

    @property
    def pending_count(self) -> int:
        return 0

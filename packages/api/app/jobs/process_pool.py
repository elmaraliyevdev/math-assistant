"""Shared process pool for CPU-bound simulation shard execution."""

from __future__ import annotations

import multiprocessing
from concurrent.futures import ProcessPoolExecutor

import structlog

logger = structlog.get_logger("simulation.process_pool")


class SimulationProcessPool:
    """Long-lived process pool owned by the API lifespan."""

    def __init__(self, *, max_workers: int) -> None:
        self._max_workers = max(1, max_workers)
        self._executor: ProcessPoolExecutor | None = None

    @property
    def is_running(self) -> bool:
        return self._executor is not None

    @property
    def max_workers(self) -> int:
        return self._max_workers

    def start(self) -> None:
        if self._executor is not None:
            return
        ctx = multiprocessing.get_context("spawn")
        self._executor = ProcessPoolExecutor(
            max_workers=self._max_workers,
            mp_context=ctx,
        )
        logger.info(
            "simulation_process_pool_started",
            max_workers=self._max_workers,
        )

    def shutdown(self, *, wait: bool = True) -> None:
        if self._executor is None:
            return
        self._executor.shutdown(wait=wait, cancel_futures=True)
        self._executor = None
        logger.info("simulation_process_pool_stopped")

    def executor(self) -> ProcessPoolExecutor:
        if self._executor is None:
            msg = "Simulation process pool is not running"
            raise RuntimeError(msg)
        return self._executor

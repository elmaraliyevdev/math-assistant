"""Prometheus metrics registry."""

from __future__ import annotations

import time
from typing import TYPE_CHECKING

from prometheus_client import Counter, Gauge, Histogram, generate_latest

if TYPE_CHECKING:
    from collections.abc import Callable

API_REQUESTS_TOTAL = Counter(
    "api_requests_total",
    "Total API HTTP requests",
    ["method", "path", "status"],
)
SIMULATIONS_TOTAL = Counter(
    "simulations_total",
    "Total simulations created",
    ["status"],
)
WORKER_QUEUE_SIZE = Gauge(
    "simulation_worker_queue_size",
    "Current simulation worker queue depth",
)
SIMULATION_DURATION_SECONDS = Histogram(
    "simulation_duration_seconds",
    "Simulation execution duration in seconds",
    buckets=(1, 5, 10, 30, 60, 120, 300, 600, 1800, 3600),
)


def metrics_payload() -> bytes:
    return generate_latest()


class MetricsTimer:
    def __init__(self, histogram: Histogram) -> None:
        self._histogram = histogram
        self._start = 0.0

    def __enter__(self) -> MetricsTimer:
        self._start = time.perf_counter()
        return self

    def __exit__(self, *args: object) -> None:
        self._histogram.observe(time.perf_counter() - self._start)


def observe_request(method: str, path: str, status: int) -> None:
    API_REQUESTS_TOTAL.labels(method=method, path=path, status=str(status)).inc()

"""Shared benchmark helpers — hardware info and resource measurement."""

from __future__ import annotations

import os
import platform
import resource
import sys
import time
from dataclasses import dataclass, field
from typing import TYPE_CHECKING, Callable, TypeVar

if TYPE_CHECKING:
    from collections.abc import Sequence

T = TypeVar("T")

ENGINE_VERSION = "runtime-core@1.8.0"
DEFAULT_FIXTURE_ID = "fixture-01-base-5x3"
DEFAULT_MASTER_SEED = b"cert-benchmark-v1"
DEFAULT_SIMULATION_RUN_ID = "cert-benchmark-run"


@dataclass(frozen=True, slots=True)
class HardwareSpec:
    platform_system: str
    platform_release: str
    platform_machine: str
    processor: str
    python_version: str
    cpu_count_logical: int
    cpu_count_physical: int | None
    total_memory_bytes: int | None

    def to_dict(self) -> dict[str, object]:
        return {
            "platformSystem": self.platform_system,
            "platformRelease": self.platform_release,
            "platformMachine": self.platform_machine,
            "processor": self.processor,
            "pythonVersion": self.python_version,
            "cpuCountLogical": self.cpu_count_logical,
            "cpuCountPhysical": self.cpu_count_physical,
            "totalMemoryBytes": self.total_memory_bytes,
        }


@dataclass(frozen=True, slots=True)
class BenchmarkMetrics:
    spin_count: int
    shard_count: int
    worker_count: int
    elapsed_seconds: float
    spins_per_second: float
    peak_rss_bytes: int
    cpu_percent_avg: float | None
    engine_version: str = ENGINE_VERSION

    def to_dict(self) -> dict[str, object]:
        return {
            "spinCount": self.spin_count,
            "shardCount": self.shard_count,
            "workerCount": self.worker_count,
            "elapsedSeconds": round(self.elapsed_seconds, 4),
            "spinsPerSecond": round(self.spins_per_second, 2),
            "peakRssBytes": self.peak_rss_bytes,
            "cpuPercentAvg": (
                round(self.cpu_percent_avg, 2)
                if self.cpu_percent_avg is not None
                else None
            ),
            "engineVersion": self.engine_version,
        }


@dataclass
class BenchmarkRun:
    name: str
    hardware: HardwareSpec
    metrics: BenchmarkMetrics
    metadata: dict[str, object] = field(default_factory=dict)

    def to_dict(self) -> dict[str, object]:
        return {
            "name": self.name,
            "hardware": self.hardware.to_dict(),
            "metrics": self.metrics.to_dict(),
            "metadata": self.metadata,
        }


def collect_hardware_spec() -> HardwareSpec:
    physical: int | None = None
    total_memory: int | None = None
    try:
        import psutil

        physical = psutil.cpu_count(logical=False)
        total_memory = psutil.virtual_memory().total
    except ImportError:
        physical = None
        total_memory = None

    return HardwareSpec(
        platform_system=platform.system(),
        platform_release=platform.release(),
        platform_machine=platform.machine(),
        processor=platform.processor() or "unknown",
        python_version=sys.version.split()[0],
        cpu_count_logical=os.cpu_count() or 1,
        cpu_count_physical=physical,
        total_memory_bytes=total_memory,
    )


def _peak_rss_bytes() -> int:
    usage = resource.getrusage(resource.RUSAGE_SELF)
    rss = usage.ru_maxrss
    if sys.platform == "darwin":
        return rss
    return rss * 1024


def measure_run(
    *,
    spin_count: int,
    shard_count: int,
    worker_count: int,
    fn: Callable[[], T],
) -> tuple[T, BenchmarkMetrics]:
    """Execute *fn* and capture elapsed time, throughput, memory, CPU."""
    cpu_samples: list[float] = []
    process = None
    try:
        import psutil

        process = psutil.Process(os.getpid())
        process.cpu_percent(interval=None)
    except ImportError:
        process = None

    rss_before = _peak_rss_bytes()
    started = time.perf_counter()
    result = fn()
    elapsed = time.perf_counter() - started
    rss_after = _peak_rss_bytes()

    if process is not None:
        cpu_samples.append(process.cpu_percent(interval=None))

    spins_per_second = spin_count / elapsed if elapsed > 0 else 0.0
    cpu_avg = sum(cpu_samples) / len(cpu_samples) if cpu_samples else None

    metrics = BenchmarkMetrics(
        spin_count=spin_count,
        shard_count=shard_count,
        worker_count=worker_count,
        elapsed_seconds=elapsed,
        spins_per_second=spins_per_second,
        peak_rss_bytes=max(rss_before, rss_after),
        cpu_percent_avg=cpu_avg,
    )
    return result, metrics


def aggregate_snapshot(result: object) -> dict[str, object]:
    """Extract comparable fields from SimulationResult-like objects."""
    from runtime_core.simulation.models import SimulationResult

    if not isinstance(result, SimulationResult):
        msg = "expected SimulationResult"
        raise TypeError(msg)
    return {
        "totalBetMinorUnits": result.total_bet_minor_units,
        "totalWinMinorUnits": result.total_win_minor_units,
        "uncappedWinMinorUnits": result.uncapped_win_minor_units,
        "exposureTruncationCount": result.exposure_truncation_count,
        "chainFaultCount": result.chain_fault_count,
        "featureTriggerCounts": dict(result.feature_trigger_counts),
        "jackpotCounts": dict(result.jackpot_counts),
    }


def aggregates_equal(
    left: dict[str, object],
    right: dict[str, object],
) -> bool:
    return left == right

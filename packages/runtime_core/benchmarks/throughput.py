"""Throughput benchmarks at multiple spin scales."""

from __future__ import annotations

from benchmarks.fixtures import benchmark_profile, load_benchmark_game
from benchmarks.harness import BenchmarkRun, collect_hardware_spec, measure_run
from runtime_core.simulation.runner import run_simulation

THROUGHPUT_SPIN_COUNTS: tuple[int, ...] = (1_000, 100_000, 1_000_000, 10_000_000)


def run_throughput_benchmark(
    spin_count: int,
    *,
    shard_count: int | None = None,
) -> BenchmarkRun:
    game = load_benchmark_game()
    shards = shard_count if shard_count is not None else _default_shard_count(spin_count)
    profile = benchmark_profile(spin_count=spin_count, shard_count=shards)
    worker_count = shards

    def _execute() -> object:
        return run_simulation(game, profile, max_workers=worker_count)

    _, metrics = measure_run(
        spin_count=spin_count,
        shard_count=shards,
        worker_count=worker_count,
        fn=_execute,
    )
    return BenchmarkRun(
        name=f"throughput-{spin_count}",
        hardware=collect_hardware_spec(),
        metrics=metrics,
        metadata={"fixtureId": "fixture-01-base-5x3"},
    )


def run_all_throughput_benchmarks(
    spin_counts: tuple[int, ...] = THROUGHPUT_SPIN_COUNTS,
) -> list[BenchmarkRun]:
    return [run_throughput_benchmark(count) for count in spin_counts]


def _default_shard_count(spin_count: int) -> int:
    if spin_count <= 1_000:
        return 1
    if spin_count <= 100_000:
        return 2
    if spin_count <= 1_000_000:
        return 4
    return 8

"""Shard-count determinism validation benchmarks."""

from __future__ import annotations

from dataclasses import dataclass

from benchmarks.fixtures import benchmark_profile, load_benchmark_game
from benchmarks.harness import (
    aggregate_snapshot,
    aggregates_equal,
    collect_hardware_spec,
)
from runtime_core.simulation.runner import run_simulation

SHARD_COUNTS: tuple[int, ...] = (1, 2, 4, 8, 16)
DEFAULT_VALIDATION_SPIN_COUNT = 10_000


@dataclass(frozen=True, slots=True)
class ShardDeterminismResult:
    spin_count: int
    baseline_shards: int
    shard_count: int
    passed: bool
    baseline: dict[str, object]
    actual: dict[str, object]

    def to_dict(self) -> dict[str, object]:
        return {
            "spinCount": self.spin_count,
            "baselineShards": self.baseline_shards,
            "shardCount": self.shard_count,
            "passed": self.passed,
            "baseline": self.baseline,
            "actual": self.actual,
        }


@dataclass(frozen=True, slots=True)
class ShardDeterminismReport:
    spin_count: int
    shard_counts: tuple[int, ...]
    passed: bool
    results: tuple[ShardDeterminismResult, ...]
    hardware: object

    def to_dict(self) -> dict[str, object]:
        from benchmarks.harness import HardwareSpec

        hw = self.hardware
        return {
            "spinCount": self.spin_count,
            "shardCounts": list(self.shard_counts),
            "passed": self.passed,
            "results": [item.to_dict() for item in self.results],
            "hardware": hw.to_dict() if isinstance(hw, HardwareSpec) else hw,
        }


def run_shard_determinism_validation(
    spin_count: int = DEFAULT_VALIDATION_SPIN_COUNT,
    shard_counts: tuple[int, ...] = SHARD_COUNTS,
) -> ShardDeterminismReport:
    game = load_benchmark_game()
    baseline_profile = benchmark_profile(spin_count=spin_count, shard_count=1)
    baseline_result = run_simulation(game, baseline_profile, max_workers=1)
    baseline = aggregate_snapshot(baseline_result)

    results: list[ShardDeterminismResult] = []
    for shard_count in shard_counts:
        profile = benchmark_profile(spin_count=spin_count, shard_count=shard_count)
        actual_result = run_simulation(
            game,
            profile,
            max_workers=shard_count,
        )
        actual = aggregate_snapshot(actual_result)
        results.append(
            ShardDeterminismResult(
                spin_count=spin_count,
                baseline_shards=1,
                shard_count=shard_count,
                passed=aggregates_equal(baseline, actual),
                baseline=baseline,
                actual=actual,
            ),
        )

    return ShardDeterminismReport(
        spin_count=spin_count,
        shard_counts=shard_counts,
        passed=all(item.passed for item in results),
        results=tuple(results),
        hardware=collect_hardware_spec(),
    )

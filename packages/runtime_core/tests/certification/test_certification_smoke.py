"""Certification validation tests (pytest)."""

from __future__ import annotations

import pytest

from benchmarks.rtp_convergence import run_rtp_convergence_validation
from benchmarks.shard_determinism import run_shard_determinism_validation
from benchmarks.throughput import run_throughput_benchmark


@pytest.mark.certification
def test_shard_determinism_smoke() -> None:
    report = run_shard_determinism_validation(
        spin_count=500,
        shard_counts=(1, 2, 4),
    )
    assert report.passed, [item.to_dict() for item in report.results if not item.passed]


@pytest.mark.certification
def test_throughput_1k_smoke() -> None:
    run = run_throughput_benchmark(1_000, shard_count=1)
    assert run.metrics.spins_per_second > 0
    assert run.metrics.elapsed_seconds > 0


@pytest.mark.certification
def test_rtp_convergence_smoke() -> None:
    report = run_rtp_convergence_validation(spin_counts=(1_000, 5_000))
    assert len(report.points) == 2
    assert report.points[0].rtp >= 0

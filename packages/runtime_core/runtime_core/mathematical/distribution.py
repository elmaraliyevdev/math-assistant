"""Win distribution bucket analysis."""

from __future__ import annotations

from dataclasses import dataclass

from runtime_core.mathematical.models import WinDistributionBucket, WinDistributionResult
from runtime_core.simulation.models import SimulationResult

DEFAULT_BUCKET_LABELS: tuple[str, ...] = (
    "0x",
    "0-1x",
    "1-5x",
    "5-10x",
    "10-50x",
    "50-100x",
    "100-500x",
    "500x+",
)


@dataclass(frozen=True, slots=True)
class _BucketSpec:
    label: str
    lower_exclusive: float
    upper_inclusive: float | None


def default_bucket_specs() -> tuple[_BucketSpec, ...]:
    return (
        _BucketSpec("0x", -1.0, 0.0),
        _BucketSpec("0-1x", 0.0, 1.0),
        _BucketSpec("1-5x", 1.0, 5.0),
        _BucketSpec("5-10x", 5.0, 10.0),
        _BucketSpec("10-50x", 10.0, 50.0),
        _BucketSpec("50-100x", 50.0, 100.0),
        _BucketSpec("100-500x", 100.0, 500.0),
        _BucketSpec("500x+", 500.0, None),
    )


def _classify_multiplier(multiplier: float, specs: tuple[_BucketSpec, ...]) -> str:
    for spec in specs:
        if spec.label == "0x":
            if multiplier == 0.0:
                return spec.label
            continue
        if spec.upper_inclusive is None:
            if multiplier > spec.lower_exclusive:
                return spec.label
            continue
        if spec.lower_exclusive < multiplier <= spec.upper_inclusive:
            return spec.label
    return specs[-1].label


def calculate_win_distribution(
    result: SimulationResult,
    spin_wins_minor_units: tuple[int, ...],
    *,
    bucket_labels: tuple[str, ...] | None = None,
) -> WinDistributionResult:
    """Bucket per-spin wins as multiples of bet."""
    total_spins = result.spin_count
    if total_spins == 0:
        labels = bucket_labels or DEFAULT_BUCKET_LABELS
        return WinDistributionResult(
            total_spins=0,
            bet_minor_units_per_spin=0,
            buckets=tuple(
                WinDistributionBucket(label=label, count=0, percentage=0.0)
                for label in labels
            ),
        )
    if len(spin_wins_minor_units) != total_spins:
        msg = (
            f"spin_wins length {len(spin_wins_minor_units)} "
            f"!= spin_count {total_spins}"
        )
        raise ValueError(msg)

    bet_per_spin = result.total_bet_minor_units // total_spins
    specs = default_bucket_specs()
    if bucket_labels is not None and bucket_labels != DEFAULT_BUCKET_LABELS:
        msg = "custom bucket boundaries are not supported in MVP"
        raise ValueError(msg)

    counts = {spec.label: 0 for spec in specs}
    for win in spin_wins_minor_units:
        multiplier = 0.0 if win == 0 or bet_per_spin <= 0 else win / bet_per_spin
        label = _classify_multiplier(multiplier, specs)
        counts[label] += 1

    buckets = tuple(
        WinDistributionBucket(
            label=spec.label,
            count=counts[spec.label],
            percentage=counts[spec.label] / total_spins,
        )
        for spec in specs
    )
    return WinDistributionResult(
        total_spins=total_spins,
        bet_minor_units_per_spin=bet_per_spin,
        buckets=buckets,
    )

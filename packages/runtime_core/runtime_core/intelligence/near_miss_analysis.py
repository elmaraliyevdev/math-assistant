"""Near-miss analysis from observed grid histograms."""

from __future__ import annotations

from runtime_core.intelligence.models import IntelligenceSnapshot


def summarize_near_misses(snapshot: IntelligenceSnapshot) -> tuple[str, ...]:
    findings: list[str] = []
    if snapshot.near_miss_count > 0:
        findings.append(
            f"Recorded {snapshot.near_miss_count:,} near-miss grids where scatter count was one below feature threshold.",
        )
    one_below = snapshot.scatter_count_histogram.get("2", 0)
    if one_below > 0 and snapshot.grid_observation_count > 0:
        rate = one_below / snapshot.grid_observation_count
        findings.append(
            f"Scatter near-miss rate (exactly 2 scatters) is {rate * 100:.2f}% of observed grids.",
        )
    return tuple(findings)

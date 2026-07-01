"""Evidence and confidence helpers for simulation intelligence."""

from __future__ import annotations

import math

from runtime_core.intelligence.models import EvidenceRef, IntelligenceConfidence


def confidence_from_sample_size(
    observed: float,
    expected: float,
    *,
    sample_size: int,
    tolerance: float = 0.05,
) -> IntelligenceConfidence:
    if sample_size <= 0:
        return IntelligenceConfidence(score=0.0, label="Unknown", basis="No observations")
    gap = abs(observed - expected)
    relative = gap / max(abs(expected), 1e-9)
    sample_factor = min(1.0, math.log10(max(sample_size, 10)) / 6.0)
    score = max(0.0, min(100.0, (1.0 - min(relative / max(tolerance, 1e-9), 1.0)) * 100.0 * sample_factor))
    if score >= 95:
        label = "Very high"
    elif score >= 85:
        label = "High"
    elif score >= 70:
        label = "Medium"
    else:
        label = "Low"
    return IntelligenceConfidence(
        score=round(score, 1),
        label=label,
        basis=f"Based on {sample_size:,} simulation observations",
    )


def evidence_from_path(
    *,
    source: str,
    path: str,
    value: object,
    spin_count: int,
) -> EvidenceRef:
    return EvidenceRef(
        source=source,
        path=path,
        value=str(value),
        spin_count=spin_count,
    )

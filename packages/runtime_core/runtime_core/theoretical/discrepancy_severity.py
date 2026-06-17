"""RTP discrepancy severity classification and certification gating."""

from __future__ import annotations

from enum import StrEnum

DEFAULT_CERTIFICATION_BLOCK_THRESHOLD_PP = 25.0


class DiscrepancySeverity(StrEnum):
    """Absolute RTP gap severity in percentage points."""

    MINOR = "minor"
    MODERATE = "moderate"
    MAJOR = "major"
    CRITICAL = "critical"


def classify_rtp_gap_pp(gap_pp: float) -> DiscrepancySeverity:
    """Classify the magnitude of an RTP gap (percentage points)."""
    magnitude = abs(gap_pp)
    if magnitude < 2.0:
        return DiscrepancySeverity.MINOR
    if magnitude < 10.0:
        return DiscrepancySeverity.MODERATE
    if magnitude < 25.0:
        return DiscrepancySeverity.MAJOR
    return DiscrepancySeverity.CRITICAL


def resolve_certification_status(
    gap_pp: float,
    *,
    block_threshold_pp: float = DEFAULT_CERTIFICATION_BLOCK_THRESHOLD_PP,
) -> str:
    """Return certification workflow status for a target RTP gap."""
    severity = classify_rtp_gap_pp(gap_pp)
    if (
        severity == DiscrepancySeverity.CRITICAL
        and abs(gap_pp) >= block_threshold_pp
    ):
        return "certification_blocked"
    if severity in {DiscrepancySeverity.MAJOR, DiscrepancySeverity.CRITICAL}:
        return "review_required"
    if severity == DiscrepancySeverity.MODERATE:
        return "review_required"
    return "cleared"


def rtp_metric_status(
    gap_pp: float,
    *,
    block_threshold_pp: float = DEFAULT_CERTIFICATION_BLOCK_THRESHOLD_PP,
) -> str:
    """Map an RTP gap to a discrepancy item status label."""
    if (
        classify_rtp_gap_pp(gap_pp) == DiscrepancySeverity.CRITICAL
        and abs(gap_pp) >= block_threshold_pp
    ):
        return "certification_blocked"
    return classify_rtp_gap_pp(gap_pp).value

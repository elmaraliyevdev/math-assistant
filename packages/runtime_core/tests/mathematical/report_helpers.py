"""Mathematical test helpers."""

from __future__ import annotations

from runtime_core.mathematical.models import RtpDecompositionResult


def empty_rtp_decomposition(*, total_rtp: float = 0.0) -> RtpDecompositionResult:
    return RtpDecompositionResult(totalRtp=total_rtp, categories=())

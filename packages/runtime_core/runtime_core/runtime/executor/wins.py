"""Win application and exposure cap enforcement."""

from __future__ import annotations

from dataclasses import dataclass

from runtime_core.runtime.session.factory import SessionContext


@dataclass(frozen=True, slots=True)
class WinApplicationResult:
    capped_total: int
    uncapped_total: int
    truncated: int
    cap_applied: bool


def apply_step_wins(
    session: SessionContext,
    wins: list[dict[str, object]],
) -> WinApplicationResult:
    """Add win components to session totals with exposure cap enforcement."""
    if not wins:
        return WinApplicationResult(
            capped_total=0,
            uncapped_total=0,
            truncated=0,
            cap_applied=False,
        )

    step_uncapped = sum(int(win["winMinorUnits"]) for win in wins)
    if step_uncapped <= 0:
        return WinApplicationResult(
            capped_total=0,
            uncapped_total=0,
            truncated=0,
            cap_applied=False,
        )

    cap = session.exposure.effective_cap_minor
    if not session.exposure.enforce_cap:
        session.total_win_minor_units += step_uncapped
        session.total_uncapped_win_minor_units += step_uncapped
        return WinApplicationResult(
            capped_total=step_uncapped,
            uncapped_total=step_uncapped,
            truncated=0,
            cap_applied=False,
        )

    remaining = cap - session.total_win_minor_units
    if remaining <= 0:
        session.total_uncapped_win_minor_units += step_uncapped
        truncated = step_uncapped
        session.total_truncated_minor_units += truncated
        session.exposure_cap_applied = True
        return WinApplicationResult(
            capped_total=0,
            uncapped_total=step_uncapped,
            truncated=truncated,
            cap_applied=True,
        )

    capped = min(step_uncapped, remaining)
    truncated = step_uncapped - capped
    session.total_win_minor_units += capped
    session.total_uncapped_win_minor_units += step_uncapped
    if truncated > 0:
        session.total_truncated_minor_units += truncated
        session.exposure_cap_applied = True
    return WinApplicationResult(
        capped_total=capped,
        uncapped_total=step_uncapped,
        truncated=truncated,
        cap_applied=truncated > 0,
    )

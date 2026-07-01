"""RTP contribution breakdown."""

from __future__ import annotations

from runtime_core.intelligence.models import ContributionSlice, IntelligenceSnapshot
from runtime_core.mathematical.models import MathematicsReport


def build_contribution_slices(
    snapshot: IntelligenceSnapshot,
    report: MathematicsReport,
) -> tuple[ContributionSlice, ...]:
    total_bet = max(report.rtp.total_bet_minor_units, 1)
    slices: list[ContributionSlice] = []

    for category in report.rtp_decomposition.categories:
        slices.append(
            ContributionSlice(
                id=category.rtp_category.lower(),
                label=category.rtp_category.replace("_", " ").title(),
                rtp_percent=round(category.rtp_share * 100.0, 2),
            ),
        )

    symbol_wins = sorted(
        snapshot.symbol_win_minor_units.items(),
        key=lambda item: (-item[1], item[0]),
    )
    for symbol_id, win_minor in symbol_wins[:8]:
        slices.append(
            ContributionSlice(
                id=f"symbol-{symbol_id}",
                label=symbol_id,
                rtp_percent=round((win_minor / total_bet) * 100.0, 2),
            ),
        )
    return tuple(slices)

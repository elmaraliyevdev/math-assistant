"""Symbol intelligence profiles."""

from __future__ import annotations

from runtime_core.domain.game_version import GameVersion
from runtime_core.intelligence.models import IntelligenceSnapshot, SymbolIntelligenceProfile
from runtime_core.mathematical.models import MathematicsReport


def _expected_symbol_counts(game: GameVersion, reel_set_id: str | None = None) -> dict[str, float]:
    reel_set_id = reel_set_id or game.game_config.default_reel_set_id
    reel_set = game.reel_sets.get(reel_set_id)
    if reel_set is None:
        return {}
    totals: dict[str, int] = {}
    total_cells = 0
    for reel in reel_set.reels:
        for symbol_id in reel.symbols:
            totals[symbol_id] = totals.get(symbol_id, 0) + 1
            total_cells += 1
    if total_cells == 0:
        return {}
    scale = 1.0
    return {symbol_id: count / total_cells for symbol_id, count in totals.items()}


def _top_neighbours(
    snapshot: IntelligenceSnapshot,
    symbol_id: str,
    limit: int = 3,
) -> tuple[str, ...]:
    neighbours: dict[str, int] = {}
    for other_id, count in snapshot.symbol_occurrence_counts.items():
        if other_id == symbol_id:
            continue
        neighbours[other_id] = count
    ranked = sorted(neighbours.items(), key=lambda item: (-item[1], item[0]))
    return tuple(symbol for symbol, _ in ranked[:limit])


def build_symbol_profiles(
    snapshot: IntelligenceSnapshot,
    report: MathematicsReport,
    game: GameVersion,
) -> tuple[SymbolIntelligenceProfile, ...]:
    expected_ratios = _expected_symbol_counts(game)
    total_observed = max(snapshot.grid_observation_count, 1)
    total_bet = max(report.rtp.total_bet_minor_units, 1)
    profiles: list[SymbolIntelligenceProfile] = []

    symbol_ids = sorted(
        set(snapshot.symbol_occurrence_counts) | set(expected_ratios),
    )
    for symbol_id in symbol_ids:
        occurrences = snapshot.symbol_occurrence_counts.get(symbol_id, 0)
        expected = expected_ratios.get(symbol_id, 0.0) * total_observed
        difference_percent = (
            ((occurrences - expected) / expected) * 100.0 if expected > 0 else 0.0
        )
        win_minor = snapshot.symbol_win_minor_units.get(symbol_id, 0)
        rtp_contribution = (win_minor / total_bet) * 100.0
        top_combo = None
        top_combo_count = 0
        for signature, count in snapshot.winning_line_signatures.items():
            if not signature.startswith(f"{symbol_id}x"):
                continue
            if count > top_combo_count:
                top_combo = signature
                top_combo_count = count
        health = "Healthy"
        if abs(difference_percent) > 5:
            health = "Warning"
        if abs(difference_percent) > 12:
            health = "Unhealthy"
        profiles.append(
            SymbolIntelligenceProfile(
                symbol_id=symbol_id,
                occurrences=occurrences,
                expected_occurrences=round(expected, 1),
                difference_percent=round(difference_percent, 2),
                rtp_contribution_percent=round(rtp_contribution, 2),
                average_spacing=None,
                top_neighbours=_top_neighbours(snapshot, symbol_id),
                top_winning_combination=top_combo,
                top_winning_combination_count=top_combo_count,
                health=health,
            ),
        )
    return tuple(profiles)

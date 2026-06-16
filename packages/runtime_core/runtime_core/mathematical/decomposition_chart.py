"""Chart-friendly RTP decomposition with jackpot split."""

from __future__ import annotations

from runtime_core.domain.game_version import GameVersion
from runtime_core.mathematical.models import RtpDecompositionChart
from runtime_core.simulation.models import SimulationResult


def _jackpot_tiers(game: GameVersion) -> dict[str, int]:
    haw = game.state_machines.get("hold_and_win")
    if haw is None:
        return {}
    state = haw.states.get("HAW_RESPINS")
    if state is None:
        return {}
    raw = state.plugin_config.get("jackpotTiers", {})
    if not isinstance(raw, dict):
        return {}
    return {str(k): int(v) for k, v in raw.items()}


def build_rtp_decomposition_chart(
    result: SimulationResult,
    game: GameVersion | None = None,
) -> RtpDecompositionChart:
    """Build percentage shares (0–100 scale) that sum to total RTP percent."""
    total_bet = result.total_bet_minor_units
    if total_bet <= 0:
        return RtpDecompositionChart()

    bet_per_spin = total_bet // result.spin_count if result.spin_count else 0
    category_wins = result.win_by_rtp_category_minor_units

    base_pct = category_wins.get("BASE", 0) / total_bet * 100.0
    fs_pct = category_wins.get("FREE_SPINS", 0) / total_bet * 100.0
    haw_total_pct = category_wins.get("HOLD_AND_WIN", 0) / total_bet * 100.0

    jackpot_pct = 0.0
    if game is not None and bet_per_spin > 0 and result.jackpot_counts:
        tiers = _jackpot_tiers(game)
        jackpot_win = sum(
            result.jackpot_counts.get(tier, 0) * mult * bet_per_spin
            for tier, mult in tiers.items()
        )
        jackpot_pct = jackpot_win / total_bet * 100.0

    haw_pct = max(0.0, haw_total_pct - jackpot_pct)
    total_pct = base_pct + fs_pct + haw_pct + jackpot_pct

    return RtpDecompositionChart(
        base=round(base_pct, 4),
        free_spins=round(fs_pct, 4),
        hold_and_win=round(haw_pct, 4),
        jackpot=round(jackpot_pct, 4),
        total_rtp=round(total_pct, 4),
    )

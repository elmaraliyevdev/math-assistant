"""Reel and position intelligence."""

from __future__ import annotations

from runtime_core.domain.game_version import GameVersion
from runtime_core.intelligence.clustering_analysis import reel_entropy
from runtime_core.intelligence.models import IntelligenceSnapshot, PositionIntelligenceCell, ReelIntelligenceReport


def build_reel_reports(
    snapshot: IntelligenceSnapshot,
    game: GameVersion,
) -> tuple[ReelIntelligenceReport, ...]:
    reel_set = game.reel_sets.get(game.game_config.default_reel_set_id)
    if reel_set is None:
        return ()
    reports: list[ReelIntelligenceReport] = []
    total_win = max(sum(snapshot.reel_win_minor_units.values()), 1)
    for reel in reel_set.reels:
        reel_key = str(reel.reel_index)
        symbol_counts: dict[str, int] = {}
        wild = 0
        scatter = 0
        feature = 0
        for symbol_id, per_reel in snapshot.symbol_reel_counts.items():
            count = per_reel.get(reel_key, 0)
            if count <= 0:
                continue
            symbol_counts[symbol_id] = count
            upper = symbol_id.upper()
            if "WILD" in upper or symbol_id in {"W", "WI"}:
                wild += count
            if "SCATTER" in upper or symbol_id in {"S", "SC"}:
                scatter += count
            if "BONUS" in upper or symbol_id in {"B"}:
                feature += count
        observations = sum(symbol_counts.values()) or 1
        win_share = snapshot.reel_win_minor_units.get(reel_key, 0)
        health = "Healthy"
        entropy = reel_entropy(symbol_counts)
        if entropy < 1.5:
            health = "Warning"
        reports.append(
            ReelIntelligenceReport(
                reel_index=reel.reel_index,
                length=len(reel.symbols),
                entropy=round(entropy, 2),
                feature_density=round(feature / observations, 4),
                wild_density=round(wild / observations, 4),
                scatter_density=round(scatter / observations, 4),
                winning_contribution_percent=round((win_share / total_win) * 100.0, 2),
                health=health,
                rank=0,
            ),
        )
    ranked = sorted(reports, key=lambda item: (-item.winning_contribution_percent, item.reel_index))
    return tuple(
        item.model_copy(update={"rank": index + 1}) for index, item in enumerate(ranked)
    )


def build_position_highlights(
    snapshot: IntelligenceSnapshot,
    *,
    limit: int = 12,
) -> tuple[PositionIntelligenceCell, ...]:
    cells: list[PositionIntelligenceCell] = []
    for symbol_id, positions in snapshot.symbol_position_counts.items():
        for key, landings in positions.items():
            reel_str, pos_str = key.split(":", 1)
            contribution = "High" if landings > snapshot.grid_observation_count * 0.05 else "Medium"
            health = "Good" if landings > 0 else "Low"
            cells.append(
                PositionIntelligenceCell(
                    reel_index=int(reel_str),
                    position=int(pos_str),
                    symbol_id=symbol_id,
                    landings=landings,
                    winning_contribution=contribution,
                    health=health,
                ),
            )
    cells.sort(key=lambda item: (-item.landings, item.reel_index, item.position))
    return tuple(cells[:limit])

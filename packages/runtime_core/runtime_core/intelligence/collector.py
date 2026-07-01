"""Collect commutative intelligence counters during spin execution."""

from __future__ import annotations

from dataclasses import dataclass, field

from runtime_core.intelligence.models import IntelligenceSnapshot, _merge_counts, _merge_nested_counts

_FEATURE_SYMBOL_HINTS = frozenset({"SCATTER", "S", "WILD", "W", "BONUS", "B"})


@dataclass
class IntelligenceCollector:
    snapshot: IntelligenceSnapshot = field(default_factory=IntelligenceSnapshot.empty)

    def record_grid(
        self,
        rtp_category: str,
        symbols: list[list[str]],
        *,
        scatter_near_miss_threshold: int = 3,
    ) -> None:
        if not symbols:
            return
        symbol_occurrence_counts = dict(self.snapshot.symbol_occurrence_counts)
        symbol_reel_counts = {key: dict(value) for key, value in self.snapshot.symbol_reel_counts.items()}
        symbol_position_counts = {
            key: dict(value) for key, value in self.snapshot.symbol_position_counts.items()
        }
        scatter_landings_by_reel = dict(self.snapshot.scatter_landings_by_reel)
        wild_landings_by_reel = dict(self.snapshot.wild_landings_by_reel)
        feature_mode_grid_counts = dict(self.snapshot.feature_mode_grid_counts)
        scatter_count_histogram = dict(self.snapshot.scatter_count_histogram)

        scatter_count = 0
        for reel_index, column in enumerate(symbols):
            for position, symbol_id in enumerate(column):
                symbol_occurrence_counts[symbol_id] = symbol_occurrence_counts.get(symbol_id, 0) + 1
                reel_bucket = symbol_reel_counts.setdefault(symbol_id, {})
                reel_key = str(reel_index)
                reel_bucket[reel_key] = reel_bucket.get(reel_key, 0) + 1
                position_bucket = symbol_position_counts.setdefault(symbol_id, {})
                position_key = f"{reel_index}:{position}"
                position_bucket[position_key] = position_bucket.get(position_key, 0) + 1
                upper = symbol_id.upper()
                if "SCATTER" in upper or symbol_id in {"S", "SC"}:
                    scatter_count += 1
                    scatter_landings_by_reel[reel_key] = scatter_landings_by_reel.get(reel_key, 0) + 1
                if "WILD" in upper or symbol_id in {"W", "WI"}:
                    wild_landings_by_reel[reel_key] = wild_landings_by_reel.get(reel_key, 0) + 1

        scatter_key = str(scatter_count)
        scatter_count_histogram[scatter_key] = scatter_count_histogram.get(scatter_key, 0) + 1
        feature_mode_grid_counts[rtp_category] = feature_mode_grid_counts.get(rtp_category, 0) + 1

        near_miss_count = self.snapshot.near_miss_count
        if scatter_near_miss_threshold > 0 and scatter_count == scatter_near_miss_threshold - 1:
            near_miss_count += 1

        self.snapshot = IntelligenceSnapshot(
            grid_observation_count=self.snapshot.grid_observation_count + 1,
            symbol_occurrence_counts=symbol_occurrence_counts,
            symbol_reel_counts=symbol_reel_counts,
            symbol_position_counts=symbol_position_counts,
            symbol_win_minor_units=dict(self.snapshot.symbol_win_minor_units),
            symbol_win_event_counts=dict(self.snapshot.symbol_win_event_counts),
            reel_win_minor_units=dict(self.snapshot.reel_win_minor_units),
            winning_line_signatures=dict(self.snapshot.winning_line_signatures),
            scatter_landings_by_reel=scatter_landings_by_reel,
            scatter_count_histogram=scatter_count_histogram,
            wild_landings_by_reel=wild_landings_by_reel,
            feature_mode_grid_counts=feature_mode_grid_counts,
            near_miss_count=near_miss_count,
        )

    def record_wins(self, wins: list[dict[str, object]]) -> None:
        if not wins:
            return
        symbol_win_minor_units = dict(self.snapshot.symbol_win_minor_units)
        symbol_win_event_counts = dict(self.snapshot.symbol_win_event_counts)
        winning_line_signatures = dict(self.snapshot.winning_line_signatures)
        for win in wins:
            symbol_id = str(win.get("symbolId", ""))
            amount = int(win.get("winMinorUnits", 0))
            if not symbol_id:
                continue
            symbol_win_minor_units[symbol_id] = symbol_win_minor_units.get(symbol_id, 0) + amount
            symbol_win_event_counts[symbol_id] = symbol_win_event_counts.get(symbol_id, 0) + 1
            count = int(win.get("count", 0))
            signature = f"{symbol_id}x{count}" if count > 0 else symbol_id
            winning_line_signatures[signature] = winning_line_signatures.get(signature, 0) + 1
        self.snapshot = self.snapshot.model_copy(
            update={
                "symbol_win_minor_units": symbol_win_minor_units,
                "symbol_win_event_counts": symbol_win_event_counts,
                "winning_line_signatures": winning_line_signatures,
            },
        )

    def freeze(self) -> IntelligenceSnapshot:
        return self.snapshot

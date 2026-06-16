"""Per-chain analytics collected independently of event log mode."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

_NON_FEATURE_TRIGGER_TOKENS = frozenset({"SPIN_COMPLETE", "FEATURE_COMPLETE"})


@dataclass
class ChainMetricsCollector:
    """Mutable accumulator for one spin chain execution."""

    feature_trigger_counts: dict[str, int] = field(default_factory=dict)
    win_by_rtp_category_minor_units: dict[str, int] = field(default_factory=dict)
    jackpot_counts: dict[str, int] = field(default_factory=dict)
    nested_feature_entries: int = 0
    trace_steps: list[dict[str, Any]] = field(default_factory=list)

    def record_trigger_tokens(self, tokens: list[str]) -> None:
        for token in tokens:
            if token in _NON_FEATURE_TRIGGER_TOKENS:
                continue
            self.feature_trigger_counts[token] = (
                self.feature_trigger_counts.get(token, 0) + 1
            )

    def record_wins(self, rtp_category: str, wins: list[dict[str, Any]]) -> None:
        total = sum(int(win.get("winMinorUnits", 0)) for win in wins)
        if total > 0:
            self.win_by_rtp_category_minor_units[rtp_category] = (
                self.win_by_rtp_category_minor_units.get(rtp_category, 0) + total
            )
        for win in wins:
            if str(win.get("source")) != "jackpot":
                continue
            tier = str(win.get("symbolId", "unknown"))
            self.jackpot_counts[tier] = self.jackpot_counts.get(tier, 0) + 1

    def record_nested_spawn(self) -> None:
        self.nested_feature_entries += 1

    def record_trace_step(self, step: dict[str, Any]) -> None:
        self.trace_steps.append(step)

    def freeze(self) -> ChainMetrics:
        return ChainMetrics(
            feature_trigger_counts=dict(self.feature_trigger_counts),
            win_by_rtp_category_minor_units=dict(self.win_by_rtp_category_minor_units),
            jackpot_counts=dict(self.jackpot_counts),
            nested_feature_entries=self.nested_feature_entries,
            trace_steps=tuple(self.trace_steps),
        )


@dataclass(frozen=True, slots=True)
class ChainMetrics:
    """Deterministic per-chain metrics for simulation aggregation."""

    feature_trigger_counts: dict[str, int]
    win_by_rtp_category_minor_units: dict[str, int]
    jackpot_counts: dict[str, int]
    nested_feature_entries: int
    trace_steps: tuple[dict[str, Any], ...] = ()

    @classmethod
    def empty(cls) -> ChainMetrics:
        return cls(
            feature_trigger_counts={},
            win_by_rtp_category_minor_units={},
            jackpot_counts={},
            nested_feature_entries=0,
            trace_steps=(),
        )

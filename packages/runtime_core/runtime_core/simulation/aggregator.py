"""Commutative partial accumulator for simulation aggregation."""

from __future__ import annotations

from dataclasses import dataclass, field

from runtime_core.intelligence.models import IntelligenceSnapshot
from runtime_core.runtime.spin_chain import SpinChainResult


def _merge_counts(left: dict[str, int], right: dict[str, int]) -> dict[str, int]:
    merged = dict(left)
    for key, value in right.items():
        merged[key] = merged.get(key, 0) + value
    return merged


@dataclass
class PartialAccumulator:
    """Shard-local metrics merged commutatively across shards."""

    spin_count: int = 0
    total_bet_minor_units: int = 0
    total_win_minor_units: int = 0
    uncapped_win_minor_units: int = 0
    exposure_truncation_count: int = 0
    exposure_truncated_minor_units: int = 0
    chain_fault_count: int = 0
    limit_hit_count: int = 0
    feature_trigger_counts: dict[str, int] = field(default_factory=dict)
    jackpot_counts: dict[str, int] = field(default_factory=dict)
    win_by_rtp_category_minor_units: dict[str, int] = field(default_factory=dict)
    nested_feature_entries: int = 0
    event_sample_count: int = 0
    intelligence_snapshot: IntelligenceSnapshot = field(default_factory=IntelligenceSnapshot.empty)

    @classmethod
    def empty(cls) -> PartialAccumulator:
        return cls()

    def merge(self, other: PartialAccumulator) -> PartialAccumulator:
        return PartialAccumulator(
            spin_count=self.spin_count + other.spin_count,
            total_bet_minor_units=self.total_bet_minor_units + other.total_bet_minor_units,
            total_win_minor_units=self.total_win_minor_units + other.total_win_minor_units,
            uncapped_win_minor_units=(
                self.uncapped_win_minor_units + other.uncapped_win_minor_units
            ),
            exposure_truncation_count=(
                self.exposure_truncation_count + other.exposure_truncation_count
            ),
            exposure_truncated_minor_units=(
                self.exposure_truncated_minor_units + other.exposure_truncated_minor_units
            ),
            chain_fault_count=self.chain_fault_count + other.chain_fault_count,
            limit_hit_count=self.limit_hit_count + other.limit_hit_count,
            feature_trigger_counts=_merge_counts(
                self.feature_trigger_counts,
                other.feature_trigger_counts,
            ),
            jackpot_counts=_merge_counts(self.jackpot_counts, other.jackpot_counts),
            win_by_rtp_category_minor_units=_merge_counts(
                self.win_by_rtp_category_minor_units,
                other.win_by_rtp_category_minor_units,
            ),
            nested_feature_entries=self.nested_feature_entries + other.nested_feature_entries,
            event_sample_count=self.event_sample_count + other.event_sample_count,
            intelligence_snapshot=self.intelligence_snapshot.merge(other.intelligence_snapshot),
        )

    def add_chain(self, result: SpinChainResult, *, events_sampled: bool) -> PartialAccumulator:
        updated = PartialAccumulator(
            spin_count=self.spin_count + 1,
            total_bet_minor_units=self.total_bet_minor_units + result.total_bet_minor_units,
            total_win_minor_units=self.total_win_minor_units + result.total_win_minor_units,
            uncapped_win_minor_units=(
                self.uncapped_win_minor_units + result.total_uncapped_win_minor_units
            ),
            exposure_truncation_count=(
                self.exposure_truncation_count
                + result.accumulator_delta.exposure_truncation_count
            ),
            exposure_truncated_minor_units=(
                self.exposure_truncated_minor_units
                + result.accumulator_delta.exposure_truncated_minor_units
            ),
            chain_fault_count=(
                self.chain_fault_count + result.accumulator_delta.chain_fault_count
            ),
            limit_hit_count=self.limit_hit_count + (1 if result.limit_hit is not None else 0),
            feature_trigger_counts=dict(self.feature_trigger_counts),
            jackpot_counts=dict(self.jackpot_counts),
            win_by_rtp_category_minor_units=dict(self.win_by_rtp_category_minor_units),
            nested_feature_entries=self.nested_feature_entries,
            event_sample_count=self.event_sample_count + (1 if events_sampled else 0),
            intelligence_snapshot=self.intelligence_snapshot,
        )
        updated.feature_trigger_counts = _merge_counts(
            updated.feature_trigger_counts,
            _feature_triggers_from_chain_metrics(result),
        )
        updated.jackpot_counts = _merge_counts(
            updated.jackpot_counts,
            _jackpot_counts_from_chain_metrics(result),
        )
        updated.win_by_rtp_category_minor_units = _merge_counts(
            updated.win_by_rtp_category_minor_units,
            dict(result.chain_metrics.win_by_rtp_category_minor_units),
        )
        updated.nested_feature_entries += result.chain_metrics.nested_feature_entries
        updated.intelligence_snapshot = updated.intelligence_snapshot.merge(
            result.chain_metrics.intelligence_snapshot,
        )
        if result.fault is not None:
            updated.chain_fault_count += 1
        return updated


class AccumulatorAggregator:
    """Merge partial accumulators from independent shards."""

    @staticmethod
    def aggregate(partials: tuple[PartialAccumulator, ...]) -> PartialAccumulator:
        total = PartialAccumulator.empty()
        for partial in partials:
            total = total.merge(partial)
        return total


def _feature_triggers_from_chain_metrics(result: SpinChainResult) -> dict[str, int]:
    return dict(result.chain_metrics.feature_trigger_counts)


def _jackpot_counts_from_chain_metrics(result: SpinChainResult) -> dict[str, int]:
    return dict(result.chain_metrics.jackpot_counts)


def _feature_triggers_from_events(result: SpinChainResult) -> dict[str, int]:
    counts: dict[str, int] = {}
    for event in result.events:
        if event.event_type != EventType.TRIGGER_EMITTED:
            continue
        tokens = event.payload.get("tokens")
        if not isinstance(tokens, list):
            continue
        for token in tokens:
            if isinstance(token, str):
                counts[token] = counts.get(token, 0) + 1
    return counts


def _jackpot_counts_from_events(result: SpinChainResult) -> dict[str, int]:
    counts: dict[str, int] = {}
    for event in result.events:
        if event.event_type != EventType.WIN_EVALUATED:
            continue
        components = event.payload.get("components")
        if not isinstance(components, list):
            continue
        for component in components:
            if not isinstance(component, dict):
                continue
            if component.get("source") != "jackpot":
                continue
            tier = str(component.get("symbolId", "unknown"))
            counts[tier] = counts.get(tier, 0) + 1
    return counts

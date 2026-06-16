"""Theoretical feature trigger and jackpot probabilities."""

from __future__ import annotations

from runtime_core.domain.game_version import GameVersion
from runtime_core.mathematical.theoretical_frequency import (
    collect_trigger_specs,
    expected_trigger_frequency,
)
from runtime_core.theoretical.models import FeatureProbability


def calculate_feature_probabilities(game: GameVersion) -> tuple[FeatureProbability, ...]:
    """Compute theoretical trigger probabilities for features and jackpots."""
    results: list[FeatureProbability] = []
    seen: set[str] = set()

    for spec in collect_trigger_specs(game):
        if spec.state_id != "BASE":
            continue
        key = spec.feature
        if key in seen:
            continue
        probability = expected_trigger_frequency(game, spec)
        if probability is None:
            continue
        seen.add(key)
        results.append(_to_probability(key, probability))

    for tier, probability in _jackpot_tier_probabilities(game).items():
        trigger = f"JACKPOT_{tier.upper()}"
        if trigger in seen:
            continue
        seen.add(trigger)
        results.append(_to_probability(trigger, probability))

    return tuple(sorted(results, key=lambda item: item.trigger))


def _to_probability(trigger: str, probability: float) -> FeatureProbability:
    one_in_x = None
    if probability > 0.0:
        one_in_x = round(1.0 / probability, 2)
    return FeatureProbability(
        trigger=trigger,
        probability=round(probability, 8),
        oneInX=one_in_x,
    )


def _jackpot_tier_probabilities(game: GameVersion) -> dict[str, float]:
    """Estimate jackpot tier hit rates from Hold & Win configuration."""
    tiers: dict[str, int] = {}
    haw_trigger_prob = 0.0

    for spec in collect_trigger_specs(game):
        if spec.feature != "HOLD_AND_WIN" or spec.state_id != "BASE":
            continue
        expected = expected_trigger_frequency(game, spec)
        if expected is not None:
            haw_trigger_prob = max(haw_trigger_prob, expected)

    for machine in game.state_machines.values():
        for state in machine.states.values():
            config = state.plugin_config
            raw_tiers = config.get("jackpotTiers")
            if not isinstance(raw_tiers, dict):
                continue
            for tier_name, multiplier in raw_tiers.items():
                if isinstance(multiplier, (int, float)) and multiplier > 0:
                    tiers[str(tier_name)] = int(multiplier)

    if not tiers:
        return {}

    if haw_trigger_prob <= 0.0:
        return {name: 0.0 for name in tiers}

    inverse_weights = {name: 1.0 / value for name, value in tiers.items()}
    weight_sum = sum(inverse_weights.values())
    return {
        name: haw_trigger_prob * (weight / weight_sum)
        for name, weight in inverse_weights.items()
    }

"""Win adjustment logic for core.multiplier."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from runtime_core.plugins.multiplier.config import ApplyTo, MultiplierConfig
from runtime_core.runtime.rng.protocol import RNG


@dataclass(frozen=True, slots=True)
class MultiplierApplyResult:
    wins: list[dict[str, Any]]
    factor: int


def apply_multiplier(
    config: MultiplierConfig,
    wins: list[dict[str, Any]],
    rng: RNG,
) -> MultiplierApplyResult:
    """Adjust win components in place according to multiplier config."""
    factor = resolve_multiplier_factor(config, rng)
    adjusted: list[dict[str, Any]] = []
    for win in wins:
        if not _should_apply(config.apply_to, win):
            adjusted.append(dict(win))
            continue
        base = int(win["winMinorUnits"])
        patched = dict(win)
        patched["winMinorUnits"] = base * factor
        patched["multiplierApplied"] = factor
        adjusted.append(patched)
    return MultiplierApplyResult(wins=adjusted, factor=factor)


def resolve_multiplier_factor(config: MultiplierConfig, rng: RNG) -> int:
    if config.mode == "fixed":
        return config.value
    if config.mode == "ladder":
        if not config.ladder:
            msg = "ladder mode requires ladder values"
            raise ValueError(msg)
        index = rng.next_int(len(config.ladder))
        return config.ladder[index]
    if not config.weights:
        msg = "random_weighted mode requires weights"
        raise ValueError(msg)
    values = _weighted_multiplier_values(config)
    index = _weighted_index(rng, config.weights)
    return values[index]


def _weighted_multiplier_values(config: MultiplierConfig) -> tuple[int, ...]:
    if config.ladder:
        return config.ladder
    return tuple(config.value * (index + 1) for index in range(len(config.weights)))


def _weighted_index(rng: RNG, weights: tuple[int, ...]) -> int:
    total = sum(weights)
    if total <= 0:
        msg = "weights must sum to a positive value"
        raise ValueError(msg)
    pick = rng.next_int(total)
    cumulative = 0
    for index, weight in enumerate(weights):
        cumulative += weight
        if pick < cumulative:
            return index
    return len(weights) - 1


def _should_apply(apply_to: ApplyTo, win: dict[str, Any]) -> bool:
    source = str(win.get("source", ""))
    if apply_to == "all_wins_in_frame":
        return True
    if apply_to == "line_wins_only":
        return source == "lines"
    return source != "lines"

"""Multiplier configuration parsing for core.multiplier."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Literal

from runtime_core.plugins.exceptions import PluginConfigurationError

ApplyTo = Literal["all_wins_in_frame", "line_wins_only", "feature_wins_only"]
Mode = Literal["fixed", "ladder", "random_weighted"]


@dataclass(frozen=True, slots=True)
class MultiplierConfig:
    mode: Mode
    value: int
    scope: str
    apply_to: ApplyTo
    ladder: tuple[int, ...] = ()
    weights: tuple[int, ...] = ()


def parse_multiplier_config(raw: dict[str, object]) -> MultiplierConfig:
    mode = str(raw["mode"])
    if mode not in {"fixed", "ladder", "random_weighted"}:
        msg = f"unsupported multiplier mode {mode!r}"
        raise PluginConfigurationError(msg)
    value = int(raw["value"])  # type: ignore[arg-type]
    apply_to = str(raw["applyTo"])
    if apply_to not in {
        "all_wins_in_frame",
        "line_wins_only",
        "feature_wins_only",
    }:
        msg = f"unsupported multiplier applyTo {apply_to!r}"
        raise PluginConfigurationError(msg)
    ladder_raw = raw.get("ladder", [])
    weights_raw = raw.get("weights", [])
    ladder = tuple(int(item) for item in ladder_raw) if isinstance(ladder_raw, list) else ()
    weights = tuple(int(item) for item in weights_raw) if isinstance(weights_raw, list) else ()
    if mode == "ladder" and not ladder:
        msg = "ladder mode requires ladder values"
        raise PluginConfigurationError(msg)
    if mode == "random_weighted" and not weights:
        msg = "random_weighted mode requires weights"
        raise PluginConfigurationError(msg)
    return MultiplierConfig(
        mode=mode,  # type: ignore[arg-type]
        value=value,
        scope=str(raw["scope"]),
        apply_to=apply_to,  # type: ignore[arg-type]
        ladder=ladder,
        weights=weights,
    )

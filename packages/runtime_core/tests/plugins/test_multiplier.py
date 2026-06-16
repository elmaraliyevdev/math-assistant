"""core.multiplier plugin tests."""

from __future__ import annotations

import pytest

from runtime_core.plugins.exceptions import PluginConfigurationError
from runtime_core.plugins.multiplier.apply import apply_multiplier
from runtime_core.plugins.multiplier.config import parse_multiplier_config
from runtime_core.plugins.multiplier.plugin import MultiplierPlugin
from runtime_core.runtime.rng.service import RNGService


class _FixedRNG:
    __slots__ = ("_values", "_index", "_draw_id")

    def __init__(self, values: list[int]) -> None:
        self._values = values
        self._index = 0
        self._draw_id = 0

    def next_uint64(self) -> int:
        self._draw_id += 1
        return 0

    def next_int(self, n: int) -> int:
        self._draw_id += 1
        value = self._values[self._index]
        self._index = min(self._index + 1, len(self._values) - 1)
        if value >= n:
            return n - 1
        return value

    @property
    def draw_id(self) -> int:
        return self._draw_id


def _sample_wins() -> list[dict[str, int | str]]:
    return [
        {"source": "lines", "symbolId": "H1", "count": 5, "winMinorUnits": 10000},
        {"source": "scatter", "symbolId": "SCATTER", "count": 3, "winMinorUnits": 500},
    ]


def test_fixed_multiplier_applies_to_all_wins() -> None:
    config = parse_multiplier_config(
        {
            "mode": "fixed",
            "value": 2,
            "scope": "feature_frame",
            "applyTo": "all_wins_in_frame",
        },
    )
    result = apply_multiplier(config, _sample_wins(), _FixedRNG([0]))
    assert result.factor == 2
    assert result.wins[0]["winMinorUnits"] == 20000
    assert result.wins[1]["winMinorUnits"] == 1000


def test_fixed_multiplier_line_wins_only() -> None:
    config = parse_multiplier_config(
        {
            "mode": "fixed",
            "value": 3,
            "scope": "feature_frame",
            "applyTo": "line_wins_only",
        },
    )
    result = apply_multiplier(config, _sample_wins(), _FixedRNG([0]))
    assert result.wins[0]["winMinorUnits"] == 30000
    assert result.wins[1]["winMinorUnits"] == 500


def test_fixed_multiplier_feature_wins_only() -> None:
    config = parse_multiplier_config(
        {
            "mode": "fixed",
            "value": 4,
            "scope": "feature_frame",
            "applyTo": "feature_wins_only",
        },
    )
    result = apply_multiplier(config, _sample_wins(), _FixedRNG([0]))
    assert result.wins[0]["winMinorUnits"] == 10000
    assert result.wins[1]["winMinorUnits"] == 2000


def test_weighted_multiplier_is_deterministic() -> None:
    config = parse_multiplier_config(
        {
            "mode": "random_weighted",
            "value": 2,
            "scope": "feature_frame",
            "applyTo": "all_wins_in_frame",
            "weights": [1, 1, 8],
        },
    )
    service = RNGService()
    scope = service.new_chain_scope(b"multiplier-weighted", 0, "run", 0)
    rng_a = scope.frame_stream("f-0-0").multiplier_rng("mult.test", 0)
    rng_b = scope.frame_stream("f-0-0").multiplier_rng("mult.test", 0)
    result_a = apply_multiplier(config, _sample_wins(), rng_a)
    result_b = apply_multiplier(config, _sample_wins(), rng_b)
    assert result_a.factor == result_b.factor
    assert result_a.wins == result_b.wins


def test_weighted_multiplier_uses_value_scaled_ladder() -> None:
    config = parse_multiplier_config(
        {
            "mode": "random_weighted",
            "value": 2,
            "scope": "feature_frame",
            "applyTo": "all_wins_in_frame",
            "weights": [0, 0, 1],
        },
    )
    result = apply_multiplier(config, _sample_wins(), _FixedRNG([0]))
    assert result.factor == 6


def test_multiplier_plugin_apply_wins() -> None:
    plugin = MultiplierPlugin()
    result = plugin.apply_wins(
        {
            "mode": "fixed",
            "value": 5,
            "scope": "feature_frame",
            "applyTo": "all_wins_in_frame",
        },
        _sample_wins(),
        _FixedRNG([0]),
    )
    assert result.wins[0]["winMinorUnits"] == 50000
    assert result.frame_local_patch["multiplierFactor"] == 5


def test_invalid_mode_raises() -> None:
    with pytest.raises(PluginConfigurationError, match="unsupported multiplier mode"):
        parse_multiplier_config(
            {
                "mode": "unknown",
                "value": 1,
                "scope": "feature_frame",
                "applyTo": "all_wins_in_frame",
            },
        )


def test_random_weighted_requires_weights() -> None:
    with pytest.raises(PluginConfigurationError, match="requires weights"):
        parse_multiplier_config(
            {
                "mode": "random_weighted",
                "value": 2,
                "scope": "feature_frame",
                "applyTo": "all_wins_in_frame",
            },
        )

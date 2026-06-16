"""Additional Free Spins and counter helper coverage."""

from __future__ import annotations

import pytest

from runtime_core.plugins.contracts import CounterUpdateRequest, FeatureStepResult, PluginContext
from runtime_core.plugins.exceptions import PluginConfigurationError
from runtime_core.plugins.free_spins.config import parse_free_spins_config
from runtime_core.plugins.free_spins.lifecycle import finalize_step_result
from runtime_core.plugins.free_spins.retrigger import evaluate_retrigger
from runtime_core.plugins.bindings import plugin_game_bindings
from runtime_core.runtime.frames import new_frame_context
from runtime_core.runtime.plugins.counters import (
    apply_counter_updates,
    apply_step_side_effects,
)
from runtime_core.plugins.contracts import CounterUpdateRequest
from runtime_core.common.golden import load_golden_game_version


def test_parse_config_retrigger_disabled() -> None:
    config = parse_free_spins_config(
        {
            "reelSetId": "free_spins",
            "awardsByScatterCount": {"3": 10},
            "retrigger": {"enabled": False},
        },
    )
    assert config.retrigger is not None
    assert config.retrigger.enabled is False


def test_parse_config_empty_awards_raises() -> None:
    with pytest.raises(PluginConfigurationError, match="at least one entry"):
        parse_free_spins_config(
            {
                "reelSetId": "free_spins",
                "awardsByScatterCount": {},
            },
        )


def test_parse_config_retrigger_enabled_without_awards_raises() -> None:
    with pytest.raises(PluginConfigurationError, match="requires awardsByScatterCount"):
        parse_free_spins_config(
            {
                "reelSetId": "free_spins",
                "awardsByScatterCount": {"3": 10},
                "retrigger": {"enabled": True},
            },
        )


def test_finalize_step_result_forces_complete_at_max_steps() -> None:
    spin = FeatureStepResult(trigger_tokens=[])
    from runtime_core.plugins.free_spins.retrigger import RetriggerOutcome

    result = finalize_step_result(
        spin,
        spins_before=5,
        retrigger=RetriggerOutcome(award=0, emit_token=False, retrigger_count=0),
        max_steps=1,
        current_step_count=1,
    )
    assert "FEATURE_COMPLETE" in result.trigger_tokens
    assert result.counter_updates[-1].after == 0


def test_retrigger_disabled_returns_zero_award() -> None:
    game = load_golden_game_version("fixture-02-base-free-spins")
    bindings = plugin_game_bindings(game)
    config = parse_free_spins_config(
        {
            "reelSetId": "free_spins",
            "awardsByScatterCount": {"3": 10},
            "retrigger": {"enabled": False},
        },
    )
    outcome = evaluate_retrigger(
        config,
        bindings,
        scatter_count=3,
        current_retrigger_count=0,
    )
    assert outcome.award == 0


def test_apply_counter_updates_unsupported_field_raises() -> None:
    frame = new_frame_context()
    with pytest.raises(ValueError, match="unsupported counter field"):
        apply_counter_updates(
            frame,
            [CounterUpdateRequest(field="unknownCounter", after=1)],
        )


def test_apply_step_side_effects_applies_patch_and_counters() -> None:
    frame = new_frame_context()
    result = FeatureStepResult(
        frame_local_patch={"marker": True},
        counter_updates=[CounterUpdateRequest(field="spinsRemaining", after=7)],
    )
    effects = apply_step_side_effects(frame, result)
    assert frame.spins_remaining == 7
    assert frame.frame_local_state["marker"] is True
    assert effects.counter_events[0].before == 0
    assert effects.counter_events[0].after == 7


def test_parse_config_without_retrigger_block() -> None:
    config = parse_free_spins_config(
        {
            "reelSetId": "free_spins",
            "awardsByScatterCount": {"3": 10},
        },
    )
    assert config.retrigger is None


def test_parse_config_invalid_award_map_type_raises() -> None:
    with pytest.raises(PluginConfigurationError, match="award map must be an object"):
        parse_free_spins_config(
            {
                "reelSetId": "free_spins",
                "awardsByScatterCount": "bad",
            },
        )


def test_entry_scatter_count_from_entry_field_only() -> None:
    from runtime_core.plugins.contracts import PluginContext
    from runtime_core.plugins.free_spins.lifecycle import resolve_entry_scatter_count
    from runtime_core.runtime.frames import new_frame_context

    frame = new_frame_context()
    frame.frame_local_state["entryScatterCount"] = 5
    ctx = PluginContext(
        plugin_id="core.free-spins",
        plugin_version="1.0.0",
        config_schema_version="1.0.0",
        plugin_config={},
        frame_context=frame,
        rtp_category="FREE_SPINS",
        frame_id="f-0-0",
        machine_id="main",
        state_id="FREE_SPINS",
        plugin_ref_id="fs",
    )
    assert resolve_entry_scatter_count(ctx) == 5


def test_finalize_step_result_clamps_negative_spins() -> None:
    from runtime_core.plugins.free_spins.retrigger import RetriggerOutcome

    spin = FeatureStepResult(trigger_tokens=[])
    result = finalize_step_result(
        spin,
        spins_before=0,
        retrigger=RetriggerOutcome(award=0, emit_token=False, retrigger_count=0),
        max_steps=None,
        current_step_count=0,
    )
    assert result.counter_updates[-1].after == 0
    assert "FEATURE_COMPLETE" in result.trigger_tokens


def test_finalize_step_result_skips_duplicate_feature_complete_token() -> None:
    from runtime_core.plugins.free_spins.retrigger import RetriggerOutcome

    spin = FeatureStepResult(trigger_tokens=["FEATURE_COMPLETE"])
    result = finalize_step_result(
        spin,
        spins_before=1,
        retrigger=RetriggerOutcome(award=0, emit_token=False, retrigger_count=0),
        max_steps=None,
        current_step_count=0,
    )
    assert result.trigger_tokens.count("FEATURE_COMPLETE") == 1


def test_free_spins_plugin_metadata() -> None:
    from runtime_core.plugins.free_spins.plugin import FreeSpinsPlugin

    plugin = FreeSpinsPlugin()
    assert plugin.plugin_id == "core.free-spins"
    assert plugin.plugin_version == "1.0.0"
    plugin.on_exit(
        PluginContext(
            plugin_id="core.free-spins",
            plugin_version="1.0.0",
            config_schema_version="1.0.0",
            plugin_config={},
            frame_context=new_frame_context(),
            rtp_category="FREE_SPINS",
            frame_id="f-0-0",
            machine_id="main",
            state_id="FREE_SPINS",
            plugin_ref_id="fs",
        ),
    )

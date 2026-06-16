"""Plugin contract type tests."""

from __future__ import annotations

from runtime_core.plugins.contracts import FeatureStepResult, PluginContext


def test_feature_step_result_defaults() -> None:
    result = FeatureStepResult()
    assert result.trigger_tokens == []
    assert result.consume_step is True
    assert result.frame_local_patch == {}


def test_plugin_context_fields() -> None:
    from runtime_core.runtime.frames import new_frame_context

    ctx = PluginContext(
        plugin_id="core.base-game",
        plugin_version="1.0.0",
        config_schema_version="1.0.0",
        plugin_config={"k": "v"},
        frame_context=new_frame_context(),
        rtp_category="BASE",
        frame_id="f-0-0",
        machine_id="main",
        state_id="BASE",
        plugin_ref_id="base_main",
    )
    assert ctx.plugin_ref_id == "base_main"

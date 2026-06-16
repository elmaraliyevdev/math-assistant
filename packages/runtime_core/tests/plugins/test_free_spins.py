"""core.free-spins plugin tests."""

from __future__ import annotations

import pytest

from runtime_core.common.golden import load_golden_game_version
from runtime_core.domain.game_version import GameVersion
from runtime_core.plugins.bindings import plugin_game_bindings
from runtime_core.plugins.contracts import CounterUpdateRequest, FeatureStepResult
from runtime_core.plugins.exceptions import PluginConfigurationError
from runtime_core.plugins.free_spins.config import lookup_scatter_award, parse_free_spins_config
from runtime_core.plugins.free_spins.lifecycle import (
    build_enter_result,
    finalize_step_result,
    resolve_entry_scatter_count,
)
from runtime_core.plugins.free_spins.plugin import FreeSpinsPlugin
from runtime_core.plugins.free_spins.retrigger import evaluate_retrigger
from runtime_core.runtime.plugins.counters import apply_step_side_effects
from runtime_core.runtime.rng.service import RNGService
from tests.plugins.conftest import base_plugin_context


@pytest.fixture
def fs_game() -> GameVersion:
    return load_golden_game_version("fixture-02-base-free-spins")


def _fs_plugin_config(game: GameVersion) -> dict[str, object]:
    return dict(game.state_machines["main"].states["FREE_SPINS"].plugin_config or {})


def _fs_context(game: GameVersion):
    machine = game.state_machines["main"]
    state = machine.states["FREE_SPINS"]
    ref = game.plugins[state.plugin_ref_id]
    from runtime_core.runtime.frames import new_frame_context
    from runtime_core.runtime.stack import build_frame

    frame = build_frame(
        frame_id="f-0-0",
        machine_id="main",
        state=state,
        frame_context=new_frame_context(),
    )
    frame.frame_context.frame_local_state["scatterCounts"] = {"SCATTER": 3}
    from runtime_core.plugins.contracts import PluginContext

    return PluginContext(
        plugin_id=ref.plugin_id,
        plugin_version=ref.plugin_version,
        config_schema_version=ref.config_schema_version,
        plugin_config=_fs_plugin_config(game),
        frame_context=frame.frame_context,
        rtp_category="FREE_SPINS",
        frame_id=frame.frame_id,
        machine_id=frame.machine_id,
        state_id=frame.state_id,
        plugin_ref_id=ref.ref_id,
        game_bindings=plugin_game_bindings(game),
    )


def _step_rng(seed: bytes, frame_id: str = "f-0-0", step: int = 0):
    service = RNGService()
    scope = service.new_chain_scope(seed, 0, "fs-test", 0)
    return scope.frame_stream(frame_id).step_rng(step)


def test_initialization_awards_ten_spins_for_three_scatters(fs_game: GameVersion) -> None:
    ctx = _fs_context(fs_game)
    config = parse_free_spins_config(ctx.plugin_config)
    enter = build_enter_result(ctx, config)
    assert enter.counter_updates == [
        CounterUpdateRequest(field="spinsRemaining", after=10),
    ]


def test_on_enter_produces_enter_result(fs_game: GameVersion) -> None:
    plugin = FreeSpinsPlugin()
    ctx = _fs_context(fs_game)
    plugin.on_enter(ctx)
    enter = plugin.enter_result()
    assert enter is not None
    assert enter.counter_updates[0].after == 10


def test_apply_enter_result_sets_spins_remaining(fs_game: GameVersion) -> None:
    ctx = _fs_context(fs_game)
    config = parse_free_spins_config(ctx.plugin_config)
    enter = build_enter_result(ctx, config)
    apply_step_side_effects(ctx.frame_context, enter)
    assert ctx.frame_context.spins_remaining == 10
    assert ctx.frame_context.frame_local_state["fsInitialized"] is True


def test_spin_consumption_decrements_counter(fs_game: GameVersion) -> None:
    ctx = _fs_context(fs_game)
    config = parse_free_spins_config(ctx.plugin_config)
    apply_step_side_effects(ctx.frame_context, build_enter_result(ctx, config))
    plugin = FreeSpinsPlugin()
    before = ctx.frame_context.spins_remaining
    result = plugin.execute_step(ctx, _step_rng(b"fs-decrement", step=0))
    apply_step_side_effects(ctx.frame_context, result)
    assert ctx.frame_context.spins_remaining == before - 1


def test_feature_complete_emitted_when_spins_reach_zero(fs_game: GameVersion) -> None:
    ctx = _fs_context(fs_game)
    ctx.frame_context.spins_remaining = 1
    ctx.frame_context.frame_local_state["fsInitialized"] = True
    ctx.frame_context.frame_local_state["fsRetriggerCount"] = 0
    ctx.frame_context.frame_local_state["fsStepCount"] = 0
    plugin = FreeSpinsPlugin()
    result = plugin.execute_step(ctx, _step_rng(b"fs-complete", step=0))
    assert "FEATURE_COMPLETE" in result.trigger_tokens
    apply_step_side_effects(ctx.frame_context, result)
    assert ctx.frame_context.spins_remaining == 0


def test_retrigger_awards_additional_spins(fs_game: GameVersion) -> None:
    bindings = plugin_game_bindings(fs_game)
    config = parse_free_spins_config(_fs_plugin_config(fs_game))
    outcome = evaluate_retrigger(
        config,
        bindings,
        scatter_count=3,
        current_retrigger_count=0,
    )
    assert outcome.award == 5
    assert outcome.emit_token is True


def test_retrigger_respects_max_retriggers_per_feature(fs_game: GameVersion) -> None:
    bindings = plugin_game_bindings(fs_game)
    config = parse_free_spins_config(_fs_plugin_config(fs_game))
    outcome = evaluate_retrigger(
        config,
        bindings,
        scatter_count=3,
        current_retrigger_count=bindings.max_retriggers_per_feature or 0,
    )
    assert outcome.award == 0
    assert outcome.emit_token is False


def test_finalize_step_result_emits_retrigger_token() -> None:
    spin = FeatureStepResult(
        trigger_tokens=[],
        frame_local_patch={"scatterCounts": {"SCATTER": 3}},
    )
    from runtime_core.plugins.free_spins.retrigger import RetriggerOutcome

    result = finalize_step_result(
        spin,
        spins_before=10,
        retrigger=RetriggerOutcome(award=5, emit_token=True, retrigger_count=1),
        max_steps=500,
        current_step_count=0,
    )
    assert "RETRIGGER" in result.trigger_tokens
    assert result.counter_updates[-1].after == 14


def test_deterministic_free_spins_outcomes(fs_game: GameVersion) -> None:
    plugin = FreeSpinsPlugin()
    seed = b"fixture-02-determinism"

    def run_chain() -> list[dict[str, object] | None]:
        ctx = _fs_context(fs_game)
        apply_step_side_effects(
            ctx.frame_context,
            build_enter_result(ctx, parse_free_spins_config(ctx.plugin_config)),
        )
        grids: list[dict[str, object] | None] = []
        for step in range(3):
            result = plugin.execute_step(ctx, _step_rng(seed, step=step))
            apply_step_side_effects(ctx.frame_context, result)
            grids.append(result.grid_outcome)
        return grids

    assert run_chain() == run_chain()


def test_entry_scatter_count_required(fs_game: GameVersion) -> None:
    ctx = _fs_context(fs_game)
    ctx.frame_context.frame_local_state.clear()
    with pytest.raises(PluginConfigurationError, match="entry requires"):
        resolve_entry_scatter_count(ctx)


def test_lookup_scatter_award_exact_match() -> None:
    awards = {3: 10, 4: 15, 5: 20}
    assert lookup_scatter_award(awards, 4) == 15


def test_lookup_scatter_award_missing_raises() -> None:
    with pytest.raises(PluginConfigurationError):
        lookup_scatter_award({3: 10}, 2)


def test_execute_step_requires_game_bindings(fs_game: GameVersion) -> None:
    plugin = FreeSpinsPlugin()
    ctx = _fs_context(fs_game)
    ctx = type(ctx)(
        plugin_id=ctx.plugin_id,
        plugin_version=ctx.plugin_version,
        config_schema_version=ctx.config_schema_version,
        plugin_config=ctx.plugin_config,
        frame_context=ctx.frame_context,
        rtp_category=ctx.rtp_category,
        frame_id=ctx.frame_id,
        machine_id=ctx.machine_id,
        state_id=ctx.state_id,
        plugin_ref_id=ctx.plugin_ref_id,
        game_bindings=None,
    )
    with pytest.raises(PluginConfigurationError, match="game_bindings"):
        plugin.execute_step(ctx, _step_rng(b"x"))

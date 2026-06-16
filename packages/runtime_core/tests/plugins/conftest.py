"""Plugin implementation test helpers."""

from __future__ import annotations

import pytest

from runtime_core.common.golden import load_golden_game_version
from runtime_core.common.paths import game_schema_root
from runtime_core.domain.game_version import GameVersion
from runtime_core.domain.plugins import PluginRef
from runtime_core.plugins.bindings import plugin_game_bindings
from runtime_core.plugins.contracts import PluginContext
from runtime_core.runtime.frames import new_frame_context
from runtime_core.runtime.stack import build_frame
from runtime_core.validation.validators.priority_tiers import PriorityTierRegistry


@pytest.fixture
def base_game() -> GameVersion:
    return load_golden_game_version("fixture-01-base-5x3")


@pytest.fixture(scope="session")
def priority_tiers() -> PriorityTierRegistry:
    return PriorityTierRegistry.load(game_schema_root())


def base_state_plugin_config(game: GameVersion) -> dict[str, object]:
    machine = game.state_machines["main"]
    state = machine.states["BASE"]
    return dict(state.plugin_config or {})


def base_plugin_ref(game: GameVersion) -> PluginRef:
    machine = game.state_machines["main"]
    state = machine.states["BASE"]
    return game.plugins[state.plugin_ref_id]


def base_plugin_context(
    game: GameVersion,
    *,
    plugin_config: dict[str, object] | None = None,
) -> PluginContext:
    ref = base_plugin_ref(game)
    config = plugin_config if plugin_config is not None else base_state_plugin_config(game)
    frame = build_frame(
        frame_id="f-0-0",
        machine_id="main",
        state=game.state_machines["main"].states["BASE"],
        frame_context=new_frame_context(),
    )
    return PluginContext(
        plugin_id=ref.plugin_id,
        plugin_version=ref.plugin_version,
        config_schema_version=ref.config_schema_version,
        plugin_config=config,
        frame_context=frame.frame_context,
        rtp_category="BASE",
        frame_id=frame.frame_id,
        machine_id=frame.machine_id,
        state_id=frame.state_id,
        plugin_ref_id=ref.ref_id,
        game_bindings=plugin_game_bindings(game),
    )

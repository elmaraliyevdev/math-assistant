"""SessionExecutor unit tests."""

from __future__ import annotations

import pytest

from runtime_core.common.golden import load_golden_game_version
from runtime_core.domain.game_version import GameVersion
from runtime_core.plugins.exceptions import PluginNotImplementedError
from runtime_core.runtime.events import EventLogMode, EventType
from runtime_core.runtime.executor import SessionExecutor, SessionExecutorConfig
from runtime_core.runtime.plugins.registry import PluginRegistry
from runtime_core.runtime.spin_chain import SpinChainRequest
from runtime_core.validation.validators.priority_tiers import PriorityTierRegistry
from tests.runtime.conftest import session_test_game
from tests.runtime.executor.conftest import (
    make_spin_chain_request,
    relaxed_hold_and_win_game,
)


@pytest.fixture
def executor(priority_tiers: PriorityTierRegistry) -> SessionExecutor:
    return SessionExecutor(SessionExecutorConfig(priority_tiers=priority_tiers))


def test_execute_spin_chain_base_game_completes(
    base_game: GameVersion,
    executor: SessionExecutor,
) -> None:
    req = make_spin_chain_request(base_game, b"fixture-01-executor")
    result = executor.execute_spin_chain(req)

    assert result.fault is None
    assert result.limit_hit is None
    assert result.step_count >= 1
    assert result.frame_push_count == 0
    assert result.total_bet_minor_units > 0


def test_execute_spin_chain_deterministic_event_hash(
    base_game: GameVersion,
    executor: SessionExecutor,
) -> None:
    seed = b"determinism-check"
    req_a = make_spin_chain_request(base_game, seed)
    req_b = make_spin_chain_request(base_game, seed)

    hash_a = executor.execute_spin_chain(req_a).event_log_hash
    hash_b = executor.execute_spin_chain(req_b).event_log_hash

    assert hash_a
    assert hash_a == hash_b


def test_execute_spin_chain_emits_lifecycle_events(
    base_game: GameVersion,
    executor: SessionExecutor,
) -> None:
    req = make_spin_chain_request(
        base_game,
        b"events-check",
        event_log_mode=EventLogMode.FULL,
    )
    result = executor.execute_spin_chain(req)
    types = [event.event_type for event in result.events]

    assert EventType.SPIN_CHAIN_START in types
    assert EventType.SPIN_CHAIN_END in types
    assert EventType.STATE_ENTER in types
    assert EventType.TRANSITION_TAKEN in types


def test_runtime_step_limit(priority_tiers: PriorityTierRegistry) -> None:
    from runtime_core.common.golden import load_golden_game_version

    game = load_golden_game_version("fixture-02-base-free-spins")
    payload = game.to_json_dict()
    payload["session"]["runtimeLimits"] = {"maxStepsPerSpinChain": 2}
    limited = GameVersion.model_validate(payload)

    executor = SessionExecutor(
        SessionExecutorConfig(priority_tiers=priority_tiers),
    )
    for index in range(512):
        req = make_spin_chain_request(limited, b"step-limit-" + index.to_bytes(2, "big"))
        result = executor.execute_spin_chain(req)
        if result.limit_hit is not None:
            assert result.limit_hit.code == "MAX_STEPS_PER_SPIN_CHAIN"
            assert any(
                event.event_type == EventType.RUNTIME_LIMIT_HIT for event in result.events
            )
            return
    pytest.fail("expected MAX_STEPS_PER_SPIN_CHAIN within search budget")


def test_runtime_event_limit(base_game: GameVersion, priority_tiers) -> None:
    payload = base_game.to_json_dict()
    payload["session"]["runtimeLimits"] = {"maxEventsPerChain": 2}
    limited = GameVersion.model_validate(payload)

    req = make_spin_chain_request(limited, b"limit-events", event_log_mode=EventLogMode.FULL)
    result = SessionExecutor(
        SessionExecutorConfig(priority_tiers=priority_tiers),
    ).execute_spin_chain(req)

    assert result.limit_hit is not None
    assert result.limit_hit.code == "MAX_EVENTS_PER_CHAIN"


def test_plugin_fault_stops_chain(priority_tiers: PriorityTierRegistry) -> None:
    from runtime_core.plugins.manifest import BUILT_IN_PLUGINS

    game = session_test_game()
    registry = PluginRegistry()
    descriptor = next(d for d in BUILT_IN_PLUGINS if d.plugin_id == "core.base-game")
    registry.register(descriptor, _FaultFactory())
    executor = SessionExecutor(
        SessionExecutorConfig(priority_tiers=priority_tiers, plugin_registry=registry),
    )
    req = make_spin_chain_request(game, b"plugin-fault")
    result = executor.execute_spin_chain(req)

    assert result.fault is not None
    assert result.fault.code == "PLUGIN_FAULT"
    assert any(event.event_type == EventType.RUNTIME_FAULT for event in result.events)


class _FaultFactory:
    def create(self):
        return _FaultPlugin()


class _FaultPlugin:
    plugin_id = "core.base-game"
    plugin_version = "1.0.0"

    def on_enter(self, ctx):
        del ctx

    def execute_step(self, ctx, rng):
        del ctx, rng
        raise PluginNotImplementedError("injected fault")

    def on_exit(self, ctx):
        del ctx


def test_exposure_cap_accumulator(
    base_game: GameVersion,
    executor: SessionExecutor,
) -> None:
    payload = base_game.to_json_dict()
    payload["exposure"] = {
        "maxWinMinorUnits": 1,
        "maxWinMultiplier": 0,
        "capScope": "session_spin_chain",
        "enforceCap": True,
        "validationMode": "strict",
    }
    capped_game = GameVersion.model_validate(payload)
    req = make_spin_chain_request(capped_game, b"exposure-cap")
    result = executor.execute_spin_chain(req)

    assert result.total_win_minor_units <= 1
    assert result.accumulator_delta.exposure_truncation_count in {0, 1}


def test_exposure_cap_event_emitted(
    base_game: GameVersion,
    executor: SessionExecutor,
) -> None:
    payload = base_game.to_json_dict()
    payload["exposure"] = {
        "maxWinMinorUnits": 1,
        "maxWinMultiplier": 0,
        "capScope": "session_spin_chain",
        "enforceCap": True,
        "validationMode": "strict",
    }
    payload["stateMachines"]["main"]["states"]["BASE"]["pluginConfig"]["scatterTriggers"] = []
    capped = GameVersion.model_validate(payload)
    for index in range(64):
        result = executor.execute_spin_chain(
            make_spin_chain_request(capped, b"cap-event-" + index.to_bytes(2, "big")),
        )
        if any(event.event_type == EventType.EXPOSURE_CAP_APPLIED for event in result.events):
            return
    pytest.skip("no seed produced capped wins in search budget")


def test_frame_push_limit(base_game: GameVersion, priority_tiers: PriorityTierRegistry) -> None:
    game = relaxed_hold_and_win_game("fixture-03-base-hold-win")
    payload = game.to_json_dict()
    payload["session"]["runtimeLimits"] = {"maxFramesPerChain": 0}
    payload["session"]["maxStackDepth"] = 1
    limited = GameVersion.model_validate(payload)
    executor = SessionExecutor(SessionExecutorConfig(priority_tiers=priority_tiers))
    for index in range(256):
        req = make_spin_chain_request(limited, b"frame-limit-" + index.to_bytes(2, "big"))
        result = executor.execute_spin_chain(req)
        if result.fault is not None and result.fault.code == "MAX_STACK_DEPTH":
            return
    pytest.fail("expected MAX_STACK_DEPTH fault")


def test_multiplier_applied_when_configured(
    base_game: GameVersion,
    priority_tiers: PriorityTierRegistry,
) -> None:
    payload = base_game.to_json_dict()
    payload["extensions"] = {
        "multiplierConfigs": {
            "mult_base": {
                "mode": "fixed",
                "value": 2,
                "scope": "frame",
                "applyTo": "all_wins_in_frame",
            },
        },
    }
    payload["stateMachines"]["main"]["states"]["BASE"]["pluginConfig"]["multiplierRefId"] = (
        "mult_base"
    )
    payload["stateMachines"]["main"]["states"]["BASE"]["pluginConfig"]["scatterTriggers"] = []
    game = GameVersion.model_validate(payload)
    executor = SessionExecutor(SessionExecutorConfig(priority_tiers=priority_tiers))
    for index in range(64):
        req = make_spin_chain_request(game, b"mult-" + index.to_bytes(2, "big"))
        result = executor.execute_spin_chain(req)
        if result.fault is None and any(
            event.event_type == EventType.MULTIPLIER_APPLIED for event in result.events
        ):
            return
    pytest.skip("no seed produced wins with multiplier in search budget")


def test_module_level_execute_spin_chain(base_game: GameVersion) -> None:
    from runtime_core.runtime.executor import execute_spin_chain

    req = make_spin_chain_request(base_game, b"module-fn")
    result = execute_spin_chain(req)
    assert result.fault is None

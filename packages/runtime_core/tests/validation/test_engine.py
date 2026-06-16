"""Validation Engine integration tests."""

from __future__ import annotations

import pytest
from tests.validation.conftest import build_nested_fs_haw, build_valid_base_game

from runtime_core.common.golden import load_golden_game_version
from runtime_core.domain.state_machine import Transition
from runtime_core.validation import VALIDATOR_VERSION, ValidationCancelledError
from runtime_core.validation.engine import ValidationEngine
from runtime_core.validation.exposure_validator import ExposureValidator
from runtime_core.validation.limits_validator import LimitsValidator
from runtime_core.validation.plugin_validator import PluginValidator
from runtime_core.validation.schema_paths import default_schema_paths


def test_valid_base_game(validation_engine: ValidationEngine) -> None:
    report = validation_engine.validate(build_valid_base_game())
    assert report.valid, report.errors
    assert report.metadata.validator_version == VALIDATOR_VERSION


def test_valid_nested_fs_haw(validation_engine: ValidationEngine) -> None:
    report = validation_engine.validate(build_nested_fs_haw())
    assert report.valid, report.errors


@pytest.mark.golden
@pytest.mark.parametrize(
    "fixture_id",
    ["fixture-01-base-5x3", "fixture-04-nested-fs-hold-win"],
)
def test_golden_fixtures_validate(
    validation_engine: ValidationEngine,
    fixture_id: str,
) -> None:
    game = load_golden_game_version(fixture_id)
    report = validation_engine.validate(game)
    assert report.valid, report.errors


def test_invalid_transition_target(validation_engine: ValidationEngine) -> None:
    game = build_valid_base_game()
    base = game.state_machines["main"].states["BASE"]
    base.transitions = [
        Transition.model_validate(
            {
                "id": "t_bad",
                "trigger": "SPIN_COMPLETE",
                "priorityTier": "FALLBACK",
                "priority": 1000,
                "effect": "goto",
                "targetStateId": "MISSING",
            },
        ),
    ]
    report = validation_engine.validate(game)
    assert not report.valid
    assert report.has_code("GV-003")


def test_orphan_states(validation_engine: ValidationEngine) -> None:
    game = build_valid_base_game()
    game.state_machines["main"].states["ORPHAN"] = base_state_with_stay("ORPHAN")
    report = validation_engine.validate(game)
    assert not report.valid
    assert report.has_code("GV-005")


def test_stack_depth_exceeded(validation_engine: ValidationEngine) -> None:
    game = build_nested_fs_haw()
    game.session.max_stack_depth = 1
    report = validation_engine.validate(game)
    assert not report.valid
    assert report.has_code("GV-012")


def test_schema_validation_stops_pipeline(validation_engine: ValidationEngine) -> None:
    game = build_valid_base_game()
    game.schema_version = ""
    report = validation_engine.validate(game)
    assert not report.valid
    assert report.errors[0].code.startswith("SV-")


def test_exposure_cap_exceeded(validation_engine: ValidationEngine) -> None:
    game = build_valid_base_game()
    game.exposure.max_win_minor_units = 100
    game.exposure.max_win_multiplier = 1
    report = validation_engine.validate(game)
    assert not report.valid
    assert report.has_code("GV-023")


def test_limits_respins_exceeded(validation_engine: ValidationEngine) -> None:
    game = build_nested_fs_haw()
    assert game.session.runtime_limits is not None
    game.session.runtime_limits.max_respins_per_feature = 1
    report = validation_engine.validate(game)
    assert not report.valid
    assert report.has_code("GV-037")


def test_plugin_ref_missing(validation_engine: ValidationEngine) -> None:
    game = build_valid_base_game()
    game.state_machines["main"].states["BASE"].plugin_ref_id = "missing_plugin"
    report = validation_engine.validate(game)
    assert not report.valid
    assert report.has_code("GV-018")


def test_invalid_pop_transition(validation_engine: ValidationEngine) -> None:
    game = build_valid_base_game()
    game.state_machines["main"].states["BASE"].transitions.append(
        Transition.model_validate(
            {
                "id": "bad_pop",
                "trigger": "FEATURE_COMPLETE",
                "priorityTier": "FEATURE_EXIT",
                "priority": 900,
                "effect": "pop",
                "targetStateId": "BASE",
            },
        ),
    )
    report = validation_engine.validate(game)
    assert not report.valid
    assert report.has_code("GV-010")


def test_priority_out_of_range(validation_engine: ValidationEngine) -> None:
    game = build_valid_base_game()
    game.state_machines["main"].states["BASE"].transitions = [
        Transition.model_validate(
            {
                "id": "t1",
                "trigger": "SPIN_COMPLETE",
                "priorityTier": "FALLBACK",
                "priority": 50,
                "effect": "stay",
                "targetStateId": "BASE",
            },
        ),
    ]
    report = validation_engine.validate(game)
    assert not report.valid
    assert report.has_code("GV-027")


def test_limits_frames_exceed_stack(validation_engine: ValidationEngine) -> None:
    game = build_valid_base_game()
    assert game.session.runtime_limits is not None
    game.session.runtime_limits.max_frames_per_chain = 10
    report = validation_engine.validate(game)
    assert not report.valid
    assert report.has_code("GV-036")


def test_unsupported_plugin_version(validation_engine: ValidationEngine) -> None:
    game = build_valid_base_game()
    plugin = game.plugins["base_main"]
    game.plugins["base_main"] = plugin.model_copy(update={"plugin_version": "9.9.9"})
    report = validation_engine.validate(game)
    assert not report.valid
    assert report.has_code("GV-019")


def test_engine_nil_game(validation_engine: ValidationEngine) -> None:
    with pytest.raises(ValueError, match="game is nil"):
        validation_engine.validate(None)


def test_validation_cancelled(validation_engine: ValidationEngine) -> None:
    with pytest.raises(ValidationCancelledError):
        validation_engine.validate(build_valid_base_game(), should_cancel=lambda: True)


def test_exposure_validator_direct() -> None:
    game = build_valid_base_game()
    game.exposure.cap_scope = "not_valid"
    report = ExposureValidator().validate(game)
    assert not report.valid
    assert report.has_code("GV-023")


def test_limits_validator_nil() -> None:
    assert LimitsValidator().validate(None).valid


def test_plugin_validator_nil() -> None:
    assert PluginValidator(None, None).validate(None).valid


def test_default_schema_paths_env(monkeypatch: pytest.MonkeyPatch) -> None:
    from runtime_core.common.paths import resolve_game_schema_root

    root = resolve_game_schema_root()
    monkeypatch.setenv("MATH_ASSISTANT_SCHEMA_ROOT", str(root))
    paths = default_schema_paths()
    assert paths.game_schema.is_file()


def base_state_with_stay(state_id: str):
    from runtime_core.domain.state_machine import State

    return State.model_validate(
        {
            "id": state_id,
            "pluginRefId": "base_main",
            "stateType": "atomic_spin",
            "rtpCategory": "BASE",
            "pluginConfig": {"reelSetId": "base_game"},
            "transitions": [
                {
                    "id": "t_stay",
                    "trigger": "SPIN_COMPLETE",
                    "priorityTier": "FALLBACK",
                    "priority": 1000,
                    "effect": "stay",
                    "targetStateId": state_id,
                },
            ],
        },
    )

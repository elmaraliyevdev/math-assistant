"""Additional graph and pipeline edge-case tests."""

from __future__ import annotations

from tests.validation.conftest import build_valid_base_game

from runtime_core.domain.state_machine import State, Transition
from runtime_core.validation.engine import ValidationEngine
from runtime_core.validation.exposure_validator import ExposureValidator
from runtime_core.validation.schema_paths import default_schema_paths
from runtime_core.validation.validators.priority_tiers import PriorityTierRegistry
from runtime_core.validation.validators.progression_validator import (
    validate_progression,
)
from runtime_core.validation.validators.state_machine_validator import (
    validate_state_machines,
)
from runtime_core.validation.validators.transition_validator import validate_transitions


def test_infinite_loop_detection(validation_engine: ValidationEngine) -> None:
    game = build_valid_base_game()
    game.symbols["BONUS"] = {"id": "BONUS", "type": "bonus", "pays": False}
    game.plugins["haw_main"] = game.plugins["base_main"].model_copy(
        update={
            "ref_id": "haw_main",
            "plugin_id": "core.hold-and-win",
            "capabilities": ["spin.grid", "state.multistep", "jackpot.local"],
        },
    )
    game.state_machines["main"].states["LOOP"] = State.model_validate(
        {
            "id": "LOOP",
            "pluginRefId": "haw_main",
            "stateType": "multi_step",
            "rtpCategory": "HOLD_AND_WIN",
            "pluginConfig": {
                "reelSetId": "base_game",
                "triggerSymbolId": "BONUS",
                "triggerSymbolCount": 6,
                "initialRespins": 3,
                "gridCapacity": 15,
            },
            "transitions": [
                {
                    "id": "t_loop",
                    "trigger": "SPIN_COMPLETE",
                    "priorityTier": "FALLBACK",
                    "priority": 1000,
                    "effect": "stay",
                    "targetStateId": "LOOP",
                },
            ],
        },
    )
    report = validation_engine.validate(game)
    assert not report.valid
    assert report.has_code("GV-011")


def test_invalid_plugin_configuration(validation_engine: ValidationEngine) -> None:
    game = build_valid_base_game()
    game.state_machines["main"].states["BASE"].plugin_config = {
        "reelSetId": "base_game",
        "scatterTriggers": [
            {"symbolId": "SCATTER", "minCount": "three", "emitTrigger": "FREE_SPINS"},
        ],
    }
    report = validation_engine.validate(game)
    assert not report.valid


def test_duplicate_transition_id(validation_engine: ValidationEngine) -> None:
    game = build_valid_base_game()
    transition = game.state_machines["main"].states["BASE"].transitions[0]
    game.state_machines["main"].states["BASE"].transitions = [transition, transition]
    report = validation_engine.validate(game)
    assert not report.valid
    assert report.has_code("GV-013")


def test_exposure_multiplier_zero() -> None:
    game = build_valid_base_game()
    game.exposure.max_win_multiplier = 0
    report = ExposureValidator().validate(game)
    assert not report.valid
    assert report.has_code("GV-023")


def test_transition_priority_conflict_warning() -> None:
    game = build_valid_base_game()
    base = game.state_machines["main"].states["BASE"]
    base.transitions = [
        Transition.model_validate(
            {
                "id": "t_a",
                "trigger": "SPIN_COMPLETE",
                "priorityTier": "FALLBACK",
                "priority": 1000,
                "effect": "stay",
                "targetStateId": "BASE",
            },
        ),
        Transition.model_validate(
            {
                "id": "t_b",
                "trigger": "SPIN_COMPLETE",
                "priorityTier": "FALLBACK",
                "priority": 1000,
                "effect": "goto",
                "targetStateId": "BASE",
            },
        ),
    ]
    tiers = PriorityTierRegistry.load(default_schema_paths().game_schema.parent.parent)
    findings = validate_transitions(game, tiers)
    codes = [finding.code for finding in findings]
    assert "GV-016" in codes
    assert "GV-017" in codes


def test_state_machine_missing_initial() -> None:
    game = build_valid_base_game()
    game.state_machines["main"].initial_state_id = ""
    findings = validate_state_machines(game)
    assert any(f.code == "GV-001" for f in findings)


def test_progression_validator_direct() -> None:
    assert validate_progression(None) == []

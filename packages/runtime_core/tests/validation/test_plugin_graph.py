"""Plugin reference and graph edge coverage tests."""

from __future__ import annotations

from tests.validation.conftest import build_nested_fs_haw, build_valid_base_game

from runtime_core.domain.state_machine import State
from runtime_core.validation.engine import ValidationEngine
from runtime_core.validation.validators.plugin_config_validator import (
    validate_plugin_references,
)
from runtime_core.validation.validators.reachability_validator import (
    validate_reachability,
)


def test_reel_count_mismatch(validation_engine: ValidationEngine) -> None:
    game = build_valid_base_game()
    game.reel_sets["base_game"].reels = game.reel_sets["base_game"].reels[:3]
    report = validation_engine.validate(game)
    assert not report.valid
    assert report.has_code("GV-022")


def test_dead_end_non_terminal_state(validation_engine: ValidationEngine) -> None:
    game = build_valid_base_game()
    game.state_machines["main"].states["DEAD"] = State.model_validate(
        {
            "id": "DEAD",
            "pluginRefId": "base_main",
            "stateType": "atomic_spin",
            "rtpCategory": "BASE",
            "pluginConfig": {"reelSetId": "base_game"},
            "transitions": [],
        },
    )
    game.state_machines["main"].states["BASE"].transitions.append(
        game.state_machines["main"]
        .states["BASE"]
        .transitions[0]
        .model_copy(
            update={"id": "to_dead", "effect": "goto", "targetStateId": "DEAD"},
        ),
    )
    report = validation_engine.validate(game)
    assert not report.valid
    assert report.has_code("GV-006")


def test_spawn_machine_without_pop(validation_engine: ValidationEngine) -> None:
    game = build_nested_fs_haw()
    game.state_machines["hold_and_win"].states["HAW_RESPINS"].transitions = []
    report = validation_engine.validate(game)
    assert not report.valid
    assert report.has_code("GV-008")


def test_rtp_category_unknown(validation_engine: ValidationEngine) -> None:
    game = build_valid_base_game()
    game.state_machines["main"].states["BASE"].rtp_category = "NOT_A_CATEGORY"
    report = validation_engine.validate(game)
    assert not report.valid
    assert report.has_code("GV-025")


def test_plugin_reference_symbol_and_multiplier_paths() -> None:
    game = build_valid_base_game()
    game.state_machines["main"].states["BASE"].plugin_config = {
        "reelSetId": "missing_reel",
        "triggerSymbolId": "NOPE",
        "multiplierRefId": "missing_mult",
        "scatterTriggers": [{"symbolId": "NOPE", "minCount": 3, "emitTrigger": "X"}],
    }
    findings = validate_plugin_references(game)
    codes = {finding.code for finding in findings}
    assert "GV-021" in codes
    assert "GV-018" in codes


def test_reachability_with_missing_root_machine() -> None:
    game = build_valid_base_game()
    game.session.root_machine_id = "missing"
    findings = validate_reachability(game)
    assert any(f.code == "GV-005" for f in findings)

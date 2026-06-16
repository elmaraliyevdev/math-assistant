"""State machine validator edge cases."""

from tests.validation.conftest import build_valid_base_game

from runtime_core.domain.state_machine import StateMachine
from runtime_core.validation.validators.state_machine_validator import (
    validate_state_machines,
)


def test_duplicate_machine_id_key_mismatch() -> None:
    game = build_valid_base_game()
    game.state_machines["other"] = StateMachine.model_validate(
        {
            "id": "main",
            "initialStateId": "BASE",
            "states": game.state_machines["main"].states,
        },
    )
    findings = validate_state_machines(game)
    assert any(f.code == "GV-015" for f in findings)


def test_duplicate_state_id_in_machine() -> None:
    game = build_valid_base_game()
    base = game.state_machines["main"].states["BASE"]
    game.state_machines["main"].states["ALIAS"] = base.model_copy(update={"id": "BASE"})
    findings = validate_state_machines(game)
    assert any(f.code == "GV-014" for f in findings)


def test_validate_state_machines_nil() -> None:
    assert validate_state_machines(None) == []

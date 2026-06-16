"""Schema validator unit tests."""

from __future__ import annotations

import pytest
from jsonschema.exceptions import ValidationError

from runtime_core.validation.schema_paths import default_schema_paths
from runtime_core.validation.schema_validator import SchemaValidator, map_schema_error


@pytest.fixture(scope="module")
def schema_validator() -> SchemaValidator:
    paths = default_schema_paths()
    return SchemaValidator(
        game_schema=paths.game_schema,
        plugin_schema_dir=paths.plugin_schema_dir,
    )


def test_validate_invalid_json(schema_validator: SchemaValidator) -> None:
    report = schema_validator.validate_game_bytes(b"{not json")
    assert not report.valid
    assert report.errors[0].code == "SV-002"


def test_validate_missing_required_field(schema_validator: SchemaValidator) -> None:
    report = schema_validator.validate_game_dict({"schemaVersion": "1.0.0"})
    assert not report.valid
    assert any(error.code == "SV-001" for error in report.errors)


def test_validate_plugin_config_valid(schema_validator: SchemaValidator) -> None:
    findings = schema_validator.validate_plugin_config(
        "core.base-game",
        "1.0.0",
        {"reelSetId": "base_game"},
    )
    assert findings == []


def test_validate_plugin_config_invalid_type(schema_validator: SchemaValidator) -> None:
    findings = schema_validator.validate_plugin_config(
        "core.base-game",
        "1.0.0",
        {
            "reelSetId": "base_game",
            "scatterTriggers": [
                {"symbolId": "SCATTER", "minCount": "three", "emitTrigger": "X"}
            ],
        },
    )
    assert findings
    assert findings[0].code == "GV-021"


def test_validate_unsupported_plugin_schema_version(
    schema_validator: SchemaValidator,
) -> None:
    findings = schema_validator.validate_plugin_config("core.base-game", "9.9.9", {})
    assert any(f.code == "GV-019" for f in findings)


def test_map_schema_error_branches() -> None:
    error = ValidationError("'x' is a required property")
    assert map_schema_error(error).code == "SV-001"
    error = ValidationError("None is not of type 'string'")
    assert map_schema_error(error).code == "SV-002"
    error = ValidationError("'bad' is not one of ['a', 'b']")
    assert map_schema_error(error).code == "SV-003"
    error = ValidationError("'abc' does not match '^[0-9]+$' pattern")
    assert map_schema_error(error).code == "SV-004"
    error = ValidationError("10 is less than the minimum of 20")
    assert map_schema_error(error).code == "SV-005"
    error = ValidationError(
        "Additional properties are not allowed ('extra' was unexpected)"
    )
    assert map_schema_error(error).code == "SV-006"

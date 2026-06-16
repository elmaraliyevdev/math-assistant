"""JSON Schema validation (SV-*)."""

from __future__ import annotations

import json
from hashlib import sha256
from pathlib import Path
from typing import Any

from jsonschema import Draft202012Validator
from jsonschema.exceptions import ValidationError

from runtime_core.validation.issues import (
    schema_additional_property,
    schema_enum,
    schema_generic,
    schema_invalid_json,
    schema_pattern,
    schema_range,
    schema_required,
    schema_type,
)
from runtime_core.validation.report import ValidationFinding, ValidationReport

_PLUGIN_SCHEMA_FILES: dict[tuple[str, str], str] = {
    ("core.base-game", "1.0.0"): "base-game-1.0.0.schema.json",
    ("core.free-spins", "1.0.0"): "free-spins-1.0.0.schema.json",
    ("core.hold-and-win", "1.0.0"): "hold-and-win-1.0.0.schema.json",
    ("core.multiplier", "1.0.0"): "multiplier-1.0.0.schema.json",
}


def content_hash(raw: bytes) -> str:
    return sha256(raw).hexdigest()


class SchemaValidator:
    """Validates raw JSON against game-version-1.0.0.schema.json."""

    def __init__(self, *, game_schema: Path, plugin_schema_dir: Path) -> None:
        if not game_schema.is_file():
            msg = f"game schema not found: {game_schema}"
            raise FileNotFoundError(msg)
        self._plugin_dir = plugin_schema_dir
        self._game_validator = self._load_validator(game_schema)
        self._plugin_cache: dict[str, Draft202012Validator] = {}

    @staticmethod
    def _load_validator(schema_path: Path) -> Draft202012Validator:
        schema = json.loads(schema_path.read_text(encoding="utf-8"))
        return Draft202012Validator(schema)

    def validate_game_bytes(self, raw: bytes) -> ValidationReport:
        report = ValidationReport.empty(content_hash=content_hash(raw))
        try:
            doc = json.loads(raw)
        except json.JSONDecodeError as exc:
            report.add_error(schema_invalid_json(str(exc)))
            return report
        if not isinstance(doc, dict):
            report.add_error(schema_invalid_json("root must be a JSON object"))
            return report
        self._validate_document(doc, report)
        return report

    def validate_game_dict(self, doc: dict[str, Any]) -> ValidationReport:
        raw = json.dumps(doc, sort_keys=True).encode("utf-8")
        report = ValidationReport.empty(content_hash=content_hash(raw))
        self._validate_document(doc, report)
        return report

    def _validate_document(self, doc: dict[str, Any], report: ValidationReport) -> None:
        for error in sorted(self._game_validator.iter_errors(doc), key=_error_sort_key):
            report.add_error(map_schema_error(error))

    def validate_plugin_config(
        self,
        plugin_id: str,
        config_schema_version: str,
        config: dict[str, Any] | None,
    ) -> list[ValidationFinding]:
        from runtime_core.validation.issues import (
            graph_plugin_config_invalid,
            graph_plugin_version_unsupported,
        )

        if config is None:
            return []
        schema_file = _PLUGIN_SCHEMA_FILES.get((plugin_id, config_schema_version))
        if schema_file is None:
            return [
                graph_plugin_version_unsupported("", plugin_id, config_schema_version),
            ]
        try:
            validator = self._load_plugin_validator(schema_file)
        except OSError as exc:
            return [graph_plugin_config_invalid("pluginConfig", str(exc))]
        findings: list[ValidationFinding] = []
        for error in validator.iter_errors(config):
            collect_plugin_schema_errors(findings, "pluginConfig", error)
        if not findings and not validator.is_valid(config):
            findings.append(
                graph_plugin_config_invalid("pluginConfig", "invalid config")
            )
        return findings

    def _load_plugin_validator(self, filename: str) -> Draft202012Validator:
        cached = self._plugin_cache.get(filename)
        if cached is not None:
            return cached
        path = self._plugin_dir / filename
        validator = self._load_validator(path)
        self._plugin_cache[filename] = validator
        return validator


def map_schema_error(error: ValidationError) -> ValidationFinding:
    path = json_pointer_path(list(error.absolute_path))
    message = error.message
    lower = message.lower()
    if "is a required property" in lower or "required" in lower:
        return schema_required(path, message)
    if "does not match" in lower and "pattern" in lower:
        return schema_pattern(path)
    if "is not one of" in lower or "enum" in lower:
        return schema_enum(path, message)
    if "additional properties" in lower:
        prop = _extract_additional_property(message)
        return schema_additional_property(path, prop)
    if "is not of type" in lower:
        return schema_type(path, message)
    if any(
        token in lower
        for token in (
            "minimum",
            "maximum",
            "minlength",
            "maxlength",
            "less than",
            "greater",
        )
    ):
        return schema_range(path, message)
    return schema_generic(path, message)


def collect_plugin_schema_errors(
    findings: list[ValidationFinding],
    base_path: str,
    error: ValidationError,
) -> None:
    from runtime_core.validation.issues import graph_plugin_config_invalid

    rel = ".".join(str(part) for part in error.absolute_path)
    path = f"{base_path}.{rel}" if rel else base_path
    findings.append(graph_plugin_config_invalid(path, error.message))
    for cause in error.context:
        collect_plugin_schema_errors(findings, base_path, cause)


def json_pointer_path(parts: list[str | int]) -> str:
    if not parts:
        return "$"
    rendered = ".".join(str(part) for part in parts)
    return f"$.{rendered}"


def _error_sort_key(error: ValidationError) -> tuple[str, ...]:
    return tuple(str(part) for part in error.absolute_path)


def _extract_additional_property(message: str) -> str:
    marker = "'"
    if marker not in message:
        return message
    parts = message.split(marker)
    if len(parts) >= 2:
        return parts[1]
    return message

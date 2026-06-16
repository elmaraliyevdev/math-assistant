"""Game validation service — ValidationEngine public API only."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from pydantic import ValidationError
from runtime_core.runtime import ENGINE_VERSION
from runtime_core.validation import ValidationEngine, ValidationReport

from app.adapters.game_version import compute_content_hash, parse_game_version
from app.exceptions.engine import EngineVersionMismatchError
from app.schemas.games import (
    ReadyResponse,
    ValidateGameFailureResponse,
    ValidateGameSuccessResponse,
    ValidationFindingResponse,
    ValidationReportMetadataResponse,
    ValidationReportResponse,
)


@dataclass(frozen=True, slots=True)
class ValidationService:
    validation_engine: ValidationEngine

    @classmethod
    def create(cls) -> ValidationService:
        return cls(validation_engine=ValidationEngine.create())

    def ready(self) -> ReadyResponse:
        return ReadyResponse(ready=True, engine_version=ENGINE_VERSION)

    def validate(
        self,
        *,
        canonical_json: dict[str, Any],
        engine_version: str,
    ) -> ValidateGameSuccessResponse | ValidateGameFailureResponse:
        if engine_version != ENGINE_VERSION:
            raise EngineVersionMismatchError(
                requested=engine_version,
                deployed=ENGINE_VERSION,
            )

        content_hash = compute_content_hash(canonical_json)
        try:
            game = parse_game_version(canonical_json)
        except ValidationError:
            return ValidateGameFailureResponse(
                content_hash=content_hash,
                report=ValidationReportResponse(
                    passed=False,
                    findings=[
                        ValidationFindingResponse(
                            code="CANONICAL_JSON_INVALID",
                            severity="error",
                            message=(
                                "canonical JSON is not a valid "
                                "GameVersion document"
                            ),
                            path="/",
                        ),
                    ],
                ),
            )
        report = self.validation_engine.validate(game)
        schema_version = _schema_version(canonical_json)
        api_report = _to_api_report(report, schema_version=schema_version)

        if report.valid:
            return ValidateGameSuccessResponse(
                content_hash=content_hash,
                engine_version=ENGINE_VERSION,
                report=api_report,
            )
        return ValidateGameFailureResponse(
            content_hash=content_hash,
            report=ValidationReportResponse(
                passed=False,
                findings=api_report.findings,
            ),
        )


def _schema_version(canonical_json: dict[str, Any]) -> str:
    value = canonical_json.get("schemaVersion")
    if isinstance(value, str) and value:
        return value
    return "1.0.0"


def _to_api_report(
    report: ValidationReport,
    *,
    schema_version: str,
    include_metadata: bool = True,
) -> ValidationReportResponse:
    findings = [
        ValidationFindingResponse(
            code=finding.code,
            severity=finding.severity.value,
            message=finding.message,
            path=finding.path,
            suggestion=finding.suggestion,
        )
        for finding in (*report.errors, *report.warnings)
    ]
    metadata = None
    if include_metadata:
        metadata = ValidationReportMetadataResponse(
            validator_version=report.metadata.validator_version,
            schema_version=schema_version,
        )
    return ValidationReportResponse(
        passed=report.valid,
        findings=findings,
        metadata=metadata,
    )

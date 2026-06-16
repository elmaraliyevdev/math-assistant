"""Validation report models."""

from __future__ import annotations

from datetime import UTC, datetime
from enum import StrEnum

from pydantic import BaseModel, ConfigDict, Field

VALIDATOR_VERSION = "validation-engine@1.0.0"


class Severity(StrEnum):
    ERROR = "error"
    WARNING = "warning"


class ValidationFinding(BaseModel):
    """Single schema or graph validation finding."""

    model_config = ConfigDict(extra="forbid")

    code: str
    severity: Severity
    path: str
    message: str
    suggestion: str | None = None


class ValidationMetadata(BaseModel):
    """Report provenance."""

    model_config = ConfigDict(extra="forbid", populate_by_name=True)

    validator_version: str = Field(alias="validatorVersion")
    timestamp: datetime
    game_content_hash: str | None = Field(default=None, alias="gameContentHash")


class ValidationReport(BaseModel):
    """Aggregated validation outcomes."""

    model_config = ConfigDict(extra="forbid")

    valid: bool = True
    errors: list[ValidationFinding] = Field(default_factory=list)
    warnings: list[ValidationFinding] = Field(default_factory=list)
    metadata: ValidationMetadata

    @classmethod
    def empty(cls, *, content_hash: str = "") -> ValidationReport:
        return cls(
            metadata=ValidationMetadata(
                validator_version=VALIDATOR_VERSION,
                timestamp=datetime.now(tz=UTC),
                game_content_hash=content_hash or None,
            ),
        )

    def add_error(self, finding: ValidationFinding) -> None:
        self.errors.append(finding.model_copy(update={"severity": Severity.ERROR}))
        self.valid = False

    def add_warning(self, finding: ValidationFinding) -> None:
        self.warnings.append(finding.model_copy(update={"severity": Severity.WARNING}))

    def merge(self, other: ValidationReport | None) -> None:
        if other is None:
            return
        for finding in other.errors:
            self.add_error(finding.model_copy(deep=True))
        for finding in other.warnings:
            self.add_warning(finding.model_copy(deep=True))

    def has_errors(self) -> bool:
        return len(self.errors) > 0

    def has_code(self, code: str) -> bool:
        return any(f.code == code for f in self.errors) or any(
            f.code == code for f in self.warnings
        )

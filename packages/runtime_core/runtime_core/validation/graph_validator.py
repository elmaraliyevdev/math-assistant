"""Graph-level static analysis (GV-*)."""

from __future__ import annotations

from runtime_core.domain.game_version import GameVersion
from runtime_core.validation.report import Severity, ValidationFinding, ValidationReport
from runtime_core.validation.validators.finding import Finding
from runtime_core.validation.validators.priority_tiers import PriorityTierRegistry
from runtime_core.validation.validators.progression_validator import (
    validate_progression,
)
from runtime_core.validation.validators.reachability_validator import (
    validate_reachability,
)
from runtime_core.validation.validators.stack_depth_validator import (
    validate_stack_depth,
)
from runtime_core.validation.validators.state_machine_validator import (
    validate_state_machines,
)
from runtime_core.validation.validators.transition_validator import validate_transitions


class GraphValidator:
    def __init__(self, tiers: PriorityTierRegistry) -> None:
        self._tiers = tiers

    def validate(self, game: GameVersion | None) -> ValidationReport:
        report = ValidationReport.empty()
        if game is None:
            return report
        _add_findings(report, validate_state_machines(game))
        _add_findings(report, validate_transitions(game, self._tiers))
        _add_findings(report, validate_reachability(game))
        _add_findings(report, validate_stack_depth(game))
        _add_findings(report, validate_progression(game))
        return report


def _add_findings(report: ValidationReport, findings: list[Finding]) -> None:
    for finding in findings:
        issue = ValidationFinding(
            code=finding.code,
            severity=Severity(finding.severity),
            path=finding.path,
            message=finding.message,
            suggestion=finding.suggestion,
        )
        if finding.severity == Severity.WARNING.value:
            report.add_warning(issue)
        else:
            report.add_error(issue)

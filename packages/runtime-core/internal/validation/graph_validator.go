package validation

import (
	"math-assistant/runtime-core/internal/domain"
	"math-assistant/runtime-core/internal/validation/validators"
)

// GraphValidator runs graph-level static analysis (GV-xxx).
type GraphValidator struct {
	tiers *validators.PriorityTierRegistry
}

// NewGraphValidator constructs a graph validator with registry data.
func NewGraphValidator(tiers *validators.PriorityTierRegistry) *GraphValidator {
	return &GraphValidator{tiers: tiers}
}

// Validate executes all graph validators and merges findings.
func (v *GraphValidator) Validate(game *domain.GameVersion) *ValidationReport {
	report := NewReport("")
	if game == nil {
		return report
	}
	addFindings(report, validators.ValidateStateMachines(game))
	addFindings(report, validators.ValidateTransitions(game, v.tiers))
	addFindings(report, validators.ValidateReachability(game))
	addFindings(report, validators.ValidateStackDepth(game))
	addFindings(report, validators.ValidateProgression(game))
	return report
}

func addFindings(report *ValidationReport, findings []validators.Finding) {
	for _, f := range findings {
		issue := ValidationIssue{
			Code:       f.Code,
			Path:       f.Path,
			Message:    f.Message,
			Suggestion: f.Suggestion,
		}
		if f.Severity == string(SeverityWarning) {
			report.AddWarning(issue)
		} else {
			report.AddError(issue)
		}
	}
}

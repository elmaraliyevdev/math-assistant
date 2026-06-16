package validation

import "time"

const ValidatorVersion = "validation-engine@1.0.0"

// Severity classifies validation findings.
type Severity string

const (
	SeverityError   Severity = "error"
	SeverityWarning Severity = "warning"
)

// ValidationIssue is a single schema or graph validation finding.
type ValidationIssue struct {
	Code       string   `json:"code"`
	Severity   Severity `json:"severity"`
	Path       string   `json:"path"`
	Message    string   `json:"message"`
	Suggestion string   `json:"suggestion,omitempty"`
}

// ValidationMetadata captures report provenance.
type ValidationMetadata struct {
	ValidatorVersion string    `json:"validatorVersion"`
	Timestamp        time.Time `json:"timestamp"`
	GameContentHash  string    `json:"gameContentHash,omitempty"`
}

// ValidationReport aggregates validation outcomes.
type ValidationReport struct {
	Valid    bool               `json:"valid"`
	Errors   []ValidationIssue    `json:"errors"`
	Warnings []ValidationIssue    `json:"warnings"`
	Metadata ValidationMetadata   `json:"metadata"`
}

// NewReport builds an empty report with metadata populated.
func NewReport(contentHash string) *ValidationReport {
	return &ValidationReport{
		Valid:    true,
		Errors:   nil,
		Warnings: nil,
		Metadata: ValidationMetadata{
			ValidatorVersion: ValidatorVersion,
			Timestamp:        time.Now().UTC(),
			GameContentHash:  contentHash,
		},
	}
}

func (r *ValidationReport) AddError(issue ValidationIssue) {
	issue.Severity = SeverityError
	r.Errors = append(r.Errors, issue)
	r.Valid = false
}

func (r *ValidationReport) AddWarning(issue ValidationIssue) {
	issue.Severity = SeverityWarning
	r.Warnings = append(r.Warnings, issue)
}

func (r *ValidationReport) Merge(other *ValidationReport) {
	if other == nil {
		return
	}
	for _, e := range other.Errors {
		r.AddError(e)
	}
	for _, w := range other.Warnings {
		r.AddWarning(w)
	}
}

func (r *ValidationReport) HasErrors() bool {
	return len(r.Errors) > 0
}

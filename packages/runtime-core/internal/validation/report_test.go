package validation_test

import (
	"testing"

	"math-assistant/runtime-core/internal/validation"
)

func TestSchemaValidatorInvalidJSON(t *testing.T) {
	paths, err := validation.DefaultSchemaPaths()
	if err != nil {
		t.Fatal(err)
	}
	sv, err := validation.NewSchemaValidator(paths)
	if err != nil {
		t.Fatal(err)
	}
	report, err := sv.ValidateGame([]byte("{not-json"))
	if err != nil {
		t.Fatal(err)
	}
	if report.Valid {
		t.Fatal("expected invalid JSON report")
	}
}

func TestAddFindingsWarning(t *testing.T) {
	report := validation.NewReport("hash")
	report.AddWarning(validation.ValidationIssue{Code: "GV-028", Message: "warn"})
	if len(report.Warnings) != 1 || !report.Valid {
		t.Fatalf("unexpected report: %+v", report)
	}
}

func TestReportMergeNil(t *testing.T) {
	report := validation.NewReport("")
	report.Merge(nil)
	if !report.Valid {
		t.Fatal("expected valid after nil merge")
	}
}

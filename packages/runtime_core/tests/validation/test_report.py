"""Validation report unit tests."""

from runtime_core.validation.issues import graph_orphan_state, schema_required
from runtime_core.validation.report import ValidationReport


def test_report_merge_and_codes() -> None:
    report = ValidationReport.empty(content_hash="abc")
    report.add_error(schema_required("$.schemaVersion", "schemaVersion"))
    other = ValidationReport.empty()
    other.add_warning(graph_orphan_state("main", "ORPHAN"))
    report.merge(other)
    assert not report.valid
    assert report.has_code("SV-001")
    assert report.has_code("GV-005")
    assert len(report.warnings) == 1

"""Golden mathematical validation tests."""

from __future__ import annotations

import pytest

from runtime_core.mathematical.golden import (
    list_golden_math_fixtures,
    validate_golden_math_fixture,
)


@pytest.mark.golden_mathematical
@pytest.mark.parametrize("fixture_id", list_golden_math_fixtures())
def test_golden_mathematical_fixture(fixture_id: str) -> None:
    result = validate_golden_math_fixture(fixture_id)
    assert result.passed, f"fixture {fixture_id}: {[d.field for d in result.diffs]}"


def test_golden_mathematical_report_deterministic() -> None:
    first = validate_golden_math_fixture("analytic-4spin-bucketed")
    second = validate_golden_math_fixture("analytic-4spin-bucketed")
    assert first.passed and second.passed
    assert first.diffs == second.diffs

"""Edge-case tests for golden validation modules."""

from __future__ import annotations

from pathlib import Path

import pytest

from runtime_core.golden.cli import main
from runtime_core.golden.compare import format_diff_report
from runtime_core.golden.loader import GoldenArtifactError, load_simulation_profile
from runtime_core.golden.models import GoldenComparisonResult, GoldenDiff, RuntimeOverrides
from runtime_core.golden.overrides import apply_runtime_overrides
from runtime_core.golden.runner import golden_runner
from runtime_core.runtime.version import ENGINE_VERSION
from tests.conftest import repo_root


def test_format_diff_report_without_diffs() -> None:
    result = GoldenComparisonResult(fixture_id="fixture-01", passed=True, diffs=())
    text = format_diff_report(result)
    assert "passed: True" in text
    assert "diffs:" not in text


def test_format_diff_report_with_diffs() -> None:
    result = GoldenComparisonResult(
        fixture_id="fixture-01",
        passed=False,
        diffs=(GoldenDiff(field="eventLogHash", expected="a", actual="b"),),
    )
    text = format_diff_report(result)
    assert "eventLogHash" in text


def test_apply_runtime_overrides_noop(repo_root) -> None:
    from runtime_core.common.golden import load_golden_game_version

    game = load_golden_game_version("fixture-01-base-5x3", repo_root=repo_root)
    assert apply_runtime_overrides(game, None) is game
    assert apply_runtime_overrides(game, RuntimeOverrides()) is game


def test_apply_runtime_overrides_entry_min_count_only(repo_root) -> None:
    from runtime_core.common.golden import load_golden_game_version

    game = load_golden_game_version("fixture-03-base-hold-win", repo_root=repo_root)
    modified = apply_runtime_overrides(
        game,
        RuntimeOverrides(hold_and_win_entry_min_count=3),
    )
    assert modified is not game


def test_runner_content_hash_mismatch(repo_root) -> None:
    runner = golden_runner(repo_root=repo_root)
    profile_path = (
        repo_root / "tests/golden/fixture-01-base-5x3/simulation.profile.yaml"
    )
    original = profile_path.read_text(encoding="utf-8")
    try:
        profile_path.write_text(
            original.replace(
                "3d4f300b51844a5b1b5dbead2fff1978024905367a4cb8500aa5063a273993b4",
                "0" * 64,
            ),
            encoding="utf-8",
        )
        result = runner.validate_fixture("fixture-01-base-5x3")
        assert not result.passed
        assert result.diffs[0].field == "gameVersionContentHash"
    finally:
        profile_path.write_text(original, encoding="utf-8")


def test_cli_single_fixture_json(repo_root) -> None:
    exit_code = main(
        [
            "--fixture",
            "fixture-01-base-5x3",
            "--format",
            "json",
            "--repo-root",
            str(repo_root),
        ],
    )
    assert exit_code == 0


def test_cli_fails_on_mismatch(repo_root, tmp_path: Path) -> None:
    expected_path = (
        repo_root / "tests/golden/fixture-01-base-5x3/expected.yaml"
    )
    original = expected_path.read_text(encoding="utf-8")
    try:
        expected_path.write_text(
            original.replace("stepCount: 1", "stepCount: 999"),
            encoding="utf-8",
        )
        exit_code = main(
            ["--fixture", "fixture-01-base-5x3", "--repo-root", str(repo_root)],
        )
        assert exit_code == 1
    finally:
        expected_path.write_text(original, encoding="utf-8")


def test_cli_requires_fixture_or_all() -> None:
    with pytest.raises(SystemExit):
        main([])


def test_load_simulation_profile_missing(tmp_path: Path) -> None:
    with pytest.raises(GoldenArtifactError, match="not found"):
        load_simulation_profile("missing-fixture", repo_root=tmp_path)


def test_cli_subset_validation(repo_root) -> None:
    exit_code = main(
        [
            "--fixture",
            "fixture-01-base-5x3",
            "--fixture",
            "fixture-02-base-free-spins",
            "--repo-root",
            str(repo_root),
        ],
    )
    assert exit_code == 0


def test_cli_determinism_json(repo_root) -> None:
    exit_code = main(
        [
            "--fixture",
            "fixture-01-base-5x3",
            "--determinism",
            "--format",
            "json",
            "--repo-root",
            str(repo_root),
        ],
    )
    assert exit_code == 0


def test_compare_engine_version_mismatch() -> None:
    from runtime_core.golden.compare import compare_outcome
    from runtime_core.golden.models import (
        ExpectedAccumulatorDelta,
        ExpectedBaseline,
        ExpectedDeterminism,
        ExpectedExposure,
        ExpectedRuntimeOutcome,
        GoldenRunOutcome,
    )

    expected = ExpectedBaseline(
        version="1.0.0",
        locked=True,
        engineVersion="runtime-core@0.0.0",
        runtimeOutcome=ExpectedRuntimeOutcome(
            eventLogHash="x",
            totalWinMinorUnits=0,
            totalBetMinorUnits=100,
            stepCount=1,
            framePushCount=0,
            exposure=ExpectedExposure(
                capApplied=False,
                truncatedMinorUnits=0,
                uncappedWinMinorUnits=0,
                truncationCount=0,
            ),
            accumulatorDelta=ExpectedAccumulatorDelta(
                cappedWinMinorUnits=0,
                uncappedWinMinorUnits=0,
                exposureTruncationCount=0,
                exposureTruncatedMinorUnits=0,
                chainFaultCount=0,
            ),
        ),
        determinism=ExpectedDeterminism(
            requireExactEngineMatch=True,
            requireExactEventLogHash=True,
        ),
    )
    actual = GoldenRunOutcome(
        engineVersion=ENGINE_VERSION,
        gameVersionContentHash="hash",
        eventLogHash="x",
        totalWinMinorUnits=0,
        totalBetMinorUnits=100,
        stepCount=1,
        framePushCount=0,
        exposureCapApplied=False,
        totalUncappedWinMinorUnits=0,
        totalTruncatedMinorUnits=0,
        chainFaultCount=0,
        exposureTruncationCount=0,
        exposureTruncatedMinorUnits=0,
        cappedWinMinorUnits=0,
        uncappedWinMinorUnits=0,
    )
    result = compare_outcome("f", expected, actual, engine_version=ENGINE_VERSION)
    assert any(diff.field == "engineVersion" for diff in result.diffs)

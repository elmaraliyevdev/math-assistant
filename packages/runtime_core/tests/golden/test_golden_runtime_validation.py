"""Golden runtime validation tests (Phase M7)."""

from __future__ import annotations

import pytest

from runtime_core.golden.cli import main
from runtime_core.golden.compare import compare_outcome, format_diff_report
from runtime_core.golden.loader import (
    load_expected_baseline,
    load_manifest,
    load_simulation_profile,
    list_manifest_fixtures,
)
from runtime_core.golden.models import (
    ExpectedAccumulatorDelta,
    ExpectedBaseline,
    ExpectedDeterminism,
    ExpectedExposure,
    ExpectedRuntimeOutcome,
    GoldenRunOutcome,
)
from runtime_core.golden.overrides import apply_runtime_overrides
from runtime_core.golden.runner import golden_runner, render_validation_report
from runtime_core.runtime.version import ENGINE_VERSION
from tests.conftest import repo_root


@pytest.fixture
def runner(repo_root):
    return golden_runner(repo_root=repo_root)


@pytest.mark.golden_runtime
@pytest.mark.parametrize(
    "fixture_id",
    [
        "fixture-01-base-5x3",
        "fixture-02-base-free-spins",
        "fixture-03-base-hold-win",
        "fixture-04-nested-fs-hold-win",
    ],
)
def test_golden_runtime_matches_expected(runner, fixture_id: str) -> None:
    result = runner.validate_fixture(fixture_id)
    assert result.passed, format_diff_report(result)


@pytest.mark.golden_runtime
def test_golden_runtime_validate_all(runner) -> None:
    report = runner.validate_all()
    assert report.passed, render_validation_report(report)


@pytest.mark.golden_runtime
@pytest.mark.parametrize(
    "fixture_id",
    [
        "fixture-01-base-5x3",
        "fixture-02-base-free-spins",
        "fixture-03-base-hold-win",
        "fixture-04-nested-fs-hold-win",
    ],
)
def test_golden_runtime_determinism(runner, fixture_id: str) -> None:
    assert runner.validate_determinism(fixture_id)


@pytest.mark.golden_runtime
def test_golden_cli_all_passes(repo_root) -> None:
    exit_code = main(["--all", "--repo-root", str(repo_root)])
    assert exit_code == 0


@pytest.mark.golden_runtime
def test_golden_cli_determinism_passes(repo_root) -> None:
    exit_code = main(["--all", "--determinism", "--repo-root", str(repo_root)])
    assert exit_code == 0


@pytest.mark.golden_runtime
def test_manifest_lists_all_fixtures(repo_root) -> None:
    manifest = load_manifest(repo_root=repo_root)
    assert manifest["version"] == "1.0.0"
    assert list_manifest_fixtures(repo_root=repo_root) == [
        "fixture-01-base-5x3",
        "fixture-02-base-free-spins",
        "fixture-03-base-hold-win",
        "fixture-04-nested-fs-hold-win",
    ]


@pytest.mark.golden_runtime
def test_simulation_profile_pins_engine_version(repo_root) -> None:
    profile = load_simulation_profile("fixture-01-base-5x3", repo_root=repo_root)
    expected = load_expected_baseline("fixture-01-base-5x3", repo_root=repo_root)
    assert profile.engine_version == ENGINE_VERSION
    assert expected.engine_version == ENGINE_VERSION


def test_compare_outcome_detects_event_hash_mismatch() -> None:
    expected = ExpectedBaseline(
        version="1.0.0",
        locked=True,
        engineVersion=ENGINE_VERSION,
        runtimeOutcome=ExpectedRuntimeOutcome(
            eventLogHash="aaa",
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
        eventLogHash="bbb",
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
    result = compare_outcome("fixture-test", expected, actual, engine_version=ENGINE_VERSION)
    assert not result.passed
    assert any(diff.field == "eventLogHash" for diff in result.diffs)


def test_compare_outcome_skips_when_unlocked() -> None:
    expected = ExpectedBaseline(
        version="1.0.0",
        locked=False,
        engineVersion=ENGINE_VERSION,
        runtimeOutcome=ExpectedRuntimeOutcome(
            eventLogHash="aaa",
            totalWinMinorUnits=99,
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
        eventLogHash="bbb",
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
    assert compare_outcome("x", expected, actual, engine_version=ENGINE_VERSION).passed


def test_apply_runtime_overrides_changes_content_hash(repo_root) -> None:
    from runtime_core.common.golden import load_golden_game_version
    from runtime_core.golden.models import RuntimeOverrides
    from runtime_core.runtime.session.resolution import content_hash

    game = load_golden_game_version("fixture-03-base-hold-win", repo_root=repo_root)
    canonical = content_hash(game)
    overrides = RuntimeOverrides(
        hold_and_win_entry_min_count=3,
        hold_and_win_trigger_symbol_count=3,
    )
    modified = apply_runtime_overrides(game, overrides)
    assert content_hash(modified) != canonical

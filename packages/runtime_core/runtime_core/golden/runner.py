"""Golden runtime validation runner."""

from __future__ import annotations

from pathlib import Path

from runtime_core.common.golden import load_golden_game_version
from runtime_core.golden.compare import compare_outcome, format_diff_report
from runtime_core.golden.loader import (
    load_expected_baseline,
    load_simulation_profile,
    list_manifest_fixtures,
)
from runtime_core.golden.models import GoldenRunOutcome, GoldenValidationReport
from runtime_core.golden.overrides import apply_runtime_overrides
from runtime_core.runtime.events import EventLogMode
from runtime_core.runtime.executor import SessionExecutor
from runtime_core.runtime.session.resolution import content_hash
from runtime_core.runtime.spin_chain import SpinChainRequest
from runtime_core.runtime.version import ENGINE_VERSION


class GoldenRunner:
    """Execute and validate golden runtime fixtures."""

    def __init__(self, *, repo_root: Path | None = None) -> None:
        self._repo_root = repo_root
        self._executor = SessionExecutor()

    def execute_fixture(self, fixture_id: str) -> GoldenRunOutcome:
        profile = load_simulation_profile(fixture_id, repo_root=self._repo_root)
        game = load_golden_game_version(fixture_id, repo_root=self._repo_root)
        game = apply_runtime_overrides(game, profile.runtime_overrides)
        event_mode = EventLogMode(profile.event_log_mode)
        request = SpinChainRequest(
            game=game,
            master_seed=profile.master_seed_bytes(),
            spin_chain_index=profile.spin_chain_index,
            shard_index=profile.shard_index,
            simulation_run_id=profile.simulation_run_id,
            bet_minor_units=profile.bet_minor_units,
            engine_version=profile.engine_version,
            event_log_mode=event_mode,
        )
        result = self._executor.execute_spin_chain(request)
        return GoldenRunOutcome(
            engine_version=profile.engine_version,
            game_version_content_hash=content_hash(game),
            event_log_hash=result.event_log_hash,
            total_win_minor_units=result.total_win_minor_units,
            total_bet_minor_units=result.total_bet_minor_units,
            step_count=result.step_count,
            frame_push_count=result.frame_push_count,
            exposure_cap_applied=result.exposure_cap_applied,
            total_uncapped_win_minor_units=result.total_uncapped_win_minor_units,
            total_truncated_minor_units=result.total_truncated_minor_units,
            chain_fault_count=result.accumulator_delta.chain_fault_count,
            exposure_truncation_count=result.accumulator_delta.exposure_truncation_count,
            exposure_truncated_minor_units=result.accumulator_delta.exposure_truncated_minor_units,
            capped_win_minor_units=result.accumulator_delta.capped_win_minor_units,
            uncapped_win_minor_units=result.accumulator_delta.uncapped_win_minor_units,
            fault=result.fault.code if result.fault else None,
            limit_hit=result.limit_hit.code if result.limit_hit else None,
        )

    def validate_fixture(self, fixture_id: str):
        from runtime_core.golden.models import GoldenComparisonResult

        profile = load_simulation_profile(fixture_id, repo_root=self._repo_root)
        expected = load_expected_baseline(fixture_id, repo_root=self._repo_root)
        actual = self.execute_fixture(fixture_id)
        if profile.game_version_content_hash != actual.game_version_content_hash:
            from runtime_core.golden.models import GoldenDiff

            return GoldenComparisonResult(
                fixture_id=fixture_id,
                passed=False,
                diffs=(
                    GoldenDiff(
                        field="gameVersionContentHash",
                        expected=profile.game_version_content_hash,
                        actual=actual.game_version_content_hash,
                    ),
                ),
            )
        return compare_outcome(
            fixture_id,
            expected,
            actual,
            engine_version=ENGINE_VERSION,
        )

    def validate_all(self) -> GoldenValidationReport:
        results = tuple(
            self.validate_fixture(fixture_id)
            for fixture_id in list_manifest_fixtures(repo_root=self._repo_root)
        )
        return GoldenValidationReport(
            passed=all(result.passed for result in results),
            engine_version=ENGINE_VERSION,
            results=results,
        )

    def validate_determinism(self, fixture_id: str) -> bool:
        first = self.execute_fixture(fixture_id)
        second = self.execute_fixture(fixture_id)
        return (
            first.event_log_hash == second.event_log_hash
            and first.total_win_minor_units == second.total_win_minor_units
            and first.step_count == second.step_count
            and first.frame_push_count == second.frame_push_count
            and first.chain_fault_count == second.chain_fault_count
        )


def golden_runner(*, repo_root: Path | None = None) -> GoldenRunner:
    return GoldenRunner(repo_root=repo_root)


def render_validation_report(report: GoldenValidationReport) -> str:
    lines = [
        f"engineVersion: {report.engine_version}",
        f"passed: {report.passed}",
        "",
    ]
    for result in report.results:
        lines.append(format_diff_report(result))
        lines.append("")
    return "\n".join(lines).rstrip()

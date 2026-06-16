"""CLI entry point for golden runtime validation."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

from runtime_core.golden.loader import list_manifest_fixtures
from runtime_core.golden.runner import golden_runner, render_validation_report


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Golden runtime validation runner for SessionExecutor",
    )
    parser.add_argument(
        "--fixture",
        action="append",
        dest="fixtures",
        help="Validate a single fixture id (repeatable)",
    )
    parser.add_argument(
        "--all",
        action="store_true",
        help="Validate all fixtures listed in tests/golden/manifest.yaml",
    )
    parser.add_argument(
        "--repo-root",
        type=Path,
        default=None,
        help="Repository root containing tests/golden/",
    )
    parser.add_argument(
        "--format",
        choices=("text", "json"),
        default="text",
        help="Output format for validation report",
    )
    parser.add_argument(
        "--determinism",
        action="store_true",
        help="Run each fixture twice and verify identical outcomes",
    )
    args = parser.parse_args(argv)

    if not args.all and not args.fixtures:
        parser.error("specify --all or at least one --fixture")

    runner = golden_runner(repo_root=args.repo_root)
    fixture_ids = (
        list_manifest_fixtures(repo_root=args.repo_root)
        if args.all
        else list(args.fixtures or [])
    )

    if args.determinism:
        failures = [
            fixture_id
            for fixture_id in fixture_ids
            if not runner.validate_determinism(fixture_id)
        ]
        if failures:
            _emit(
                args.format,
                {
                    "passed": False,
                    "failures": failures,
                    "reason": "determinism mismatch",
                },
            )
            return 1
        _emit(args.format, {"passed": True, "determinism": "ok", "fixtures": fixture_ids})
        return 0

    if len(fixture_ids) == 1 and not args.all:
        result = runner.validate_fixture(fixture_ids[0])
        from runtime_core.golden.models import GoldenValidationReport
        from runtime_core.runtime.version import ENGINE_VERSION

        report = GoldenValidationReport(
            passed=result.passed,
            engine_version=ENGINE_VERSION,
            results=(result,),
        )
        if args.format == "json":
            print(json.dumps(report.model_dump(mode="json", by_alias=True), indent=2))
        else:
            print(render_validation_report(report))
        return 0 if result.passed else 1

    report = runner.validate_all() if args.all else _validate_subset(runner, fixture_ids)
    if args.format == "json":
        print(json.dumps(report.model_dump(mode="json", by_alias=True), indent=2))
    else:
        print(render_validation_report(report))
    return 0 if report.passed else 1


def _validate_subset(runner, fixture_ids: list[str]):
    from runtime_core.runtime.version import ENGINE_VERSION
    from runtime_core.golden.models import GoldenValidationReport

    results = tuple(runner.validate_fixture(fixture_id) for fixture_id in fixture_ids)
    return GoldenValidationReport(
        passed=all(result.passed for result in results),
        engine_version=ENGINE_VERSION,
        results=results,
    )


def _emit(fmt: str, payload: dict[str, object]) -> None:
    if fmt == "json":
        print(json.dumps(payload, indent=2))
    else:
        print(payload)


if __name__ == "__main__":
    sys.exit(main())

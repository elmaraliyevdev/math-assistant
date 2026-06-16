"""Certification benchmark CLI."""

from __future__ import annotations

import argparse
import json
import sys
from datetime import UTC, datetime
from pathlib import Path

from benchmarks.harness import ENGINE_VERSION
from benchmarks.report import write_certification_docs
from benchmarks.rtp_convergence import (
    CONVERGENCE_SPIN_COUNTS,
    run_rtp_convergence_validation,
)
from benchmarks.shard_determinism import (
    SHARD_COUNTS,
    run_shard_determinism_validation,
)
from benchmarks.throughput import THROUGHPUT_SPIN_COUNTS, run_all_throughput_benchmarks


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Performance and certification benchmarks for runtime-core",
    )
    parser.add_argument(
        "--quick",
        action="store_true",
        help="Run reduced spin counts for smoke validation",
    )
    parser.add_argument(
        "--output-dir",
        type=Path,
        default=Path("benchmarks/results"),
        help="Directory for JSON results",
    )
    parser.add_argument(
        "--skip-docs",
        action="store_true",
        help="Skip writing docs/PERFORMANCE_REPORT and CERTIFICATION_READINESS",
    )
    parser.add_argument(
        "--repo-root",
        type=Path,
        default=None,
        help="Repository root for documentation output",
    )
    parser.add_argument(
        "--docs-only",
        action="store_true",
        help="Regenerate docs from existing benchmarks/results/certification_results.json",
    )
    args = parser.parse_args(argv)

    if args.docs_only:
        results_path = args.output_dir / "certification_results.json"
        if not results_path.is_file():
            print(f"Missing {results_path}", file=sys.stderr)
            return 1
        payload = json.loads(results_path.read_text(encoding="utf-8"))
        repo_root = args.repo_root or _find_repo_root()
        write_certification_docs(payload, repo_root=repo_root)
        print(f"Updated docs in {repo_root / 'docs'}")
        return 0

    throughput_counts = (1_000, 10_000) if args.quick else THROUGHPUT_SPIN_COUNTS
    convergence_counts = (1_000, 5_000) if args.quick else CONVERGENCE_SPIN_COUNTS
    shard_counts = (1, 2, 4) if args.quick else SHARD_COUNTS
    shard_spins = 1_000 if args.quick else 10_000

    print(f"Engine: {ENGINE_VERSION}")
    print("Running throughput benchmarks...")
    throughput = run_all_throughput_benchmarks(throughput_counts)

    print("Running shard determinism validation...")
    shard_report = run_shard_determinism_validation(
        spin_count=shard_spins,
        shard_counts=shard_counts,
    )

    print("Running RTP convergence validation...")
    convergence = run_rtp_convergence_validation(convergence_counts)

    payload = {
        "generatedAt": datetime.now(tz=UTC).isoformat(),
        "engineVersion": ENGINE_VERSION,
        "quickMode": args.quick,
        "throughput": [run.to_dict() for run in throughput],
        "shardDeterminism": shard_report.to_dict(),
        "convergence": convergence.to_dict(),
    }

    args.output_dir.mkdir(parents=True, exist_ok=True)
    results_path = args.output_dir / "certification_results.json"
    results_path.write_text(json.dumps(payload, indent=2), encoding="utf-8")
    print(f"Wrote {results_path}")

    if not args.skip_docs:
        repo_root = args.repo_root or _find_repo_root()
        write_certification_docs(payload, repo_root=repo_root)
        print(f"Updated docs in {repo_root / 'docs'}")

    all_passed = shard_report.passed and convergence.passed
    if not all_passed:
        print("Certification validation FAILED", file=sys.stderr)
        return 1
    print("Certification validation PASSED")
    return 0


def _find_repo_root() -> Path:
    candidate = Path.cwd()
    for _ in range(6):
        if (candidate / "tests/golden/manifest.yaml").is_file():
            return candidate
        if candidate.parent == candidate:
            break
        candidate = candidate.parent
    return Path.cwd().parents[1] if "runtime_core" in str(Path.cwd()) else Path.cwd()


if __name__ == "__main__":
    sys.exit(main())

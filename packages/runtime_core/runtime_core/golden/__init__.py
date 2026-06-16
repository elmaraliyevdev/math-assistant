"""Golden runtime validation — deterministic end-to-end regression contracts."""

from runtime_core.golden.compare import GoldenComparisonResult, GoldenDiff, compare_outcome
from runtime_core.golden.models import (
    ExpectedBaseline,
    GoldenRunOutcome,
    GoldenRuntimeProfile,
    GoldenValidationReport,
)
from runtime_core.golden.runner import GoldenRunner, golden_runner

__all__ = [
    "ExpectedBaseline",
    "GoldenComparisonResult",
    "GoldenDiff",
    "GoldenRunOutcome",
    "GoldenRuntimeProfile",
    "GoldenRunner",
    "GoldenValidationReport",
    "compare_outcome",
    "golden_runner",
]

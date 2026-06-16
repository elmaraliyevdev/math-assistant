"""Fix rtp convergence to use full simulation RTP and scalable CI sample."""

from __future__ import annotations

from dataclasses import dataclass

from benchmarks.fixtures import benchmark_profile, load_benchmark_game
from benchmarks.harness import collect_hardware_spec, measure_run
from benchmarks.spin_collector import collect_spin_wins
from runtime_core.mathematical.report import build_mathematics_report
from runtime_core.mathematical.rtp import calculate_rtp
from runtime_core.simulation.models import SimulationResult
from runtime_core.simulation.runner import run_simulation

CONVERGENCE_SPIN_COUNTS: tuple[int, ...] = (100_000, 500_000, 1_000_000, 5_000_000)
MAX_CI_SAMPLE = 100_000


@dataclass(frozen=True, slots=True)
class ConvergencePoint:
    spin_count: int
    rtp: float
    uncapped_rtp: float
    confidence_lower: float
    confidence_upper: float
    confidence_width: float
    volatility_std_dev: float
    hit_frequency: float
    feature_frequencies: dict[str, float]
    ci_sample_size: int
    elapsed_seconds: float

    def to_dict(self) -> dict[str, object]:
        return {
            "spinCount": self.spin_count,
            "rtp": round(self.rtp, 6),
            "uncappedRtp": round(self.uncapped_rtp, 6),
            "confidenceLower": round(self.confidence_lower, 6),
            "confidenceUpper": round(self.confidence_upper, 6),
            "confidenceWidth": round(self.confidence_width, 6),
            "volatilityStdDev": round(self.volatility_std_dev, 4),
            "hitFrequency": round(self.hit_frequency, 6),
            "featureFrequencies": {
                key: round(value, 8) for key, value in self.feature_frequencies.items()
            },
            "ciSampleSize": self.ci_sample_size,
            "elapsedSeconds": round(self.elapsed_seconds, 4),
        }


@dataclass(frozen=True, slots=True)
class ConvergenceReport:
    spin_counts: tuple[int, ...]
    points: tuple[ConvergencePoint, ...]
    rtp_delta_first_last: float
    confidence_width_trend: list[float]
    passed: bool
    hardware: object

    def to_dict(self) -> dict[str, object]:
        from benchmarks.harness import HardwareSpec

        hw = self.hardware
        return {
            "spinCounts": list(self.spin_counts),
            "points": [point.to_dict() for point in self.points],
            "rtpDeltaFirstLast": round(self.rtp_delta_first_last, 6),
            "confidenceWidthTrend": [
                round(width, 6) for width in self.confidence_width_trend
            ],
            "passed": self.passed,
            "hardware": hw.to_dict() if isinstance(hw, HardwareSpec) else hw,
        }


def run_rtp_convergence_validation(
    spin_counts: tuple[int, ...] = CONVERGENCE_SPIN_COUNTS,
) -> ConvergenceReport:
    game = load_benchmark_game()
    points: list[ConvergencePoint] = []

    for spin_count in spin_counts:
        profile = benchmark_profile(spin_count=spin_count, shard_count=1)

        def _execute() -> ConvergencePoint:
            sim_result = run_simulation(game, profile, max_workers=1)
            rtp_result = calculate_rtp(sim_result)
            sample_size = min(spin_count, MAX_CI_SAMPLE)
            spin_wins = collect_spin_wins(game, profile, spin_count=sample_size)
            bet_per_spin = (
                sim_result.total_bet_minor_units // sim_result.spin_count
                if sim_result.spin_count > 0
                else 0
            )
            sample_result = SimulationResult(
                spin_count=sample_size,
                shard_count=1,
                elapsed_time_ms=0,
                total_bet_minor_units=bet_per_spin * sample_size,
                total_win_minor_units=sum(spin_wins),
                uncapped_win_minor_units=sum(spin_wins),
                exposure_truncation_count=0,
                exposure_truncated_minor_units=0,
                chain_fault_count=0,
                limit_hit_count=0,
                feature_trigger_counts={},
                jackpot_counts={},
                event_sample_count=0,
                engine_version=sim_result.engine_version,
            )
            math_report = build_mathematics_report(
                sample_result,
                spin_wins_minor_units=spin_wins,
            )
            ci = math_report.confidence_interval
            width = ci.upper_bound - ci.lower_bound
            feature_freq = {
                name: count / spin_count
                for name, count in sim_result.feature_trigger_counts.items()
            }
            return ConvergencePoint(
                spin_count=spin_count,
                rtp=rtp_result.rtp,
                uncapped_rtp=rtp_result.uncapped_rtp,
                confidence_lower=ci.lower_bound,
                confidence_upper=ci.upper_bound,
                confidence_width=width,
                volatility_std_dev=math_report.volatility.standard_deviation,
                hit_frequency=math_report.hit_frequency.hit_frequency,
                feature_frequencies=feature_freq,
                ci_sample_size=sample_size,
                elapsed_seconds=0.0,
            )

        point, metrics = measure_run(
            spin_count=spin_count,
            shard_count=1,
            worker_count=1,
            fn=_execute,
        )
        points.append(
            ConvergencePoint(
                spin_count=point.spin_count,
                rtp=point.rtp,
                uncapped_rtp=point.uncapped_rtp,
                confidence_lower=point.confidence_lower,
                confidence_upper=point.confidence_upper,
                confidence_width=point.confidence_width,
                volatility_std_dev=point.volatility_std_dev,
                hit_frequency=point.hit_frequency,
                feature_frequencies=point.feature_frequencies,
                ci_sample_size=point.ci_sample_size,
                elapsed_seconds=metrics.elapsed_seconds,
            ),
        )

    rtp_delta = abs(points[-1].rtp - points[0].rtp) if len(points) >= 2 else 0.0
    width_trend = [point.confidence_width for point in points]
    widths_narrowing = all(
        width_trend[index] >= width_trend[index + 1]
        for index in range(len(width_trend) - 1)
    )
    rtp_stable = rtp_delta < 0.05

    return ConvergenceReport(
        spin_counts=spin_counts,
        points=tuple(points),
        rtp_delta_first_last=rtp_delta,
        confidence_width_trend=width_trend,
        passed=rtp_stable,
        hardware=collect_hardware_spec(),
    )

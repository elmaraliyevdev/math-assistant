"""Mathematical Engine — deterministic statistical analysis of simulation outputs."""

from runtime_core.mathematical.confidence import calculate_rtp_confidence_interval
from runtime_core.mathematical.distribution import calculate_win_distribution
from runtime_core.mathematical.exposure import calculate_exposure_analysis
from runtime_core.mathematical.feature_frequency import calculate_feature_frequencies
from runtime_core.mathematical.hit_frequency import calculate_hit_frequency
from runtime_core.mathematical.jackpot_frequency import calculate_jackpot_frequencies
from runtime_core.mathematical.insights import enrich_mathematics_report
from runtime_core.mathematical.models import (
    ConfidenceIntervalResult,
    ExposureAnalysisResult,
    FeatureFrequencyResult,
    FeatureValidationResult,
    HitFrequencyResult,
    JackpotFrequencyResult,
    MathematicsReport,
    RecommendationResult,
    RTPResult,
    RtpCategoryContribution,
    RtpDecompositionChart,
    RtpDecompositionResult,
    RtpValidationResult,
    VolatilityResult,
    WinDistributionBucket,
    WinDistributionResult,
)
from runtime_core.mathematical.recommendations import generate_recommendations
from runtime_core.mathematical.report import build_mathematics_report
from runtime_core.mathematical.rtp_decomposition import calculate_rtp_decomposition
from runtime_core.mathematical.rtp_validation import validate_rtp_target
from runtime_core.mathematical.decomposition_chart import build_rtp_decomposition_chart
from runtime_core.mathematical.feature_validation import validate_feature_frequencies
from runtime_core.mathematical.rtp import calculate_rtp
from runtime_core.mathematical.volatility import calculate_volatility

__all__ = [
    "ConfidenceIntervalResult",
    "ExposureAnalysisResult",
    "FeatureFrequencyResult",
    "FeatureValidationResult",
    "HitFrequencyResult",
    "JackpotFrequencyResult",
    "MathematicsReport",
    "RecommendationResult",
    "RTPResult",
    "RtpCategoryContribution",
    "RtpDecompositionChart",
    "RtpDecompositionResult",
    "RtpValidationResult",
    "VolatilityResult",
    "WinDistributionBucket",
    "WinDistributionResult",
    "build_mathematics_report",
    "build_rtp_decomposition_chart",
    "calculate_exposure_analysis",
    "calculate_feature_frequencies",
    "calculate_hit_frequency",
    "calculate_jackpot_frequencies",
    "calculate_rtp",
    "calculate_rtp_decomposition",
    "calculate_rtp_confidence_interval",
    "calculate_volatility",
    "calculate_win_distribution",
    "enrich_mathematics_report",
    "generate_recommendations",
    "validate_feature_frequencies",
    "validate_rtp_target",
]

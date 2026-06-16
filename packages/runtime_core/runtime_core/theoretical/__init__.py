"""Theoretical mathematics and calibration engine."""

from runtime_core.theoretical.calibration import calibrate_rtp, generate_calibration_recommendations
from runtime_core.theoretical.certification import build_certification_report
from runtime_core.theoretical.discrepancy import analyze_discrepancies
from runtime_core.theoretical.models import (
    CalibrationRecommendation,
    CalibrationResult,
    CertificationReport,
    DiscrepancyAnalysis,
    FeatureProbability,
    TheoreticalAnalysis,
    TheoreticalRtpResult,
)
from runtime_core.theoretical.report import (
    build_calibration_report,
    build_theoretical_analysis,
    export_certification_json,
    export_certification_pdf,
)
from runtime_core.theoretical.theoretical_features import calculate_feature_probabilities
from runtime_core.theoretical.theoretical_rtp import calculate_theoretical_rtp

__all__ = [
    "CalibrationRecommendation",
    "CalibrationResult",
    "CertificationReport",
    "DiscrepancyAnalysis",
    "FeatureProbability",
    "TheoreticalAnalysis",
    "TheoreticalRtpResult",
    "analyze_discrepancies",
    "build_calibration_report",
    "build_certification_report",
    "build_theoretical_analysis",
    "calibrate_rtp",
    "calculate_feature_probabilities",
    "calculate_theoretical_rtp",
    "export_certification_json",
    "export_certification_pdf",
    "generate_calibration_recommendations",
]

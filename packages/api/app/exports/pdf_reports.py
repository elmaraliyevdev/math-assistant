"""PDF report generation for simulation exports."""

from __future__ import annotations

import io
from typing import Any

from reportlab.lib import colors
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import inch
from reportlab.platypus import Paragraph, SimpleDocTemplate, Spacer, Table, TableStyle

from app.certification import CERTIFICATION_NOTICE


def _styles() -> dict[str, ParagraphStyle]:
    base = getSampleStyleSheet()
    return {
        "title": base["Title"],
        "heading": base["Heading2"],
        "body": base["BodyText"],
        "small": ParagraphStyle(
            "Small",
            parent=base["BodyText"],
            fontSize=9,
            textColor=colors.grey,
        ),
    }


def _table(rows: list[list[str]], col_widths: list[float] | None = None) -> Table:
    table = Table(rows, colWidths=col_widths, hAlign="LEFT")
    table.setStyle(
        TableStyle(
            [
                ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#f4f4f5")),
                ("TEXTCOLOR", (0, 0), (-1, 0), colors.black),
                ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
                ("FONTSIZE", (0, 0), (-1, -1), 9),
                ("BOTTOMPADDING", (0, 0), (-1, 0), 8),
                ("GRID", (0, 0), (-1, -1), 0.25, colors.lightgrey),
                ("VALIGN", (0, 0), (-1, -1), "TOP"),
            ],
        ),
    )
    return table


def _pct(value: float) -> str:
    return f"{value * 100:.4f}%"


def build_simulation_results_pdf(payload: dict[str, Any]) -> bytes:
    """Render a simulation results report as a binary PDF document."""
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(
        buffer,
        pagesize=letter,
        leftMargin=0.75 * inch,
        rightMargin=0.75 * inch,
        topMargin=0.75 * inch,
        bottomMargin=0.75 * inch,
        title="Simulation Results Report",
    )
    styles = _styles()
    story: list[Any] = []

    story.append(Paragraph("Simulation Results Report", styles["title"]))
    story.append(Spacer(1, 0.15 * inch))
    story.append(Paragraph(CERTIFICATION_NOTICE, styles["small"]))
    story.append(Spacer(1, 0.2 * inch))

    story.append(Paragraph("Simulation metadata", styles["heading"]))
    metadata_rows = [
        ["Field", "Value"],
        ["Simulation ID", str(payload.get("simulationId", ""))],
        ["Engine version", str(payload.get("engineVersion", ""))],
        ["Game version content hash", str(payload.get("gameVersionContentHash", ""))],
        ["Spin count", str(payload.get("hitFrequency", {}).get("winningSpinCount", 0)
                           + payload.get("hitFrequency", {}).get("losingSpinCount", 0))],
    ]
    story.append(_table(metadata_rows, [2.2 * inch, 4.3 * inch]))
    story.append(Spacer(1, 0.2 * inch))

    summary = payload.get("summary", {})
    story.append(Paragraph("RTP summary", styles["heading"]))
    story.append(
        _table(
            [
                ["Metric", "Value"],
                ["RTP", _pct(float(summary.get("rtp", 0)))],
                ["Uncapped RTP", _pct(float(summary.get("uncappedRtp", 0)))],
                ["Hit frequency", _pct(float(summary.get("hitFrequency", 0)))],
            ],
        ),
    )
    story.append(Spacer(1, 0.2 * inch))

    rtp_validation = payload.get("rtpValidation")
    if rtp_validation:
        story.append(Paragraph("RTP validation", styles["heading"]))
        story.append(
            _table(
                [
                    ["Metric", "Value"],
                    ["Target RTP", f"{float(rtp_validation['targetRtp']):.4f}%"],
                    ["Actual RTP", f"{float(rtp_validation['actualRtp']):.4f}%"],
                    ["Difference", f"{float(rtp_validation['difference']):.4f}"],
                    ["Tolerance", f"{float(rtp_validation['tolerance']):.4f}"],
                    [
                        "Within tolerance",
                        "Yes" if rtp_validation.get("withinTolerance") else "No",
                    ],
                ],
            ),
        )
        story.append(Spacer(1, 0.2 * inch))

    chart = payload.get("rtpDecompositionChart", {})
    if chart:
        story.append(Paragraph("RTP decomposition", styles["heading"]))
        story.append(
            _table(
                [
                    ["Category", "Share (%)"],
                    ["BASE", f"{float(chart.get('BASE', 0)):.4f}"],
                    ["FREE_SPINS", f"{float(chart.get('FREE_SPINS', 0)):.4f}"],
                    ["HOLD_AND_WIN", f"{float(chart.get('HOLD_AND_WIN', 0)):.4f}"],
                    ["JACKPOT", f"{float(chart.get('JACKPOT', 0)):.4f}"],
                    ["Total RTP", f"{float(chart.get('totalRtp', 0)):.4f}"],
                ],
            ),
        )
        story.append(Spacer(1, 0.2 * inch))

    features = payload.get("featureFrequencies", [])
    if features:
        story.append(Paragraph("Feature frequencies", styles["heading"]))
        feature_rows = [["Feature", "Triggers", "Frequency", "One in X"]]
        for item in features:
            one_in_x = item.get("oneInX")
            feature_rows.append(
                [
                    str(item.get("featureName", "")),
                    str(item.get("triggerCount", 0)),
                    _pct(float(item.get("frequency", 0))),
                    "—" if one_in_x is None else f"{one_in_x:.2f}",
                ],
            )
        story.append(_table(feature_rows))
        story.append(Spacer(1, 0.2 * inch))

    exposure = payload.get("exposure", {})
    story.append(Paragraph("Exposure analysis", styles["heading"]))
    story.append(
        _table(
            [
                ["Metric", "Value"],
                ["Truncation rate", _pct(float(exposure.get("truncationRate", 0)))],
                [
                    "Total truncated (minor units)",
                    str(exposure.get("totalTruncatedMinorUnits", 0)),
                ],
                ["Capped RTP", _pct(float(exposure.get("cappedRtp", 0)))],
                ["Uncapped RTP", _pct(float(exposure.get("uncappedRtp", 0)))],
                ["RTP difference", _pct(float(exposure.get("rtpDifference", 0)))],
                [
                    "Exposure cap applied",
                    "Yes" if exposure.get("exposureCapApplied") else "No",
                ],
            ],
        ),
    )
    story.append(Spacer(1, 0.2 * inch))

    recommendations = payload.get("recommendations", [])
    if recommendations:
        story.append(Paragraph("Recommendations", styles["heading"]))
        for item in recommendations:
            story.append(
                Paragraph(
                    f"<b>[{item.get('severity', '').upper()}]</b> "
                    f"{item.get('title', '')}: {item.get('description', '')}",
                    styles["body"],
                ),
            )
            story.append(Spacer(1, 0.08 * inch))

    doc.build(story)
    return buffer.getvalue()


def build_simulation_comparison_pdf(payload: dict[str, Any]) -> bytes:
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=letter, title="Simulation Comparison Report")
    styles = _styles()
    story: list[Any] = [
        Paragraph("Simulation Comparison Report", styles["title"]),
        Spacer(1, 0.15 * inch),
        Paragraph(CERTIFICATION_NOTICE, styles["small"]),
        Spacer(1, 0.2 * inch),
    ]

    for index, entry in enumerate(payload.get("simulations", []), start=1):
        detail = entry.get("detail", {})
        results = entry.get("results", {})
        summary = results.get("summary", {})
        story.append(Paragraph(f"Simulation {index}", styles["heading"]))
        story.append(
            _table(
                [
                    ["Field", "Value"],
                    ["Simulation ID", str(entry.get("simulationId", ""))],
                    ["Spins", str(detail.get("spinCount", ""))],
                    ["RTP", _pct(float(summary.get("rtp", 0)))],
                    ["Volatility (std dev)", f"{float(summary.get('volatility', 0)):.4f}"],
                    ["Hit frequency", _pct(float(summary.get("hitFrequency", 0)))],
                    ["Engine version", str(results.get("engineVersion", ""))],
                    [
                        "Content hash",
                        str(results.get("gameVersionContentHash", "")),
                    ],
                ],
                [2.2 * inch, 4.3 * inch],
            ),
        )
        story.append(Spacer(1, 0.15 * inch))

    doc.build(story)
    return buffer.getvalue()

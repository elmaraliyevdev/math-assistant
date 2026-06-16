"""Structured logging for simulation job lifecycle."""

from __future__ import annotations

import structlog

logger = structlog.get_logger("simulation.jobs")


def log_simulation_event(event: str, **fields: object) -> None:
    logger.info(event, **fields)


def log_simulation_message(message: str, **fields: object) -> None:
    """Human-readable lifecycle messages for operators."""
    logger.info(message, **fields)

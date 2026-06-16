"""structlog configuration for backend engines."""

from __future__ import annotations

import logging
import sys
from typing import Any, cast

import structlog


def configure_logging(
    *,
    json_logs: bool = False,
    log_level: int = logging.INFO,
) -> None:
    """Configure structured logging for library and test use.

    Runtime Core execution paths MUST NOT depend on log output or wall-clock
    timestamps attached by processors here.
    """
    shared_processors: list[structlog.types.Processor] = [
        structlog.contextvars.merge_contextvars,
        structlog.stdlib.add_log_level,
        structlog.stdlib.add_logger_name,
        structlog.processors.TimeStamper(fmt="iso", utc=True),
        structlog.processors.StackInfoRenderer(),
        structlog.processors.format_exc_info,
    ]

    if json_logs:
        renderer: structlog.types.Processor = structlog.processors.JSONRenderer()
    else:
        renderer = structlog.dev.ConsoleRenderer()

    structlog.configure(
        processors=[
            *shared_processors,
            structlog.stdlib.ProcessorFormatter.wrap_for_formatter,
        ],
        logger_factory=structlog.stdlib.LoggerFactory(),
        wrapper_class=structlog.stdlib.BoundLogger,
        cache_logger_on_first_use=True,
    )

    formatter = structlog.stdlib.ProcessorFormatter(
        processors=[
            structlog.stdlib.ProcessorFormatter.remove_processors_meta,
            renderer,
        ],
    )
    handler = logging.StreamHandler(sys.stderr)
    handler.setFormatter(formatter)

    root = logging.getLogger()
    root.handlers.clear()
    root.addHandler(handler)
    root.setLevel(log_level)


def get_logger(
    name: str | None = None,
    **initial_context: Any,
) -> structlog.stdlib.BoundLogger:
    """Return a structlog logger optionally bound with correlation fields."""
    logger = structlog.get_logger(name)
    bound = cast("structlog.stdlib.BoundLogger", logger)
    if initial_context:
        return bound.bind(**initial_context)
    return bound

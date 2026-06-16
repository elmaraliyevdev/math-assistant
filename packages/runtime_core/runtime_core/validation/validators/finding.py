"""Shared finding type for graph sub-validators."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class Finding:
    code: str
    severity: str
    path: str
    message: str
    suggestion: str


def err_finding(code: str, path: str, message: str, suggestion: str) -> Finding:
    return Finding(
        code=code, severity="error", path=path, message=message, suggestion=suggestion
    )


def warn_finding(code: str, path: str, message: str, suggestion: str) -> Finding:
    return Finding(
        code=code,
        severity="warning",
        path=path,
        message=message,
        suggestion=suggestion,
    )

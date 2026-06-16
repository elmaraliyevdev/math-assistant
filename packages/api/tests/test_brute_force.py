"""Brute-force guard unit tests."""

from __future__ import annotations

import pytest

from app.exceptions.domain import AccountLockedError
from app.security.brute_force import BruteForceGuard


def test_brute_force_locks_after_max_attempts() -> None:
    guard = BruteForceGuard(max_attempts=2, lockout_minutes=15)
    guard.record_failure("user@example.com", "1.2.3.4")
    guard.record_failure("user@example.com", "1.2.3.4")
    with pytest.raises(AccountLockedError):
        guard.check_allowed("user@example.com", "1.2.3.4")


def test_brute_force_clears_on_success() -> None:
    guard = BruteForceGuard(max_attempts=2, lockout_minutes=15)
    guard.record_failure("user@example.com", "1.2.3.4")
    guard.record_success("user@example.com", "1.2.3.4")
    guard.check_allowed("user@example.com", "1.2.3.4")

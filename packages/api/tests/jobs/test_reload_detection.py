"""Reload mode detection tests."""

from __future__ import annotations

from app.jobs.reload import is_uvicorn_reload_child


def test_is_uvicorn_reload_child_false_by_default(monkeypatch) -> None:
    monkeypatch.delenv("RUN_MAIN", raising=False)
    assert is_uvicorn_reload_child() is False


def test_is_uvicorn_reload_child_true_in_reload_worker(monkeypatch) -> None:
    monkeypatch.setenv("RUN_MAIN", "true")
    assert is_uvicorn_reload_child() is True

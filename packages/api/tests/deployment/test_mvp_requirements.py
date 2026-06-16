"""Verify MVP deployment configuration requirements."""

from __future__ import annotations

import subprocess
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parents[4]
MVP_ENV = REPO_ROOT / "deploy" / "mvp.env"
COMPOSE_FILE = REPO_ROOT / "docker-compose.yml"

REQUIRED_MVP_ENV = {
    "API_SIMULATION_EXECUTION_BACKEND": "distributed",
    "API_DEPLOYMENT_MODE": "mvp",
    "API_MAX_ACTIVE_SIMULATIONS": "2",
    "API_MAX_SIMULATION_SPIN_COUNT": "10000000",
}

EXPECTED_MVP_SERVICES = {
    "api",
    "postgres",
    "redis",
    "simulation-worker",
    "web",
}


def _parse_env_file(path: Path) -> dict[str, str]:
    values: dict[str, str] = {}
    for line in path.read_text().splitlines():
        stripped = line.strip()
        if not stripped or stripped.startswith("#"):
            continue
        key, _, value = stripped.partition("=")
        values[key.strip()] = value.strip()
    return values


def test_mvp_env_sets_required_variables() -> None:
    env = _parse_env_file(MVP_ENV)
    for key, expected in REQUIRED_MVP_ENV.items():
        assert env.get(key) == expected, f"{key}={env.get(key)!r}, expected {expected!r}"


def test_mvp_celery_worker_concurrency_is_one() -> None:
    compose_text = COMPOSE_FILE.read_text()
    worker_section = compose_text.split("simulation-worker:", 1)[1].split("\n\n", 1)[0]
    assert "command:" in worker_section
    assert "--concurrency=1" in worker_section


def test_mvp_compose_profile_starts_exact_services() -> None:
    result = subprocess.run(
        [
            "docker",
            "compose",
            "--env-file",
            str(MVP_ENV),
            "--profile",
            "mvp",
            "config",
            "--services",
        ],
        cwd=REPO_ROOT,
        check=True,
        capture_output=True,
        text=True,
    )
    services = {line.strip() for line in result.stdout.splitlines() if line.strip()}
    assert services == EXPECTED_MVP_SERVICES


def test_distributed_lifespan_raises_when_redis_unavailable() -> None:
    from contextlib import asynccontextmanager

    from fastapi import FastAPI

    from app.config import Settings
    from app.deployment.redis_check import RedisUnavailableError
    from app.main import _simulation_lifespan

    settings = Settings(
        simulation_execution_backend="distributed",
        redis_url="redis://127.0.0.1:6399/0",
    )
    app = FastAPI()
    app.state.settings = settings

    @asynccontextmanager
    async def run_lifespan():
        async with _simulation_lifespan(app):
            yield

    with pytest.raises(RedisUnavailableError):
        import asyncio

        async def _enter() -> None:
            async with run_lifespan():
                pass

        asyncio.run(_enter())

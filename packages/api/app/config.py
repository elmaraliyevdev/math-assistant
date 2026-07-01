"""Application configuration."""

from __future__ import annotations

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_prefix="API_",
        env_file=".env",
        extra="ignore",
    )

    app_name: str = "Math Assistant API"
    debug: bool = False
    log_level: str = "INFO"
    deployment_mode: str = Field(
        default="mvp",
        description="Deployment profile: mvp (single-server safeguards) or enterprise",
    )
    max_simulation_spin_count: int | None = Field(
        default=None,
        ge=1,
        description="Hard cap on simulation spin count (defaults by deployment_mode)",
    )
    max_active_simulations: int | None = Field(
        default=None,
        ge=0,
        description="Max concurrent pending/running simulations (0 = unlimited)",
    )
    max_recommended_spin_count: int = Field(
        default=10_000_000,
        description="Certified upper bound from Phase 10.5 benchmarks",
    )
    database_url: str = Field(
        default="postgresql+asyncpg://postgres:postgres@localhost:5432/math_assistant",
        description="Async SQLAlchemy database URL (PostgreSQL in production)",
    )
    database_echo: bool = False
    simulation_worker_count: int = Field(
        default=1,
        ge=1,
        description="Number of in-process asyncio simulation job workers",
    )
    simulation_process_pool_workers: int = Field(
        default=2,
        ge=1,
        description="Process pool workers for CPU-bound simulation shard execution",
    )
    simulation_shard_min: int = Field(default=4, ge=1)
    simulation_shard_max: int = Field(default=64, ge=1)
    simulation_spins_per_shard: int = Field(default=1_000, ge=1)
    simulation_execution_backend: str = Field(
        default="inprocess",
        description="Simulation backend: inprocess or distributed",
    )
    redis_url: str = Field(
        default="redis://localhost:6379/0",
        description="Redis URL for distributed simulation broker",
    )
    celery_broker_url: str | None = Field(
        default=None,
        description="Celery broker URL (defaults to redis_url)",
    )
    celery_result_backend: str | None = Field(
        default=None,
        description="Celery result backend URL (defaults to redis_url)",
    )
    celery_task_always_eager: bool = Field(
        default=False,
        description="Run Celery tasks synchronously (for tests)",
    )
    simulation_spin_wins_detail_limit: int = Field(
        default=10_000,
        ge=0,
        description="Collect per-spin wins for mathematics report up to this spin count",
    )
    jwt_secret_key: str = Field(
        default="dev-only-change-me-in-production",
        description="Secret key for signing JWT access and refresh tokens",
    )
    jwt_algorithm: str = "HS256"
    jwt_access_token_expire_minutes: int = Field(default=15, ge=1)
    jwt_refresh_token_expire_days: int = Field(default=30, ge=1)
    sentry_dsn: str | None = Field(default=None, description="Sentry DSN for error monitoring")
    sentry_environment: str = Field(default="development")
    sentry_traces_sample_rate: float = Field(default=0.1, ge=0.0, le=1.0)
    security_headers_enabled: bool = Field(default=True)
    enable_hsts: bool = Field(
        default=False,
        description="Enable Strict-Transport-Security (set true behind HTTPS)",
    )
    hsts_max_age_seconds: int = Field(default=31_536_000, ge=0)
    max_request_body_bytes: int = Field(
        default=10_485_760,
        ge=1,
        description="Maximum request body size in bytes (default 10 MiB)",
    )
    rate_limit_auth_per_minute: int = Field(
        default=20,
        ge=1,
        description="Per-IP rate limit for auth endpoints per minute",
    )
    brute_force_max_attempts: int = Field(
        default=5,
        ge=1,
        description="Failed login attempts before temporary lockout",
    )
    brute_force_lockout_minutes: int = Field(
        default=15,
        ge=1,
        description="Lockout duration after brute-force threshold",
    )
    metrics_bearer_token: str | None = Field(
        default=None,
        description="Optional bearer token required for GET /metrics",
    )
    frontend_url: str = Field(
        default="http://localhost:5173",
        description="Public frontend URL for email links",
    )
    platform_admin_emails: str = Field(
        default="",
        description="Comma-separated admin emails for contact submission review",
    )
    smtp_enabled: bool = Field(
        default=False,
        description="Enable outbound email (password reset, verification)",
    )

    @property
    def resolved_celery_broker_url(self) -> str:
        return self.celery_broker_url or self.redis_url

    @property
    def resolved_celery_result_backend(self) -> str:
        return self.celery_result_backend or self.redis_url

    def uses_distributed_simulation(self) -> bool:
        return self.simulation_execution_backend == "distributed"

    def is_mvp_deployment(self) -> bool:
        return self.deployment_mode.lower() == "mvp"

    def is_enterprise_deployment(self) -> bool:
        return self.deployment_mode.lower() == "enterprise"


def get_settings() -> Settings:
    return Settings()

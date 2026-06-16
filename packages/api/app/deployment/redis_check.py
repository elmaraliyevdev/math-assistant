"""Redis connectivity checks for distributed deployment startup."""

from __future__ import annotations

import redis


class RedisUnavailableError(RuntimeError):
    """Raised when the API cannot reach Redis in distributed mode."""

    def __init__(self, redis_url: str, *, cause: Exception | None = None) -> None:
        self.redis_url = redis_url
        self.cause = cause
        message = (
            f"Redis is unavailable at {redis_url}. "
            "Distributed simulation execution (API_SIMULATION_EXECUTION_BACKEND=distributed) "
            "requires a running Redis broker. Start Redis, verify API_REDIS_URL, or use "
            "API_SIMULATION_EXECUTION_BACKEND=inprocess for local development."
        )
        if cause is not None:
            message = f"{message} ({cause})"
        super().__init__(message)


def verify_redis_connectivity(
    redis_url: str,
    *,
    socket_connect_timeout: float = 3.0,
) -> None:
    client = redis.Redis.from_url(
        redis_url,
        socket_connect_timeout=socket_connect_timeout,
    )
    try:
        if not client.ping():
            raise RedisUnavailableError(redis_url)
    except redis.RedisError as exc:
        raise RedisUnavailableError(redis_url, cause=exc) from exc
    finally:
        client.close()

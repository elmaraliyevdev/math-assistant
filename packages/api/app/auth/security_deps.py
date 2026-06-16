"""Security dependencies for authentication routes."""

from __future__ import annotations

from fastapi import Depends, Request

from app.security.guards import get_auth_rate_limiter, get_brute_force_guard
from app.security.rate_limit import client_ip


def enforce_auth_rate_limit(request: Request) -> None:
    ip = client_ip(
        request.headers.get("x-forwarded-for"),
        request.client.host if request.client else None,
    )
    get_auth_rate_limiter().check(f"auth:{ip}")


def get_client_ip(request: Request) -> str:
    return client_ip(
        request.headers.get("x-forwarded-for"),
        request.client.host if request.client else None,
    )


def brute_force_guard(request: Request):
    return get_brute_force_guard(), get_client_ip(request)

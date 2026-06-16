#!/usr/bin/env python3
"""Lightweight API load benchmark for beta readiness validation."""

from __future__ import annotations

import argparse
import asyncio
import statistics
import time
import uuid

import httpx


async def _register_and_login(client: httpx.AsyncClient, base_url: str) -> dict[str, str]:
    email = f"bench-{uuid.uuid4().hex[:8]}@example.com"
    password = "benchmark-secure-password"
    register = await client.post(
        f"{base_url}/auth/register",
        json={"email": email, "password": password, "fullName": "Benchmark User"},
    )
    register.raise_for_status()
    tokens = register.json()["tokens"]
    return {"Authorization": f"Bearer {tokens['accessToken']}"}


async def _worker(
    client: httpx.AsyncClient,
    base_url: str,
    headers: dict[str, str],
    requests_per_worker: int,
    latencies: list[float],
) -> None:
    for _ in range(requests_per_worker):
        started = time.perf_counter()
        response = await client.get(f"{base_url}/dashboard/summary", headers=headers)
        latencies.append(time.perf_counter() - started)
        response.raise_for_status()


async def run_benchmark(base_url: str, users: int, requests_per_user: int) -> None:
    latencies: list[float] = []
    async with httpx.AsyncClient(timeout=30.0) as client:
        headers = await _register_and_login(client, base_url)
        started = time.perf_counter()
        await asyncio.gather(
            *[
                _worker(client, base_url, headers, requests_per_user, latencies)
                for _ in range(users)
            ],
        )
        elapsed = time.perf_counter() - started

    total_requests = len(latencies)
    print(f"Base URL: {base_url}")
    print(f"Concurrent workers: {users}")
    print(f"Requests per worker: {requests_per_user}")
    print(f"Total requests: {total_requests}")
    print(f"Elapsed seconds: {elapsed:.2f}")
    print(f"Throughput req/s: {total_requests / elapsed:.2f}")
    if latencies:
        sorted_latencies = sorted(latencies)
        p95_index = max(0, int(len(sorted_latencies) * 0.95) - 1)
        print(f"Latency mean ms: {statistics.mean(latencies) * 1000:.2f}")
        print(f"Latency p95 ms: {sorted_latencies[p95_index] * 1000:.2f}")
        print(f"Latency max ms: {max(latencies) * 1000:.2f}")


def main() -> None:
    parser = argparse.ArgumentParser(description="Math Assistant API benchmark")
    parser.add_argument("--base-url", default="http://127.0.0.1:8000")
    parser.add_argument("--users", type=int, default=100)
    parser.add_argument("--requests-per-user", type=int, default=10)
    args = parser.parse_args()
    asyncio.run(run_benchmark(args.base_url, args.users, args.requests_per_user))


if __name__ == "__main__":
    main()

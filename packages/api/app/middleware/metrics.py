"""Prometheus request metrics middleware."""

from __future__ import annotations

from starlette.middleware.base import BaseHTTPMiddleware, RequestResponseEndpoint
from starlette.requests import Request
from starlette.responses import Response

from app.observability.metrics import WORKER_QUEUE_SIZE, observe_request


class MetricsMiddleware(BaseHTTPMiddleware):
    async def dispatch(
        self,
        request: Request,
        call_next: RequestResponseEndpoint,
    ) -> Response:
        dispatcher = getattr(request.app.state, "simulation_dispatcher", None)
        if dispatcher is not None:
            WORKER_QUEUE_SIZE.set(dispatcher.queue.pending_count)

        response = await call_next(request)
        path = request.url.path
        if path != "/metrics":
            observe_request(request.method, path, response.status_code)
        return response

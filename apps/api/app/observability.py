"""Observability: structured request logs plus Prometheus metrics."""

from __future__ import annotations

import logging
import time

from prometheus_client import CONTENT_TYPE_LATEST, Counter, Histogram, generate_latest
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import Response

logger = logging.getLogger("api")
logging.basicConfig(
    level=logging.INFO, format='{"time":"%(asctime)s","msg":"%(message)s"}'
)

REQUEST_LATENCY = Histogram(
    "http_request_duration_seconds",
    "Request latency",
    ["method", "route", "status"],
)
REQUEST_ERRORS = Counter(
    "http_request_errors_total", "Requests with 5xx status", ["method", "route"]
)


def _route_template(request: Request) -> str:
    route = request.scope.get("route")
    return getattr(route, "path", request.url.path)


class ObservabilityMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next) -> Response:
        started = time.perf_counter()
        response = await call_next(request)
        elapsed = time.perf_counter() - started
        route = _route_template(request)
        REQUEST_LATENCY.labels(request.method, route, response.status_code).observe(
            elapsed
        )
        if response.status_code >= 500:
            REQUEST_ERRORS.labels(request.method, route).inc()
        logger.info(
            "%s %s -> %s in %.3fs",
            request.method,
            route,
            response.status_code,
            elapsed,
        )
        return response


def metrics_response() -> Response:
    return Response(generate_latest(), media_type=CONTENT_TYPE_LATEST)

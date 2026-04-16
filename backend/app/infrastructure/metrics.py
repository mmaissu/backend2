"""Prometheus metrics configuration and helpers."""
from prometheus_client import Counter, Histogram, make_asgi_app

from fastapi import FastAPI


REQUEST_COUNT = Counter(
    "http_requests_total",
    "Total HTTP requests",
    ["method", "endpoint", "status"],
)
REQUEST_LATENCY = Histogram(
    "http_request_duration_seconds",
    "HTTP request latency",
    ["method", "endpoint"],
)
REQUEST_ERRORS = Counter(
    "http_request_errors_total",
    "Total HTTP 5xx responses",
    ["method", "endpoint", "status"],
)


def setup_metrics(app: FastAPI) -> None:
    metrics_app = make_asgi_app()
    app.mount("/metrics", metrics_app)


def observe_request(method: str, endpoint: str, status_code: int, duration: float) -> None:
    status = str(status_code)
    REQUEST_COUNT.labels(method=method, endpoint=endpoint, status=status).inc()
    REQUEST_LATENCY.labels(method=method, endpoint=endpoint).observe(duration)
    if status_code >= 500:
        REQUEST_ERRORS.labels(method=method, endpoint=endpoint, status=status).inc()

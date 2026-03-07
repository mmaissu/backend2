"""Prometheus metrics for future monitoring."""
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


def setup_metrics(app: FastAPI) -> None:
    metrics_app = make_asgi_app()
    app.mount("/metrics", metrics_app)

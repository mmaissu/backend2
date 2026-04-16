"""Request metrics and structured request logging middleware."""
import logging
import time

from fastapi import Request
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import JSONResponse, Response

from app.infrastructure.metrics import observe_request

logger = logging.getLogger("app.observability")


class ObservabilityMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next) -> Response:
        start = time.perf_counter()
        method = request.method
        endpoint = request.url.path
        status_code = 500
        try:
            response = await call_next(request)
            status_code = response.status_code
            return response
        except Exception:
            logger.exception(
                "Unhandled exception",
                extra={"request_method": method, "request_path": endpoint},
            )
            return JSONResponse(
                status_code=500,
                content={"detail": "Internal Server Error"},
            )
        finally:
            duration = time.perf_counter() - start
            observe_request(method, endpoint, status_code, duration)
            log_extra = {
                "request_method": method,
                "request_path": endpoint,
                "status_code": status_code,
                "duration_ms": round(duration * 1000, 3),
            }
            if status_code >= 500:
                logger.error("Request completed with server error", extra=log_extra)
            else:
                logger.info("Request completed", extra=log_extra)

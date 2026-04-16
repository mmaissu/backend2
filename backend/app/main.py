"""FastAPI application entry point."""
from contextlib import asynccontextmanager
import logging

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api import router as api_router
from app.config import get_settings
from app.infrastructure.database import init_db
from app.infrastructure.logging import configure_logging
from app.infrastructure.metrics import setup_metrics
from app.middleware.observability import ObservabilityMiddleware
from app.middleware.security import SecurityHeadersMiddleware

logger = logging.getLogger("app.main")


@asynccontextmanager
async def lifespan(app: FastAPI):
    setup_metrics(app)
    await init_db()
    yield


def create_app() -> FastAPI:
    settings = get_settings()
    configure_logging(settings.log_level, settings.log_json)

    app = FastAPI(
        title=settings.app_name,
        lifespan=lifespan,
        docs_url="/api/docs",
        redoc_url="/api/redoc",
    )

    app.add_middleware(ObservabilityMiddleware)
    app.add_middleware(SecurityHeadersMiddleware)

    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.cors_origins_list + ["http://frontend:3000"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    logger.info("Application configured", extra={"config": settings.model_dump_safe()})

    app.include_router(api_router, prefix="/api")

    @app.get("/")
    def root():
        return {
            "message": "Scientific Data Harvester",
            "api": "/api",
            "docs": "/api/docs",
        }

    @app.get("/health")
    def health():
        return {"status": "ok"}

    return app


app = create_app()
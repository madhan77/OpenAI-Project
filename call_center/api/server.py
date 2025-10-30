"""FastAPI application exposing production-ready APIs and UI."""
from __future__ import annotations

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from prometheus_client import make_asgi_app

from ..config import get_config
from ..logging import configure_logging, get_logger
from .dependencies import get_call_center
from .routers import agents, auth, dashboard, interactions


def create_app() -> FastAPI:
    configure_logging()
    config = get_config()
    app = FastAPI(title="Call Center Platform", version="1.0")

    app.add_middleware(
        CORSMiddleware,
        allow_origins=config.allowed_origins,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    app.include_router(auth.router, prefix="/api")
    app.include_router(agents.router, prefix="/api")
    app.include_router(interactions.router, prefix="/api")
    app.include_router(dashboard.router, prefix="/api")

    from ..ui.routes import register_ui

    register_ui(app)

    if config.prometheus_enabled:
        metrics_app = make_asgi_app()
        app.mount("/metrics", metrics_app)

    app.mount("/ui/static", StaticFiles(directory="call_center/ui/static"), name="static")

    logger = get_logger(__name__)

    @app.on_event("startup")
    async def _startup() -> None:  # pragma: no cover - simple wiring
        logger.info("startup", agents=len(get_call_center().agents))

    return app


app = create_app()


__all__ = ["app", "create_app"]


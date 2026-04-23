from __future__ import annotations

from fastapi import FastAPI

from app.api.error_handlers import register_exception_handlers
from app.api.router import api_router
from app.core.config import Settings, get_settings
from app.core.logging import configure_logging


def create_app(settings: Settings | None = None) -> FastAPI:
    app_settings = settings or get_settings()
    configure_logging(app_settings)

    app = FastAPI(
        title=app_settings.app_name,
        debug=app_settings.debug,
        version="0.1.0",
    )
    register_exception_handlers(app)
    app.include_router(api_router, prefix=app_settings.api_v1_prefix)
    return app


app = create_app()

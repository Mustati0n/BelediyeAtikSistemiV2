from fastapi import FastAPI

from backend.app.api.v1.router import api_router
from backend.app.core.config import settings


def create_app() -> FastAPI:
    app = FastAPI(
        title=settings.app_name,
        debug=settings.debug,
        version="0.1.0",
        openapi_url=f"{settings.api_v1_prefix}/openapi.json",
        docs_url=f"{settings.api_v1_prefix}/docs",
        redoc_url=f"{settings.api_v1_prefix}/redoc",
    )
    app.include_router(api_router, prefix=settings.api_v1_prefix)
    return app


app = create_app()


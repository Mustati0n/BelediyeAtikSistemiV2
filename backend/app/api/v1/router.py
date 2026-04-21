from fastapi import APIRouter

from backend.app.api.v1.endpoints import (
    auth,
    finance,
    fleet,
    health,
    maintenance,
    operations,
    recycling,
)

api_router = APIRouter()
api_router.include_router(auth.router, prefix="/auth", tags=["auth"])
api_router.include_router(finance.router)
api_router.include_router(fleet.router)
api_router.include_router(health.router, prefix="/health", tags=["health"])
api_router.include_router(maintenance.router)
api_router.include_router(operations.router, tags=["operations"])
api_router.include_router(recycling.router)

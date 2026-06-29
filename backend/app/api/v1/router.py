from fastapi import APIRouter

from backend.app.api.v1.endpoints import (
    admin,
    auth,
    containers,
    finance,
    fleet,
    health,
    maintenance,
    operations,
    personnel,
    recycling,
    settings,
)

api_router = APIRouter()
api_router.include_router(admin.router)
api_router.include_router(auth.router, prefix="/auth", tags=["auth"])
api_router.include_router(containers.router)
api_router.include_router(finance.router)
api_router.include_router(fleet.router)
api_router.include_router(health.router, prefix="/health", tags=["health"])
api_router.include_router(maintenance.router)
api_router.include_router(operations.router, tags=["operations"])
api_router.include_router(personnel.router)
api_router.include_router(recycling.router)
api_router.include_router(settings.router)

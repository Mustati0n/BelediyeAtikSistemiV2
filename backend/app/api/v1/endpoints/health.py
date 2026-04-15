from fastapi import APIRouter

from backend.app.schemas.common import HealthCheck

router = APIRouter()


@router.get("", response_model=HealthCheck)
def read_health() -> HealthCheck:
    return HealthCheck(status="ok", service="backend")


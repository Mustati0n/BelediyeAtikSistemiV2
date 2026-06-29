from datetime import datetime
from typing import Annotated

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from backend.app.core.deps import require_roles
from backend.app.db.session import get_db
from backend.app.models.entities import Personel
from backend.app.schemas.admin import AdminDashboardSummary, AdminLogListResponse
from backend.app.services.admin import build_admin_dashboard_summary, list_audit_logs

router = APIRouter(prefix="/admin", tags=["admin"])

DBSession = Annotated[Session, Depends(get_db)]
AdminUser = Annotated[Personel, Depends(require_roles("Sistem Yoneticisi"))]


@router.get("/dashboard", response_model=AdminDashboardSummary)
def read_admin_dashboard(db: DBSession, _: AdminUser) -> AdminDashboardSummary:
    return build_admin_dashboard_summary(db)


@router.get("/logs", response_model=AdminLogListResponse)
def read_admin_logs(
    db: DBSession,
    _: AdminUser,
    query: str | None = Query(default=None, max_length=150),
    islem_tipi: str | None = Query(default=None, max_length=120),
    varlik_tipi: str | None = Query(default=None, max_length=120),
    yapan: str | None = Query(default=None, max_length=120),
    date_from: datetime | None = None,
    date_to: datetime | None = None,
    limit: int = Query(default=200, ge=1, le=500),
    offset: int = Query(default=0, ge=0),
) -> AdminLogListResponse:
    return list_audit_logs(
        db,
        query=query,
        islem_tipi=islem_tipi,
        varlik_tipi=varlik_tipi,
        yapan=yapan,
        date_from=date_from,
        date_to=date_to,
        limit=limit,
        offset=offset,
    )

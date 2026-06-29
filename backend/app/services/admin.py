from datetime import datetime
from decimal import Decimal

from sqlalchemy import func, or_, select
from sqlalchemy.orm import Session, joinedload

from backend.app.models.entities import (
    Arac,
    BakimKaydi,
    Gorev,
    IslemLog,
    Konteyner,
    Personel,
    Rol,
    Stok,
    TesisTeslim,
)
from backend.app.models.enums import GorevDurumu
from backend.app.schemas.admin import (
    AdminDashboardSummary,
    AdminLogListResponse,
    AdminModuleSnapshot,
    AdminTaskSnapshot,
    CountByStatus,
    FinanceSnapshot,
    RecentAuditLog,
)
from backend.app.services.finance import profit_loss_summary


def build_admin_dashboard_summary(db: Session) -> AdminDashboardSummary:
    finance = profit_loss_summary(db)

    return AdminDashboardSummary(
        araclar=AdminModuleSnapshot(
            toplam=_count_all(db, Arac),
            durumlar=_count_by(db, Arac.durum),
        ),
        personel=AdminModuleSnapshot(
            toplam=_count_all(db, Personel),
            durumlar=_count_personnel_by_role(db),
        ),
        konteynerler=AdminModuleSnapshot(
            toplam=_count_all(db, Konteyner),
            durumlar=_count_by(db, Konteyner.durum),
        ),
        gorevler=AdminTaskSnapshot(
            toplam=_count_all(db, Gorev),
            durumlar=_count_by(db, Gorev.durum),
            bekleyen=_count_tasks_by_status(db, GorevDurumu.BEKLIYOR),
            atanmis=_count_tasks_by_status(db, GorevDurumu.ATANDI),
            islemde=_count_tasks_by_status(db, GorevDurumu.ISLEMDE),
        ),
        bakim=AdminModuleSnapshot(
            toplam=_count_all(db, BakimKaydi),
            durumlar=_count_by(db, BakimKaydi.durum),
        ),
        tesis_teslimleri=AdminModuleSnapshot(
            toplam=_count_all(db, TesisTeslim),
            durumlar=_count_deliveries(db),
        ),
        stok_toplam_kg=_stock_total(db),
        finans=FinanceSnapshot(**finance),
        son_islemler=_recent_audit_logs(db),
    )


def list_audit_logs(
    db: Session,
    *,
    query: str | None = None,
    islem_tipi: str | None = None,
    varlik_tipi: str | None = None,
    yapan: str | None = None,
    date_from: datetime | None = None,
    date_to: datetime | None = None,
    limit: int = 200,
    offset: int = 0,
) -> AdminLogListResponse:
    stmt = (
        select(IslemLog)
        .options(joinedload(IslemLog.islemi_yapan))
        .outerjoin(IslemLog.islemi_yapan)
    )

    clean_query = query.strip() if query else ""
    if clean_query:
        needle = f"%{clean_query}%"
        stmt = stmt.where(
            or_(
                IslemLog.aciklama.ilike(needle),
                IslemLog.islem_tipi.ilike(needle),
                IslemLog.varlik_tipi.ilike(needle),
            )
        )

    if islem_tipi:
        stmt = stmt.where(IslemLog.islem_tipi.ilike(f"%{islem_tipi.strip()}%"))

    if varlik_tipi:
        stmt = stmt.where(IslemLog.varlik_tipi.ilike(f"%{varlik_tipi.strip()}%"))

    if yapan:
        actor_needle = f"%{yapan.strip()}%"
        stmt = stmt.where(
            or_(Personel.ad_soyad.ilike(actor_needle), Personel.email.ilike(actor_needle))
        )

    if date_from:
        stmt = stmt.where(IslemLog.islem_tarihi >= date_from)

    if date_to:
        stmt = stmt.where(IslemLog.islem_tarihi <= date_to)

    total = int(db.scalar(select(func.count()).select_from(stmt.subquery())) or 0)
    logs = list(
        db.scalars(
            stmt.order_by(IslemLog.islem_tarihi.desc(), IslemLog.id.desc())
            .offset(max(offset, 0))
            .limit(min(max(limit, 1), 500))
        )
    )
    return AdminLogListResponse(toplam=total, loglar=[_audit_log_response(log) for log in logs])


def _count_all(db: Session, model: type) -> int:
    return int(db.scalar(select(func.count()).select_from(model)) or 0)


def _count_by(db: Session, column) -> list[CountByStatus]:
    rows = db.execute(select(column, func.count()).group_by(column).order_by(column.asc())).all()
    return [CountByStatus(durum=str(status.value), sayi=int(count)) for status, count in rows]


def _count_personnel_by_role(db: Session) -> list[CountByStatus]:
    rows = db.execute(
        select(Rol.ad, func.count())
        .join(Personel, Personel.rol_id == Rol.id)
        .group_by(Rol.ad)
        .order_by(func.count().desc())
    )
    return [CountByStatus(durum=role_name, sayi=int(count)) for role_name, count in rows]


def _count_tasks_by_status(db: Session, status: GorevDurumu) -> int:
    return int(db.scalar(select(func.count()).select_from(Gorev).where(Gorev.durum == status)) or 0)


def _count_deliveries(db: Session) -> list[CountByStatus]:
    approved = int(
        db.scalar(
            select(func.count()).select_from(TesisTeslim).where(TesisTeslim.onaylandi_mi.is_(True))
        )
        or 0
    )
    waiting = int(
        db.scalar(
            select(func.count()).select_from(TesisTeslim).where(TesisTeslim.onaylandi_mi.is_(False))
        )
        or 0
    )
    return [
        CountByStatus(durum="Onaylandi", sayi=approved),
        CountByStatus(durum="Beklemede", sayi=waiting),
    ]


def _stock_total(db: Session) -> Decimal:
    total = db.scalar(select(func.coalesce(func.sum(Stok.toplam_miktar_kg), 0)))
    return Decimal(str(total))


def _recent_audit_logs(db: Session) -> list[RecentAuditLog]:
    logs = list(
        db.scalars(
            select(IslemLog)
            .options(joinedload(IslemLog.islemi_yapan))
            .order_by(IslemLog.islem_tarihi.desc(), IslemLog.id.desc())
            .limit(10)
        )
    )
    return [_audit_log_response(log) for log in logs]


def _audit_log_response(log: IslemLog) -> RecentAuditLog:
    return RecentAuditLog(
        id=log.id,
        islem_tipi=log.islem_tipi,
        aciklama=log.aciklama,
        varlik_tipi=log.varlik_tipi,
        varlik_id=log.varlik_id,
        islem_tarihi=log.islem_tarihi.isoformat(),
        yapan=log.islemi_yapan.ad_soyad if log.islemi_yapan else None,
    )

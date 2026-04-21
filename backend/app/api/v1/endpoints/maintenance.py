from typing import Annotated

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from backend.app.core.deps import require_roles
from backend.app.db.session import get_db
from backend.app.models.entities import Personel
from backend.app.schemas.maintenance import (
    ExpenseDecisionResponse,
    MaintenanceCreate,
    MaintenanceResponse,
    PendingExpenseResponse,
)
from backend.app.services.audit import log_action
from backend.app.services.maintenance import (
    approve_expense,
    complete_maintenance_technical,
    create_maintenance_record,
    get_expense_or_404,
    get_maintenance_or_404,
    list_pending_expenses,
    reject_expense,
)

router = APIRouter(tags=["maintenance"])

DBSession = Annotated[Session, Depends(get_db)]
TechUser = Annotated[
    Personel,
    Depends(require_roles("Bakim Teknisyeni", "Sistem Yoneticisi")),
]
FinanceUser = Annotated[
    Personel,
    Depends(require_roles("Muhasebe Personeli", "Sistem Yoneticisi")),
]


@router.post("/maintenance/bakim-kayitlari", response_model=MaintenanceResponse)
def create_maintenance_record_endpoint(
    payload: MaintenanceCreate,
    db: DBSession,
    current_user: TechUser,
) -> MaintenanceResponse:
    bakim = create_maintenance_record(db, payload, current_user)
    log_action(
        db,
        actor=current_user,
        islem_tipi="BakimKaydiOlustur",
        aciklama=f"{bakim.arac.plaka} araci icin bakim kaydi acildi.",
        varlik_tipi="BakimKaydi",
        varlik_id=bakim.id,
    )
    db.commit()
    return _build_maintenance_response(bakim)


@router.post(
    "/maintenance/bakim-kayitlari/{bakim_id}/teknik-tamamla",
    response_model=MaintenanceResponse,
)
def complete_maintenance_technical_endpoint(
    bakim_id: int,
    db: DBSession,
    current_user: TechUser,
) -> MaintenanceResponse:
    bakim = get_maintenance_or_404(db, bakim_id)
    bakim = complete_maintenance_technical(db, bakim)
    log_action(
        db,
        actor=current_user,
        islem_tipi="BakimTeknikTamamla",
        aciklama=f"{bakim.arac.plaka} araci icin teknik bakim tamamlandi.",
        varlik_tipi="BakimKaydi",
        varlik_id=bakim.id,
    )
    db.commit()
    return _build_maintenance_response(bakim)


@router.get("/finance/giderler/bekleyen", response_model=list[PendingExpenseResponse])
def read_pending_expenses(
    db: DBSession,
    _: FinanceUser,
) -> list[PendingExpenseResponse]:
    giderler = list_pending_expenses(db)
    return [
        PendingExpenseResponse(
            id=gider.id,
            tarih=gider.tarih,
            tutar=gider.tutar,
            aciklama=gider.aciklama,
            durum=gider.durum,
            bakim_kaydi_id=gider.bakim_kaydi_id,
            arac_plaka=gider.bakim_kaydi.arac.plaka if gider.bakim_kaydi is not None else None,
        )
        for gider in giderler
    ]


@router.post("/finance/giderler/{gider_id}/onayla", response_model=ExpenseDecisionResponse)
def approve_expense_endpoint(
    gider_id: int,
    db: DBSession,
    current_user: FinanceUser,
) -> ExpenseDecisionResponse:
    gider = get_expense_or_404(db, gider_id)
    gider = approve_expense(db, gider)
    log_action(
        db,
        actor=current_user,
        islem_tipi="GiderOnayla",
        aciklama=f"{gider.id} numarali gider onaylandi.",
        varlik_tipi="GiderKaydi",
        varlik_id=gider.id,
    )
    db.commit()
    return ExpenseDecisionResponse(
        gider_id=gider.id,
        durum=gider.durum,
        mesaj="Gider kaydi onaylandi.",
    )


@router.post("/finance/giderler/{gider_id}/reddet", response_model=ExpenseDecisionResponse)
def reject_expense_endpoint(
    gider_id: int,
    db: DBSession,
    current_user: FinanceUser,
) -> ExpenseDecisionResponse:
    gider = get_expense_or_404(db, gider_id)
    gider = reject_expense(db, gider)
    log_action(
        db,
        actor=current_user,
        islem_tipi="GiderReddet",
        aciklama=f"{gider.id} numarali gider reddedildi.",
        varlik_tipi="GiderKaydi",
        varlik_id=gider.id,
    )
    db.commit()
    return ExpenseDecisionResponse(
        gider_id=gider.id,
        durum=gider.durum,
        mesaj="Gider kaydi reddedildi.",
    )


def _build_maintenance_response(bakim) -> MaintenanceResponse:
    return MaintenanceResponse(
        id=bakim.id,
        arac_id=bakim.arac_id,
        arac_plaka=bakim.arac.plaka,
        tarih=bakim.tarih,
        aciklama=bakim.aciklama,
        maliyet_tl=bakim.maliyet_tl,
        durum=bakim.durum,
        teknik_tamamlanma_tarihi=bakim.teknik_tamamlanma_tarihi,
        arac_durumu=bakim.arac.durum,
        gider_kaydi_id=bakim.gider_kaydi.id if bakim.gider_kaydi is not None else None,
        gider_durumu=bakim.gider_kaydi.durum if bakim.gider_kaydi is not None else None,
    )

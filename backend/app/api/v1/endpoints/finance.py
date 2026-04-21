from decimal import Decimal
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from backend.app.core.deps import require_roles
from backend.app.db.session import get_db
from backend.app.models.entities import Personel
from backend.app.models.enums import OdemeTipi
from backend.app.schemas.finance import (
    BatchSalaryCreate,
    BatchSalaryResponse,
    ProfitLossSummary,
    SalaryCalculationResponse,
    SalaryPaymentCreate,
    SalaryPaymentResponse,
)
from backend.app.services.audit import log_action
from backend.app.services.finance import (
    calculate_salary,
    create_batch_salary_payments,
    create_salary_payment,
    get_personel_or_404,
    profit_loss_summary,
)

router = APIRouter(prefix="/finance", tags=["finance"])

DBSession = Annotated[Session, Depends(get_db)]
FinanceUser = Annotated[
    Personel,
    Depends(require_roles("Muhasebe Personeli", "Sistem Yoneticisi")),
]


@router.get("/maas/personeller/{personel_id}/hesapla", response_model=SalaryCalculationResponse)
def calculate_salary_endpoint(
    personel_id: int,
    db: DBSession,
    _: FinanceUser,
) -> SalaryCalculationResponse:
    personel = get_personel_or_404(db, personel_id)
    cocuk_destegi = Decimal(personel.cocuk_sayisi) * Decimal("1000.00")
    toplam = calculate_salary(personel)
    return SalaryCalculationResponse(
        personel_id=personel.id,
        ad_soyad=personel.ad_soyad,
        taban_maas=personel.taban_maas,
        cocuk_sayisi=personel.cocuk_sayisi,
        cocuk_destegi=cocuk_destegi,
        toplam_hesaplanan_maas=toplam,
    )


@router.post("/maas/tekli", response_model=SalaryPaymentResponse)
def create_salary_payment_endpoint(
    payload: SalaryPaymentCreate,
    db: DBSession,
    current_user: FinanceUser,
) -> SalaryPaymentResponse:
    if payload.odeme_tipi == OdemeTipi.TOPLU:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Toplu odeme icin /finance/maas/toplu endpoint'i kullanilmali.",
        )

    odeme = create_salary_payment(db, payload)
    log_action(
        db,
        actor=current_user,
        islem_tipi="MaasOdeme",
        aciklama=f"{odeme.personel.ad_soyad} icin {odeme.odeme_tipi.value} odeme yapildi.",
        varlik_tipi="MaasOdeme",
        varlik_id=odeme.id,
    )
    db.commit()
    return _build_salary_payment_response(odeme)


@router.post("/maas/toplu", response_model=BatchSalaryResponse)
def create_batch_salary_endpoint(
    payload: BatchSalaryCreate,
    db: DBSession,
    current_user: FinanceUser,
) -> BatchSalaryResponse:
    odemeler = create_batch_salary_payments(db, payload)
    for odeme in odemeler:
        log_action(
            db,
            actor=current_user,
            islem_tipi="TopluMaasOdeme",
            aciklama=f"{odeme.personel.ad_soyad} icin toplu maas odemesi yapildi.",
            varlik_tipi="MaasOdeme",
            varlik_id=odeme.id,
        )
    db.commit()
    responses = [_build_salary_payment_response(odeme) for odeme in odemeler]
    toplam = sum((odeme.tutar for odeme in odemeler), start=Decimal("0.00"))
    return BatchSalaryResponse(
        toplam_odeme=toplam,
        kayit_sayisi=len(responses),
        odemeler=responses,
    )


@router.get("/raporlar/kar-zarar", response_model=ProfitLossSummary)
def read_profit_loss_summary(
    db: DBSession,
    _: FinanceUser,
) -> ProfitLossSummary:
    summary = profit_loss_summary(db)
    return ProfitLossSummary(**summary)


def _build_salary_payment_response(odeme) -> SalaryPaymentResponse:
    return SalaryPaymentResponse(
        id=odeme.id,
        personel_id=odeme.personel_id,
        ad_soyad=odeme.personel.ad_soyad,
        tutar=odeme.tutar,
        odeme_tipi=odeme.odeme_tipi,
        durum=odeme.durum,
        donem_ay=odeme.donem_ay,
        donem_yil=odeme.donem_yil,
        odeme_tarihi=odeme.odeme_tarihi,
    )

from typing import Annotated

from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from backend.app.core.deps import get_current_user, require_roles
from backend.app.db.session import get_db
from backend.app.models.entities import Personel
from backend.app.schemas.operations import (
    CitizenReportCreate,
    CitizenReportResponse,
    ContainerFillUpdateRequest,
    ContainerFillUpdateResponse,
    DriverTaskListResponse,
    TaskAssignRequest,
    TaskCompleteRequest,
    TaskStartResponse,
)
from backend.app.services.audit import log_action
from backend.app.services.operations import (
    assign_task,
    complete_task,
    create_citizen_report,
    get_arac_or_404,
    get_container_or_404,
    get_personel_or_404,
    get_task_with_source,
    list_driver_tasks,
    start_task,
    update_container_fill,
)

router = APIRouter()

DBSession = Annotated[Session, Depends(get_db)]
CurrentUser = Annotated[Personel, Depends(get_current_user)]
AdminUser = Annotated[Personel, Depends(require_roles("Sistem Yoneticisi"))]
DriverUser = Annotated[Personel, Depends(require_roles("Sofor"))]


@router.post(
    "/public/ihbarlar",
    response_model=CitizenReportResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_public_report(
    payload: CitizenReportCreate,
    db: DBSession,
) -> CitizenReportResponse:
    ihbar, gorev = create_citizen_report(db, payload)
    db.commit()
    return CitizenReportResponse(
        ihbar_id=ihbar.id,
        gorev_id=gorev.id,
        durum=ihbar.durum,
        mesaj="Ihbariniz alindi ve gorev havuzuna eklendi.",
    )


@router.post(
    "/operations/konteynerler/{konteyner_id}/doluluk",
    response_model=ContainerFillUpdateResponse,
)
def update_container_fullness(
    konteyner_id: int,
    payload: ContainerFillUpdateRequest,
    db: DBSession,
    current_user: AdminUser,
) -> ContainerFillUpdateResponse:
    konteyner = get_container_or_404(db, konteyner_id)
    konteyner, gorev = update_container_fill(db, konteyner, payload)
    if gorev is not None:
        log_action(
            db,
            actor=current_user,
            islem_tipi="GorevOlusturma",
            aciklama=f"{konteyner.kod} konteyneri icin kritik gorev olusturuldu.",
            varlik_tipi="Gorev",
            varlik_id=gorev.id,
        )
    db.commit()
    return ContainerFillUpdateResponse(
        konteyner_id=konteyner.id,
        doluluk_orani=konteyner.doluluk_orani,
        durum=konteyner.durum,
        gorev_olusturuldu=gorev is not None,
        gorev_id=gorev.id if gorev is not None else None,
    )


@router.post("/operations/gorevler/{gorev_id}/ata", response_model=TaskStartResponse)
def assign_operation_task(
    gorev_id: int,
    payload: TaskAssignRequest,
    db: DBSession,
    current_user: AdminUser,
) -> TaskStartResponse:
    gorev = get_task_with_source(db, gorev_id)
    sofor = get_personel_or_404(db, payload.sofor_id)
    arac = get_arac_or_404(db, payload.arac_id) if payload.arac_id is not None else None
    gorev = assign_task(
        db,
        gorev,
        sofor,
        arac,
        planlanan_tarih=payload.planlanan_tarih,
        sira_no=payload.sira_no,
    )
    log_action(
        db,
        actor=current_user,
        islem_tipi="GorevAtama",
        aciklama=f"{gorev.id} numarali gorev {sofor.ad_soyad} kullanicisine atandi.",
        varlik_tipi="Gorev",
        varlik_id=gorev.id,
    )
    db.commit()
    return TaskStartResponse(
        gorev_id=gorev.id,
        durum=gorev.durum,
        mesaj="Gorev sofore atandi.",
    )


@router.get("/operations/sofor/gorevler/gunluk", response_model=DriverTaskListResponse)
def read_driver_daily_tasks(
    db: DBSession,
    current_user: DriverUser,
) -> DriverTaskListResponse:
    return list_driver_tasks(db, current_user.id)


@router.post("/operations/gorevler/{gorev_id}/baslat", response_model=TaskStartResponse)
def start_operation_task(
    gorev_id: int,
    db: DBSession,
    current_user: DriverUser,
) -> TaskStartResponse:
    gorev = get_task_with_source(db, gorev_id)
    gorev = start_task(db, gorev, current_user.id)
    log_action(
        db,
        actor=current_user,
        islem_tipi="GorevBaslat",
        aciklama=f"{gorev.id} numarali gorev baslatildi.",
        varlik_tipi="Gorev",
        varlik_id=gorev.id,
    )
    db.commit()
    return TaskStartResponse(
        gorev_id=gorev.id,
        durum=gorev.durum,
        mesaj="Gorev baslatildi.",
    )


@router.post("/operations/gorevler/{gorev_id}/sonuclandir", response_model=TaskStartResponse)
def complete_operation_task(
    gorev_id: int,
    payload: TaskCompleteRequest,
    db: DBSession,
    current_user: DriverUser,
) -> TaskStartResponse:
    gorev = get_task_with_source(db, gorev_id)
    gorev = complete_task(
        db,
        gorev,
        current_user.id,
        sonuc=payload.sonuc,
        aciklama=payload.aciklama,
    )
    log_action(
        db,
        actor=current_user,
        islem_tipi="GorevSonuclandir",
        aciklama=f"{gorev.id} numarali gorev {payload.sonuc.value} sonucu ile kapatildi.",
        varlik_tipi="Gorev",
        varlik_id=gorev.id,
    )
    db.commit()
    return TaskStartResponse(
        gorev_id=gorev.id,
        durum=gorev.durum,
        mesaj="Gorev sonuclandirildi.",
    )

from pathlib import Path
from typing import Annotated
from uuid import uuid4

from fastapi import APIRouter, Depends, File, HTTPException, UploadFile, status
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session

from backend.app.core.config import settings
from backend.app.core.deps import get_current_user, require_roles
from backend.app.db.session import get_db
from backend.app.models.entities import Personel
from backend.app.schemas.operations import (
    CitizenReportCreate,
    CitizenPhotoUploadResponse,
    CitizenReportResponse,
    CitizenReportStatusResponse,
    ContainerFillSimulationResponse,
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
    delete_open_task,
    get_arac_or_404,
    get_container_or_404,
    get_personel_or_404,
    get_task_with_source,
    get_public_report_status,
    list_operation_tasks,
    list_driver_tasks,
    start_task,
    simulate_container_fill,
    update_container_fill,
)

router = APIRouter()
UPLOAD_ROOT = Path("uploads/ihbar")
ALLOWED_IMAGE_TYPES = {"image/jpeg": ".jpg", "image/png": ".png", "image/webp": ".webp"}
MAX_IMAGE_BYTES = 5 * 1024 * 1024

DBSession = Annotated[Session, Depends(get_db)]
CurrentUser = Annotated[Personel, Depends(get_current_user)]
AdminUser = Annotated[Personel, Depends(require_roles("Sistem Yoneticisi"))]
TaskViewerUser = Annotated[
    Personel,
    Depends(require_roles("Sistem Yoneticisi", "Geri Donusum Operatoru")),
]
TaskPlannerUser = Annotated[Personel, Depends(require_roles("Geri Donusum Operatoru"))]
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


@router.post("/public/ihbarlar/fotograf", response_model=CitizenPhotoUploadResponse)
async def upload_public_report_photo(
    file: UploadFile = File(...),
) -> CitizenPhotoUploadResponse:
    extension = ALLOWED_IMAGE_TYPES.get(file.content_type or "")
    if extension is None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Sadece JPG, PNG veya WEBP fotograf yuklenebilir.",
        )

    content = await file.read()
    if len(content) > MAX_IMAGE_BYTES:
        raise HTTPException(
            status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
            detail="Fotograf boyutu 5 MB sinirini asamaz.",
        )

    UPLOAD_ROOT.mkdir(parents=True, exist_ok=True)
    filename = f"{uuid4().hex}{extension}"
    target = UPLOAD_ROOT / filename
    target.write_bytes(content)
    return CitizenPhotoUploadResponse(
        fotograf_url=f"{settings.api_v1_prefix}/public/uploads/ihbar/{filename}",
        dosya_adi=file.filename or filename,
        boyut=len(content),
    )


@router.get("/public/uploads/ihbar/{filename}")
def read_public_report_photo(filename: str) -> FileResponse:
    if "/" in filename or "\\" in filename:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Fotograf bulunamadi.")
    target = UPLOAD_ROOT / filename
    if not target.exists():
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Fotograf bulunamadi.")
    return FileResponse(target)


@router.get("/public/ihbarlar/{ihbar_id}", response_model=CitizenReportStatusResponse)
def read_public_report_status(
    ihbar_id: int,
    db: DBSession,
) -> CitizenReportStatusResponse:
    return get_public_report_status(db, ihbar_id)


@router.post(
    "/operations/ihbarlar",
    response_model=CitizenReportResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_admin_report_task(
    payload: CitizenReportCreate,
    db: DBSession,
    current_user: TaskPlannerUser,
) -> CitizenReportResponse:
    ihbar, gorev = create_citizen_report(db, payload)
    log_action(
        db,
        actor=current_user,
        islem_tipi="GorevOlusturma",
        aciklama=f"Haritadan {gorev.id} numarali ihbar gorevi olusturuldu.",
        varlik_tipi="Gorev",
        varlik_id=gorev.id,
    )
    db.commit()
    return CitizenReportResponse(
        ihbar_id=ihbar.id,
        gorev_id=gorev.id,
        durum=ihbar.durum,
        mesaj="Ihbar gorevi olusturuldu ve gorev havuzuna eklendi.",
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


@router.post(
    "/operations/konteynerler/doluluk-simulasyon",
    response_model=ContainerFillSimulationResponse,
)
def simulate_container_fullness(
    db: DBSession,
    current_user: AdminUser,
) -> ContainerFillSimulationResponse:
    result = simulate_container_fill(db)
    if result.guncellenen_konteyner:
        log_action(
            db,
            actor=current_user,
            islem_tipi="DolulukSimulasyon",
            aciklama=(
                f"{result.guncellenen_konteyner} konteyner icin doluluk simulasyonu calistirildi; "
                f"{result.olusan_gorev_sayisi} yeni gorev olustu."
            ),
            varlik_tipi="Konteyner",
            varlik_id=None,
        )
    db.commit()
    return result


@router.post("/operations/gorevler/{gorev_id}/ata", response_model=TaskStartResponse)
def assign_operation_task(
    gorev_id: int,
    payload: TaskAssignRequest,
    db: DBSession,
    current_user: TaskPlannerUser,
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


@router.get("/operations/gorevler", response_model=DriverTaskListResponse)
def read_operation_tasks(
    db: DBSession,
    _: TaskViewerUser,
) -> DriverTaskListResponse:
    return list_operation_tasks(db)


@router.delete("/operations/gorevler/{gorev_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_operation_task(
    gorev_id: int,
    db: DBSession,
    current_user: TaskPlannerUser,
) -> None:
    gorev = get_task_with_source(db, gorev_id)
    delete_open_task(db, gorev)
    log_action(
        db,
        actor=current_user,
        islem_tipi="GorevSil",
        aciklama=f"{gorev_id} numarali gorev havuzdan silindi.",
        varlik_tipi="Gorev",
        varlik_id=gorev_id,
    )
    db.commit()


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

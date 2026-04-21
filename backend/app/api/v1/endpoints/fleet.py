from typing import Annotated

from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from backend.app.core.deps import require_roles
from backend.app.db.session import get_db
from backend.app.models.entities import Personel
from backend.app.schemas.fleet import (
    VehicleCreate,
    VehicleListResponse,
    VehicleResponse,
    VehicleUpdate,
)
from backend.app.services.audit import log_action
from backend.app.services.fleet import (
    create_vehicle,
    get_vehicle_or_404,
    list_vehicles,
    update_vehicle,
)

router = APIRouter(prefix="/fleet", tags=["fleet"])

DBSession = Annotated[Session, Depends(get_db)]
AdminUser = Annotated[Personel, Depends(require_roles("Sistem Yoneticisi"))]


@router.get("/araclar", response_model=VehicleListResponse)
def read_vehicles(
    db: DBSession,
    _: AdminUser,
) -> VehicleListResponse:
    araclar = list_vehicles(db)
    return VehicleListResponse(
        toplam=len(araclar),
        araclar=[VehicleResponse.model_validate(arac) for arac in araclar],
    )


@router.post("/araclar", response_model=VehicleResponse, status_code=status.HTTP_201_CREATED)
def create_vehicle_endpoint(
    payload: VehicleCreate,
    db: DBSession,
    current_user: AdminUser,
) -> VehicleResponse:
    arac = create_vehicle(db, payload)
    log_action(
        db,
        actor=current_user,
        islem_tipi="AracOlustur",
        aciklama=f"{arac.plaka} plakali arac olusturuldu.",
        varlik_tipi="Arac",
        varlik_id=arac.id,
    )
    db.commit()
    return VehicleResponse.model_validate(arac)


@router.patch("/araclar/{arac_id}", response_model=VehicleResponse)
def update_vehicle_endpoint(
    arac_id: int,
    payload: VehicleUpdate,
    db: DBSession,
    current_user: AdminUser,
) -> VehicleResponse:
    arac = get_vehicle_or_404(db, arac_id)
    arac = update_vehicle(db, arac, payload)
    log_action(
        db,
        actor=current_user,
        islem_tipi="AracGuncelle",
        aciklama=f"{arac.plaka} plakali arac guncellendi.",
        varlik_tipi="Arac",
        varlik_id=arac.id,
    )
    db.commit()
    return VehicleResponse.model_validate(arac)

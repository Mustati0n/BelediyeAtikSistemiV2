from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from backend.app.core.deps import require_roles
from backend.app.db.session import get_db
from backend.app.models.entities import Personel, SistemParametresi
from backend.app.schemas.settings import (
    SystemParameterListResponse,
    SystemParameterResponse,
    SystemParameterUpdate,
)
from backend.app.services.audit import log_action
from backend.app.services.settings import list_system_parameters

router = APIRouter(prefix="/settings", tags=["settings"])

DBSession = Annotated[Session, Depends(get_db)]
AdminUser = Annotated[Personel, Depends(require_roles("Sistem Yoneticisi"))]


@router.get("/parameters", response_model=SystemParameterListResponse)
def read_system_parameters(db: DBSession, _: AdminUser) -> SystemParameterListResponse:
    return list_system_parameters(db)


@router.patch("/parameters/{parameter_id}", response_model=SystemParameterResponse)
def update_system_parameter(
    parameter_id: int,
    payload: SystemParameterUpdate,
    db: DBSession,
    current_user: AdminUser,
) -> SistemParametresi:
    parameter = db.get(SistemParametresi, parameter_id)
    if parameter is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Parametre bulunamadi.")

    old_value = parameter.deger
    parameter.deger = payload.deger.strip()
    log_action(
        db,
        actor=current_user,
        islem_tipi="ParametreGuncelle",
        aciklama=f"{parameter.anahtar} parametresi {old_value} -> {parameter.deger} olarak guncellendi.",
        varlik_tipi="SistemParametresi",
        varlik_id=parameter.id,
    )
    db.commit()
    db.refresh(parameter)
    return parameter

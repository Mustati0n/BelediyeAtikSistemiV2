from typing import Annotated

from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from backend.app.core.deps import require_roles
from backend.app.db.session import get_db
from backend.app.models.entities import Personel
from backend.app.schemas.personnel import (
    PersonnelCreate,
    PersonnelListResponse,
    PersonnelResponse,
    PersonnelUpdate,
    RoleResponse,
)
from backend.app.services.audit import log_action
from backend.app.services.personnel import (
    create_personnel,
    get_personnel_or_404,
    list_personnel,
    list_roles,
    update_personnel,
)

router = APIRouter(prefix="/personnel", tags=["personnel"])

DBSession = Annotated[Session, Depends(get_db)]
AdminUser = Annotated[Personel, Depends(require_roles("Sistem Yoneticisi"))]
PersonnelReadUser = Annotated[
    Personel,
    Depends(require_roles("Sistem Yoneticisi", "Muhasebe Personeli", "Geri Donusum Operatoru")),
]


@router.get("/roles", response_model=list[RoleResponse])
def read_roles(db: DBSession, _: AdminUser) -> list[RoleResponse]:
    return [RoleResponse.model_validate(role) for role in list_roles(db)]


@router.get("", response_model=PersonnelListResponse)
def read_personnel(db: DBSession, _: PersonnelReadUser) -> PersonnelListResponse:
    personeller = list_personnel(db)
    return PersonnelListResponse(
        toplam=len(personeller),
        personeller=[PersonnelResponse.model_validate(personel) for personel in personeller],
    )


@router.post("", response_model=PersonnelResponse, status_code=status.HTTP_201_CREATED)
def create_personnel_endpoint(
    payload: PersonnelCreate,
    db: DBSession,
    current_user: AdminUser,
) -> PersonnelResponse:
    personel = create_personnel(db, payload)
    log_action(
        db,
        actor=current_user,
        islem_tipi="PersonelOlustur",
        aciklama=f"{personel.email} personeli olusturuldu.",
        varlik_tipi="Personel",
        varlik_id=personel.id,
    )
    db.commit()
    return PersonnelResponse.model_validate(personel)


@router.patch("/{personel_id}", response_model=PersonnelResponse)
def update_personnel_endpoint(
    personel_id: int,
    payload: PersonnelUpdate,
    db: DBSession,
    current_user: AdminUser,
) -> PersonnelResponse:
    personel = get_personnel_or_404(db, personel_id)
    personel = update_personnel(db, personel, payload)
    log_action(
        db,
        actor=current_user,
        islem_tipi="PersonelGuncelle",
        aciklama=f"{personel.email} personeli guncellendi.",
        varlik_tipi="Personel",
        varlik_id=personel.id,
    )
    db.commit()
    return PersonnelResponse.model_validate(personel)

from typing import Annotated

from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from backend.app.core.deps import require_roles
from backend.app.db.session import get_db
from backend.app.models.entities import Personel
from backend.app.schemas.containers import (
    ContainerCreate,
    ContainerListResponse,
    ContainerResponse,
    ContainerUpdate,
    RegionCreate,
    RegionResponse,
)
from backend.app.services.audit import log_action
from backend.app.services.containers import (
    create_container,
    create_region,
    delete_container,
    get_container_or_404,
    list_containers,
    list_regions,
    update_container,
)

router = APIRouter(prefix="/containers", tags=["containers"])

DBSession = Annotated[Session, Depends(get_db)]
AdminUser = Annotated[Personel, Depends(require_roles("Sistem Yoneticisi"))]


@router.get("/regions", response_model=list[RegionResponse])
def read_regions(db: DBSession, _: AdminUser) -> list[RegionResponse]:
    return [RegionResponse.model_validate(region) for region in list_regions(db)]


@router.post("/regions", response_model=RegionResponse, status_code=status.HTTP_201_CREATED)
def create_region_endpoint(
    payload: RegionCreate,
    db: DBSession,
    current_user: AdminUser,
) -> RegionResponse:
    region = create_region(db, payload)
    log_action(
        db,
        actor=current_user,
        islem_tipi="BolgeOlustur",
        aciklama=f"{region.ad} bolgesi olusturuldu.",
        varlik_tipi="Bolge",
        varlik_id=region.id,
    )
    db.commit()
    return RegionResponse.model_validate(region)


@router.get("", response_model=ContainerListResponse)
def read_containers(db: DBSession, _: AdminUser) -> ContainerListResponse:
    containers = list_containers(db)
    return ContainerListResponse(
        toplam=len(containers),
        konteynerler=[ContainerResponse.model_validate(container) for container in containers],
    )


@router.post("", response_model=ContainerResponse, status_code=status.HTTP_201_CREATED)
def create_container_endpoint(
    payload: ContainerCreate,
    db: DBSession,
    current_user: AdminUser,
) -> ContainerResponse:
    container = create_container(db, payload)
    log_action(
        db,
        actor=current_user,
        islem_tipi="KonteynerOlustur",
        aciklama=f"{container.kod} konteyneri olusturuldu.",
        varlik_tipi="Konteyner",
        varlik_id=container.id,
    )
    db.commit()
    return ContainerResponse.model_validate(container)


@router.patch("/{container_id}", response_model=ContainerResponse)
def update_container_endpoint(
    container_id: int,
    payload: ContainerUpdate,
    db: DBSession,
    current_user: AdminUser,
) -> ContainerResponse:
    container = get_container_or_404(db, container_id)
    container = update_container(db, container, payload)
    log_action(
        db,
        actor=current_user,
        islem_tipi="KonteynerGuncelle",
        aciklama=f"{container.kod} konteyneri guncellendi.",
        varlik_tipi="Konteyner",
        varlik_id=container.id,
    )
    db.commit()
    return ContainerResponse.model_validate(container)


@router.delete("/{container_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_container_endpoint(
    container_id: int,
    db: DBSession,
    current_user: AdminUser,
) -> None:
    container = get_container_or_404(db, container_id)
    container_code = container.kod
    delete_container(db, container)
    log_action(
        db,
        actor=current_user,
        islem_tipi="KonteynerSil",
        aciklama=f"{container_code} konteyneri silindi.",
        varlik_tipi="Konteyner",
        varlik_id=container_id,
    )
    db.commit()

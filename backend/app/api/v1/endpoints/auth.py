from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session

from backend.app.core.deps import get_current_user, require_roles
from backend.app.db.session import get_db
from backend.app.models.entities import Personel
from backend.app.schemas.auth import CurrentUserResponse, TokenResponse
from backend.app.services.audit import log_action
from backend.app.services.auth import authenticate_personel, build_token_response

router = APIRouter()
LoginForm = Annotated[OAuth2PasswordRequestForm, Depends()]
DBSession = Annotated[Session, Depends(get_db)]
CurrentUser = Annotated[Personel, Depends(get_current_user)]
AdminUser = Annotated[Personel, Depends(require_roles("Sistem Yoneticisi"))]


@router.post("/login", response_model=TokenResponse)
def login(
    form_data: LoginForm,
    db: DBSession,
) -> TokenResponse:
    user = authenticate_personel(db, form_data.username, form_data.password)
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Kullanici adi veya sifre hatali.",
        )

    token, expires_at = build_token_response(user)
    log_action(
        db,
        actor=user,
        islem_tipi="Login",
        aciklama=f"{user.email} sisteme giris yapti.",
        varlik_tipi="Personel",
        varlik_id=user.id,
        commit=True,
    )
    return TokenResponse(access_token=token, expires_at=expires_at)


@router.get("/me", response_model=CurrentUserResponse)
def read_me(current_user: CurrentUser) -> CurrentUserResponse:
    return CurrentUserResponse(
        id=current_user.id,
        ad_soyad=current_user.ad_soyad,
        email=current_user.email,
        tc_no=current_user.tc_no,
        aktif_mi=current_user.aktif_mi,
        rol=current_user.rol.ad,
    )


@router.get("/admin-check", response_model=CurrentUserResponse)
def admin_check(current_user: AdminUser) -> CurrentUserResponse:
    return CurrentUserResponse(
        id=current_user.id,
        ad_soyad=current_user.ad_soyad,
        email=current_user.email,
        tc_no=current_user.tc_no,
        aktif_mi=current_user.aktif_mi,
        rol=current_user.rol.ad,
    )

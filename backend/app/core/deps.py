from collections.abc import Callable
from typing import Annotated

from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError
from sqlalchemy import select
from sqlalchemy.orm import Session, selectinload

from backend.app.core.security import decode_access_token
from backend.app.db.session import get_db
from backend.app.models.entities import Personel

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/v1/auth/login")
DBSession = Annotated[Session, Depends(get_db)]
BearerToken = Annotated[str, Depends(oauth2_scheme)]


def get_current_user(
    db: DBSession,
    token: BearerToken,
) -> Personel:
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Kimlik dogrulama basarisiz.",
        headers={"WWW-Authenticate": "Bearer"},
    )

    try:
        payload = decode_access_token(token)
        subject = payload.get("sub")
        if subject is None:
            raise credentials_exception
    except JWTError as exc:
        raise credentials_exception from exc

    stmt = (
        select(Personel)
        .options(selectinload(Personel.rol))
        .where(Personel.id == int(subject), Personel.aktif_mi.is_(True))
    )
    user = db.scalar(stmt)
    if user is None:
        raise credentials_exception
    return user


def require_roles(*roles: str) -> Callable[[Personel], Personel]:
    CurrentUser = Annotated[Personel, Depends(get_current_user)]

    def dependency(current_user: CurrentUser) -> Personel:
        if current_user.rol.ad not in roles:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Bu islem icin yetkiniz yok.",
            )
        return current_user

    return dependency

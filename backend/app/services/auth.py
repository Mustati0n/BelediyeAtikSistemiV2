from datetime import UTC, datetime, timedelta

from sqlalchemy import or_, select
from sqlalchemy.orm import Session, selectinload

from backend.app.core.config import settings
from backend.app.core.security import create_access_token, verify_password
from backend.app.models.entities import Personel


def authenticate_personel(db: Session, username: str, password: str) -> Personel | None:
    stmt = (
        select(Personel)
        .options(selectinload(Personel.rol))
        .where(
            or_(Personel.email == username, Personel.tc_no == username),
            Personel.aktif_mi.is_(True),
        )
    )
    personel = db.scalar(stmt)
    if personel is None:
        return None
    if not verify_password(password, personel.sifre_hash):
        return None
    return personel


def build_token_response(user: Personel) -> tuple[str, datetime]:
    expires_delta = timedelta(minutes=settings.access_token_expire_minutes)
    expires_at = datetime.now(UTC) + expires_delta
    token = create_access_token(
        subject=str(user.id),
        expires_delta=expires_delta,
        role=user.rol.ad,
        email=user.email,
    )
    return token, expires_at


from datetime import datetime

from backend.app.schemas.common import APIModel


class TokenResponse(APIModel):
    access_token: str
    token_type: str = "bearer"
    expires_at: datetime


class CurrentUserResponse(APIModel):
    id: int
    ad_soyad: str
    email: str
    tc_no: str
    aktif_mi: bool
    rol: str


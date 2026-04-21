from decimal import Decimal

from sqlalchemy import select
from sqlalchemy.orm import Session

from backend.app.core.config import settings
from backend.app.core.security import get_password_hash
from backend.app.db.session import SessionLocal
from backend.app.models.entities import Personel, Rol

ROLE_NAMES = [
    ("Sistem Yoneticisi", "Tum sistem yonetim yetkileri."),
    ("Muhasebe Personeli", "Maas, gider, gelir ve rapor yonetimi."),
    ("Bakim Teknisyeni", "Arac bakim ve ariza surecleri."),
    ("Sofor", "Saha operasyon gorevleri."),
    ("Geri Donusum Operatoru", "Tesis teslim, stok ve satis islemleri."),
]


def seed_roles_and_demo_users() -> None:
    with SessionLocal() as db:
        roles = ensure_roles(db)
        ensure_demo_users(db, roles)
        db.commit()


def ensure_roles(db: Session) -> dict[str, Rol]:
    roles: dict[str, Rol] = {}
    for role_name, description in ROLE_NAMES:
        stmt = select(Rol).where(Rol.ad == role_name)
        role = db.scalar(stmt)
        if role is None:
            role = Rol(ad=role_name, aciklama=description)
            db.add(role)
            db.flush()
        roles[role_name] = role
    return roles


def ensure_demo_users(db: Session, roles: dict[str, Rol]) -> None:
    demo_users = [
        {
            "tc_no": "10000000001",
            "ad_soyad": "Demo Admin",
            "email": "admin@belediye.local",
            "telefon": "5551000001",
            "taban_maas": Decimal("50000.00"),
            "cocuk_sayisi": 0,
            "rol": "Sistem Yoneticisi",
            "password": settings.seed_admin_password,
        },
        {
            "tc_no": "10000000002",
            "ad_soyad": "Demo Muhasebe",
            "email": "muhasebe@belediye.local",
            "telefon": "5551000002",
            "taban_maas": Decimal("42000.00"),
            "cocuk_sayisi": 1,
            "rol": "Muhasebe Personeli",
            "password": settings.seed_muhasebe_password,
        },
        {
            "tc_no": "10000000003",
            "ad_soyad": "Demo Bakim",
            "email": "bakim@belediye.local",
            "telefon": "5551000003",
            "taban_maas": Decimal("38000.00"),
            "cocuk_sayisi": 2,
            "rol": "Bakim Teknisyeni",
            "password": settings.seed_bakim_password,
        },
        {
            "tc_no": "10000000004",
            "ad_soyad": "Demo Sofor",
            "email": "sofor@belediye.local",
            "telefon": "5551000004",
            "taban_maas": Decimal("36000.00"),
            "cocuk_sayisi": 2,
            "rol": "Sofor",
            "password": settings.seed_sofor_password,
        },
        {
            "tc_no": "10000000005",
            "ad_soyad": "Demo Operator",
            "email": "operator@belediye.local",
            "telefon": "5551000005",
            "taban_maas": Decimal("35000.00"),
            "cocuk_sayisi": 0,
            "rol": "Geri Donusum Operatoru",
            "password": settings.seed_operator_password,
        },
    ]

    for demo_user in demo_users:
        stmt = select(Personel).where(Personel.email == demo_user["email"])
        personel = db.scalar(stmt)
        if personel is None:
            db.add(
                Personel(
                    tc_no=demo_user["tc_no"],
                    sifre_hash=get_password_hash(demo_user["password"]),
                    ad_soyad=demo_user["ad_soyad"],
                    email=demo_user["email"],
                    telefon=demo_user["telefon"],
                    taban_maas=demo_user["taban_maas"],
                    cocuk_sayisi=demo_user["cocuk_sayisi"],
                    aktif_mi=True,
                    rol=roles[demo_user["rol"]],
                )
            )


if __name__ == "__main__":
    seed_roles_and_demo_users()

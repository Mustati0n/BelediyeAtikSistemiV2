from collections.abc import Generator
from decimal import Decimal

import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker
from sqlalchemy.pool import StaticPool

from backend.app.core.security import get_password_hash
from backend.app.db.base import Base
from backend.app.db.session import get_db
from backend.app.main import create_app
from backend.app.models import entities  # noqa: F401
from backend.app.models.entities import Personel, Rol


@pytest.fixture()
def db_session() -> Generator[Session]:
    engine = create_engine(
        "sqlite://",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    TestingSessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False)
    Base.metadata.create_all(engine)

    session = TestingSessionLocal()
    try:
        yield session
    finally:
        session.close()
        Base.metadata.drop_all(engine)
        engine.dispose()


@pytest.fixture()
def app(db_session: Session):
    application = create_app()

    def override_get_db() -> Generator[Session]:
        yield db_session

    application.dependency_overrides[get_db] = override_get_db
    yield application
    application.dependency_overrides.clear()


@pytest.fixture()
def seeded_users(db_session: Session) -> dict[str, Personel]:
    admin_role = Rol(ad="Sistem Yoneticisi", aciklama="Admin")
    driver_role = Rol(ad="Sofor", aciklama="Driver")
    finance_role = Rol(ad="Muhasebe Personeli", aciklama="Finance")
    tech_role = Rol(ad="Bakim Teknisyeni", aciklama="Tech")
    operator_role = Rol(ad="Geri Donusum Operatoru", aciklama="Operator")
    db_session.add_all([admin_role, driver_role, finance_role, tech_role, operator_role])
    db_session.flush()

    admin = Personel(
        tc_no="10000000001",
        sifre_hash=get_password_hash("Admin123!"),
        ad_soyad="Admin Kullanici",
        email="admin@test.local",
        telefon="5551000001",
        taban_maas=Decimal("50000.00"),
        cocuk_sayisi=0,
        aktif_mi=True,
        rol=admin_role,
    )
    driver = Personel(
        tc_no="10000000002",
        sifre_hash=get_password_hash("Sofor123!"),
        ad_soyad="Sofor Kullanici",
        email="sofor@test.local",
        telefon="5551000002",
        taban_maas=Decimal("35000.00"),
        cocuk_sayisi=1,
        aktif_mi=True,
        rol=driver_role,
    )
    finance = Personel(
        tc_no="10000000003",
        sifre_hash=get_password_hash("Muhasebe123!"),
        ad_soyad="Muhasebe Kullanici",
        email="muhasebe@test.local",
        telefon="5551000003",
        taban_maas=Decimal("42000.00"),
        cocuk_sayisi=1,
        aktif_mi=True,
        rol=finance_role,
    )
    tech = Personel(
        tc_no="10000000004",
        sifre_hash=get_password_hash("Bakim123!"),
        ad_soyad="Bakim Kullanici",
        email="bakim@test.local",
        telefon="5551000004",
        taban_maas=Decimal("39000.00"),
        cocuk_sayisi=2,
        aktif_mi=True,
        rol=tech_role,
    )
    operator = Personel(
        tc_no="10000000005",
        sifre_hash=get_password_hash("Operator123!"),
        ad_soyad="Operator Kullanici",
        email="operator@test.local",
        telefon="5551000005",
        taban_maas=Decimal("34000.00"),
        cocuk_sayisi=0,
        aktif_mi=True,
        rol=operator_role,
    )
    db_session.add_all([admin, driver, finance, tech, operator])
    db_session.commit()
    db_session.refresh(admin)
    db_session.refresh(driver)
    db_session.refresh(finance)
    db_session.refresh(tech)
    db_session.refresh(operator)
    return {
        "admin": admin,
        "driver": driver,
        "finance": finance,
        "tech": tech,
        "operator": operator,
    }

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
    db_session.add_all([admin_role, driver_role])
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
    db_session.add_all([admin, driver])
    db_session.commit()
    db_session.refresh(admin)
    db_session.refresh(driver)
    return {"admin": admin, "driver": driver}

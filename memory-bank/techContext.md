# Tech Context

## Secilen Teknolojiler

- Masaustu personel ekranlari: PySide6 + QtWidgets.
- Backend/API: FastAPI.
- Vatandas web portali: FastAPI + Jinja2.
- ORM: SQLAlchemy 2.0.
- Veritabani: PostgreSQL.
- Auth: JWT.
- Sifre hashleme: Passlib `pbkdf2_sha256`.
- Harita bileseni: web tarafinda Leaflet onerilir; masaustu tarafinda gerekirse Qt WebEngine veya basit liste/koordinat tabanli MVP.
- Test: pytest, httpx test client.
- Migrasyon: Alembic.
- Yerel servisler: Docker Compose ile PostgreSQL.

## Gelistirme Ortami

- CWD: `/home/mustati0n/code-blocks/BelediyeAtikSistemi`
- Son dogrulanan sistem tarihi: 2026-04-21
- Zaman dilimi: Europe/Istanbul
- Repo su an iskeletsiz; proje yapisi kurulacak.
- Git deposu kullanilacak; yerel commit'ler proje fazlarina gore atilacak. Push islemi yalnizca uzak repo tanimlandiktan sonra yapilabilir.
- Faz 1 iskeleti kuruldu ve `.venv` icinde bagimlilikler yuklendi.
- Bu ortamda Docker CLI Podman ile emule ediliyor; `docker compose` komutu `podman-compose` provider'i ile calisiyor.
- Aktif Python surumu: 3.14.3.

## Onerilen Klasor Yapisi

```text
backend/
  app/
    api/
    core/
    db/
    models/
    schemas/
    services/
    templates/
    static/
  alembic/
  tests/
desktop/
  app/
  ui/
docs/
memory-bank/
```

## Frontend Sonradan Eklenecegi Icin API Kurallari

- Endpoint'ler rapordaki UI ekran listesine gore adlandirilacak ve ayrilacak.
- Backend response'lari ekranlarda kullanilacak baslik, durum, tarih, tutar, iliskili varlik ozeti gibi bilgileri dogrudan tasiyacak.
- Pydantic schema'lari frontend icin sozlesme kabul edilecek.
- Backend servisleri UI framework'unden bagimsiz olacak; PySide6, Jinja2 veya ileride React/Vue gibi bir frontend ayni API'yi kullanabilecek.
- Gosterim icin eklenen gecici UI veya test ekranlari cekirdek servis katmanindan bagimsiz bir adapter olarak yazilacak; sonradan silinmesi backend akisini bozmamali.

## Teknik Kisitlar

- MVP'de gercek IoT sensor yok; arka plan simulasyonu kullanilacak.
- MVP'de harici banka/odeme sistemi yok.
- Rota optimizasyonu ileri algoritma degil; oncelik ve siralama tabanli basit planlama ile baslayacak.
- Vatandas tarafi uyeliksiz olacak.
- Toplu maas odemesi ayin 15'i kuralina bagli olacak.

## Kurulumda Beklenenler

- Python sanal ortam veya proje yoneticisi secilecek.
- PostgreSQL Docker Compose ile calistirilacak.
- `.env` ile veritabani, JWT secret ve uygulama ayarlari tasinacak.
- Ilk seed verileri: roller, demo personeller, araclar, bolgeler, konteynerler ve sistem parametreleri.
- Mevcut seed betigi su an roller ve demo personelleri olusturur: `python -m backend.app.db.seed`.

## Faz 1 Dogrulama

- `.venv/bin/python -m pytest`: 2 test gecti.
- `.venv/bin/python -m ruff check .`: gecti.
- `python3 -m compileall backend`: gecti.
- `docker compose config`: gecti.

## Faz 2 Dogrulama

- `.venv/bin/python -m pytest`: 5 test gecti.
- `.venv/bin/python -m ruff check backend`: gecti.
- `python3 -m compileall backend`: gecti.
- `.venv/bin/alembic revision --autogenerate -m "create initial schema"`: gecti.
- `.venv/bin/alembic upgrade head`: gecti.
- `.venv/bin/alembic current`: `00f31c245a1a (head)`.
- `.venv/bin/alembic check`: `No new upgrade operations detected.`

## Faz 3 Dogrulama

- `.venv/bin/python -m ruff check backend`: gecti.
- `.venv/bin/python -m pytest`: 9 test gecti.
- `python3 -m compileall backend`: gecti.
- `.venv/bin/python -m backend.app.db.seed`: gecti.

## Faz 4 Dogrulama

- `.venv/bin/python -m ruff check backend`: gecti.
- `.venv/bin/python -m pytest`: 13 test gecti.
- `python3 -m compileall backend`: gecti.

## Faz 5 Dogrulama

- `.venv/bin/python -m ruff check backend`: gecti.
- `.venv/bin/python -m pytest`: 18 test gecti.
- `python3 -m compileall backend`: gecti.

## Faz 6 Dogrulama

- `.venv/bin/python -m ruff check backend`: gecti.
- `.venv/bin/python -m pytest`: 22 test gecti.
- `python3 -m compileall backend`: gecti.

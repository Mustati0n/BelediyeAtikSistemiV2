# Backend Setup

## Amac

Faz 1 backend iskeleti API-first olacak sekilde kurulur. UI ekranlari daha sonra eklenecegi icin endpoint ve schema yapilari rapordaki ekran ihtiyaclarina gore genisletilecektir.

## Klasorler

- `backend/app/api`: FastAPI route tanimlari.
- `backend/app/core`: Ayarlar, guvenlik ve ortak yardimcilar.
- `backend/app/db`: SQLAlchemy base/session altyapisi.
- `backend/app/models`: Domain veritabani modelleri.
- `backend/app/schemas`: Pydantic request/response sozlesmeleri.
- `backend/app/services`: Is kurallari ve durum gecisi servisleri.
- `backend/tests`: Backend testleri.

## Komutlar

Bagimlilik kurulumu:

```bash
python -m venv .venv
source .venv/bin/activate
python -m pip install -e ".[dev]"
```

API calistirma:

```bash
python -m uvicorn backend.app.main:app --reload
```

PostgreSQL:

```bash
docker compose up -d db
```

Test:

```bash
pytest
```

Demo roller ve kullanicilar:

```bash
python -m backend.app.db.seed
```

Swagger dokumantasyonu:

```bash
/api/v1/docs
```

Bu asamada test etmek icin hazir temel endpoint gruplari:

- `POST /api/v1/auth/login`
- `GET /api/v1/auth/me`
- `POST /api/v1/public/ihbarlar`
- `POST /api/v1/operations/konteynerler/{id}/doluluk`
- `POST /api/v1/operations/gorevler/{id}/ata`
- `GET /api/v1/operations/sofor/gorevler/gunluk`
- `POST /api/v1/operations/gorevler/{id}/baslat`
- `POST /api/v1/operations/gorevler/{id}/sonuclandir`
- `GET /api/v1/fleet/araclar`
- `POST /api/v1/fleet/araclar`
- `PATCH /api/v1/fleet/araclar/{id}`
- `POST /api/v1/maintenance/bakim-kayitlari`
- `POST /api/v1/maintenance/bakim-kayitlari/{id}/teknik-tamamla`
- `GET /api/v1/finance/giderler/bekleyen`
- `POST /api/v1/finance/giderler/{id}/onayla`
- `POST /api/v1/finance/giderler/{id}/reddet`
- `GET /api/v1/finance/maas/personeller/{id}/hesapla`
- `POST /api/v1/finance/maas/tekli`
- `POST /api/v1/finance/maas/toplu`
- `GET /api/v1/finance/raporlar/kar-zarar`

Migrasyon olusturma:

```bash
alembic revision --autogenerate -m "create initial schema"
```

Migrasyon uygulama:

```bash
alembic upgrade head
```

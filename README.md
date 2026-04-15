# Belediye Atik Sistemi

Akilli Sehir Atik Yonetimi ve Geri Donusum Sistemi icin backend/API odakli MVP.

## Durum

Proje Faz 1 asamasinda: FastAPI, SQLAlchemy, PostgreSQL Docker Compose ve test altyapisi kuruluyor. Frontend ve PySide6 ekranlari sonraki fazlarda eklenecek; backend API-first tasarlanir.

## Hızlı Baslangic

Python bagimliliklari kurulduktan sonra:

```bash
python -m uvicorn backend.app.main:app --reload
```

Health endpoint:

```bash
curl http://127.0.0.1:8000/api/v1/health
```

PostgreSQL servisini baslatmak icin:

```bash
docker compose up -d db
```

Bu ortamda Docker CLI Podman ile calisabilir; `docker compose` komutu `podman-compose` uzerinden isleyebilir.


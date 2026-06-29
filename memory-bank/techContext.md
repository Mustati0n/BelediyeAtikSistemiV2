# Tech Context

## Seçilen Teknolojiler

- Backend/API: FastAPI
- ORM: SQLAlchemy 2.x
- Veritabanı: PostgreSQL
- Migrasyon: Alembic
- Kimlik/Yetki: JWT + RBAC
- Şifreleme: Passlib with `pbkdf2_sha256`
- Test: pytest, httpx TestClient
- Frontend: React, TypeScript, Vite
- Harita/rota: Leaflet, OpenStreetMap, OSRM
- Sunucu/servis: Nginx, Docker Compose, HTTPS

## Geliştirme Ortamı

- Proje kökü: /root/BelediyeAtikSistemi
- Aktif Python sürümü: 3.14.3
- Node.js sürümü: v20.20.2
- npm sürümü: 10.8.2
- Zaman dilimi: Europe/Istanbul
- Aktif yayın adresleri:
  - Web panel: http://77.83.37.48
  - API: http://77.83.37.48:8000/api/v1

## Mevcut Klasör Yapısı

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
web/
  src/
  dist/
docs/
memory-bank/
```

## Aktif Mimari Yaklaşım

- Backend, iş kurallarını servis katmanında toplar.
- Frontend, aynı API üzerinden rol bazlı ekranlar üretir.
- Pydantic schema'ları frontend ve backend sözleşmesi olarak kullanılır.
- Harita ve operasyon akışları web tarafında canlı çalışır; masaüstü ekranlar artık ikincil bir legacy akış olarak ele alınır.

## Teknik Kısıtlar

- Gerçek IoT sensör entegrasyonu yoktur; doluluk akışı simülasyon ile üretilir.
- Harici banka veya ödeme sistemi entegre edilmemiştir.
- Rota optimizasyonu temel öncelik ve sıralama tabanlıdır.
- Vatandaş tarafı üyelikli bir sistem değildir; ihbar portalı açık erişimli web formudur.

## Doğrulama Komutları

- Backend testleri: `./.venv/bin/pytest -q`
- Frontend build: `cd web && npm run build`
- Nginx yapılandırma doğrulama: `nginx -t`

## Son Doğrulama Durumu

- Backend: 44 test geçti.
- Frontend: production build başarılı.
- Canlı rotalar ve ana ekranlar doğrulandı.

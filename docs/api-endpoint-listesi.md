# API Endpoint Listesi

Bu belge, mevcut web-MVP için aktif olan ana API endpoint'lerini özetler. Amaç, geliştirme ve sunum sırasında hızlı referans sağlamaktır.

## Kimlik ve yetkilendirme

- POST /api/v1/auth/login
- GET /api/v1/auth/me
- GET /api/v1/auth/admin-check

## Kamu / vatandaşa açık

- POST /api/v1/public/ihbarlar
- POST /api/v1/public/ihbarlar/fotograf
- GET /api/v1/public/ihbarlar/{ihbar_id}
- GET /api/v1/public/uploads/ihbar/{filename}

## Admin

- GET /api/v1/admin/dashboard
- GET /api/v1/admin/logs

## Personel

- GET /api/v1/personnel
- POST /api/v1/personnel
- PATCH /api/v1/personnel/{personel_id}
- GET /api/v1/personnel/roles

## Filo / araç

- GET /api/v1/fleet/araclar
- POST /api/v1/fleet/araclar
- PATCH /api/v1/fleet/araclar/{arac_id}

## Konteyner

- GET /api/v1/containers
- POST /api/v1/containers
- PATCH /api/v1/containers/{container_id}
- DELETE /api/v1/containers/{container_id}
- GET /api/v1/containers/regions
- POST /api/v1/containers/regions
- POST /api/v1/containers/{container_id}/doluluk
- POST /api/v1/operations/konteynerler/doluluk-simulasyon

## Operasyon / görev

- GET /api/v1/operations/gorevler
- POST /api/v1/operations/ihbarlar
- POST /api/v1/operations/gorevler/{gorev_id}/ata
- POST /api/v1/operations/gorevler/{gorev_id}/baslat
- POST /api/v1/operations/gorevler/{gorev_id}/sonuclandir
- GET /api/v1/operations/sofor/gorevler/gunluk

## Bakım

- GET /api/v1/maintenance/bakim-kayitlari
- POST /api/v1/maintenance/bakim-kayitlari
- POST /api/v1/maintenance/bakim-kayitlari/{bakim_id}/tamamla

## Muhasebe

- GET /api/v1/finance/muhasebe
- POST /api/v1/finance/giderler/{gider_id}/onay
- POST /api/v1/finance/giderler/{gider_id}/reddet
- POST /api/v1/finance/gelirler/{gelir_id}/onay
- POST /api/v1/finance/gelirler/{gelir_id}/reddet
- POST /api/v1/finance/maas/hesapla
- POST /api/v1/finance/maas/odeme
- POST /api/v1/finance/maas/odeme/toplu
- GET /api/v1/finance/kar-zarar

## Geri dönüşüm / tesis

- GET /api/v1/recycling/teslimler
- POST /api/v1/recycling/teslimler
- POST /api/v1/recycling/teslimler/{teslim_id}/onay
- POST /api/v1/recycling/teslimler/{teslim_id}/ayristir
- GET /api/v1/recycling/stok-hareketleri
- GET /api/v1/recycling/satislar

## Ayarlar

- GET /api/v1/settings/parameters
- PATCH /api/v1/settings/parameters/{parameter_id}

# System Patterns

## Mimari Yaklasim

Sistem uc ana katmandan olusacak:

- Backend/API: FastAPI servisleri, JWT auth, RBAC, domain servisleri, audit log.
- Veri katmani: PostgreSQL, SQLAlchemy 2.0 modelleri, Alembic migrasyonlari.
- Arayuzler: PySide6 masaustu personel ekranlari ve FastAPI + Jinja2 vatandas portali.

Frontend ve masaustu ekranlari sonraki fazlarda eklenecegi icin backend once API-first yaklasimla kurulacak:

- Her ekran ihtiyaci icin net endpoint, Pydantic request/response schema'lari ve role gore yetki kontrolu.
- Liste endpoint'lerinde filtreleme, sayfalama ve durum bazli sorgu alanlari.
- Detay endpoint'lerinde UI'nin tekrar sorgu yapmak zorunda kalmayacagi iliskili ozet bilgiler.
- Aksiyon endpoint'lerinde durum gecislerini servis katmaninda toplayan tek sorumluluklu fonksiyonlar.

## Domain Omurgasi

Ana varliklar:

- `Rol`
- `Personel`
- `Bolge`
- `Konteyner`
- `Ihbar`
- `Gorev`
- `Arac`
- `BakimKaydi`
- `TesisTeslim`
- `Stok`
- `StokHareketi`
- `Satis`
- `MaasOdeme`
- `GiderKaydi`
- `GelirKaydi`
- `IslemLog`
- Sistem parametreleri icin ek tablo gerekecek: `SistemParametresi`

## Gorev Havuzu Deseni

`Gorev`, operasyonun merkezi kaydidir.

- Kaynak `Ihbar` veya `Konteyner` olabilir.
- Her gorevin tipi `Ihbar` veya `KritikKonteyner` olur.
- Gorev durumlari: `Bekliyor`, `Atandi`, `Islemde`, `Tamamlandi`, `Basarisiz`.
- Gorev sonucu sadece sonuc girildikten sonra dolu olmalidir.
- Ayni konteyner icin acik kritik gorev varken yeni gorev olusmamali.

## Finansal Onay Deseni

Operasyonel islem finansal kaydi dogrudan kesinlestirmez.

- Bakim kaydi, `GiderKaydi` uretir ve durum `Beklemede` olur.
- Fiziksel bakim sureci ile muhasebe gider onayi ayridir. Muhasebe onayi mali kaydin kabuludur; aracin tekrar operasyona donmesi teknik bakim tamamlanma aksiyonuna baglanir.
- Satis kaydi MVP'de dogrudan yapilabilir. Stok satis aninda duser, `GelirKaydi` raporlama/onay icin olusur.
- Satis icin stok rezervasyon veya reddedilince stok geri alma detayi simdilik uygulanmayacak.
- Muhasebe onayi sonrasi durum `Onaylandi` veya `Reddedildi` olur.
- Onaylanan kayitlar raporlamaya dahil edilir.

## RBAC Deseni

- Her personel bir role baglanir.
- Login sonrasi token icinde kullanici kimligi ve rol bilgisi tasinir.
- API endpoint'leri role gore korunur.
- Masaustu ekranlari rol bazli acilir.

## Audit Log Deseni

Kritik islemler `IslemLog` kaydina yazilir:

- Login
- Personel/rol degisikligi
- Sistem parametresi degisikligi
- Bakim kaydi olusturma
- Gider/gelir onay veya red
- Maas odeme
- Satis olusturma
- Gorev sonuclandirma

## Durum Makinesi Notlari

- `Ihbar`: `Bekliyor` -> `GoreveAtandi` -> `Islemde` -> `Cozuldu` veya `Gecersiz`.
- `Konteyner`: `Normal` -> `Izleniyor` -> `Kritik` -> `GoreveAtandi` -> `Bosaltildi`.
- `BakimKaydi`: `Acildi` -> `Incelemede` -> `Tamamlandi` veya `Iptal`.
- `GiderKaydi` / `GelirKaydi`: `Beklemede` -> `Onaylandi` veya `Reddedildi`.
- `MaasOdeme`: `Bekliyor` -> `Odendi` veya `Iptal`.

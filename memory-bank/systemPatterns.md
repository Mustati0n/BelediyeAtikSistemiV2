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

Gecici gosterim/desen kuralı:

- Demo amacli UI, ornek ekran veya test paneli eklenirse bu katman yalnizca API istemcisi gibi davranacak.
- Is kurallari endpoint icine gomulmeyecek; servis katmani kalici entegrasyon noktasi olacak.
- Gecici arayuz silindiginde backend, testler ve API sozlesmesi ayakta kalmali.

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

Uygulama durumu:

- Faz 2'de bu varliklarin ilk SQLAlchemy modelleri yazildi.
- Ilk migration olusturuldu ve PostgreSQL'e uygulandi.
- `Gorev` icin tek kaynak constraint'i DB seviyesinde tanimlandi: ya `ihbar_id` ya `konteyner_id`.
- `MaasOdeme` icin `personel + donem_ay + donem_yil + odeme_tipi` unique constraint'i eklendi.
- `GiderKaydi` ve `GelirKaydi` kaynak kayitlariyla bire bir iliski olacak sekilde unique foreign key ile tasarlandi.

## Gorev Havuzu Deseni

`Gorev`, operasyonun merkezi kaydidir.

- Kaynak `Ihbar` veya `Konteyner` olabilir.
- Her gorevin tipi `Ihbar` veya `KritikKonteyner` olur.
- Gorev durumlari: `Bekliyor`, `Atandi`, `Islemde`, `Tamamlandi`, `Basarisiz`.
- Gorev sonucu sadece sonuc girildikten sonra dolu olmalidir.
- Ayni konteyner icin acik kritik gorev varken yeni gorev olusmamali.

Mevcut uygulama durumu:

- `POST /api/v1/public/ihbarlar` vatandas ihbarini alir ve ayni islemde `Gorev` uretir.
- `POST /api/v1/operations/konteynerler/{id}/doluluk` kritik esik gecildiginde gorev uretir.
- `POST /api/v1/operations/gorevler/{id}/ata` ile yonetici sofor ve arac atayabilir.
- `GET /api/v1/operations/sofor/gorevler/gunluk` atanan gorevleri sira ve oncelige gore listeler.
- `POST /api/v1/operations/gorevler/{id}/baslat` ve `.../sonuclandir` ile sofor durum gecislerini yapar.
- Gorev sonucu `Ihbar` ve `Konteyner` durumlarini servis katmaninda gunceller.

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
- Uygulamada ilk auth endpoint'leri `POST /api/v1/auth/login`, `GET /api/v1/auth/me` ve `GET /api/v1/auth/admin-check` olarak acildi.
- Token alma akisi `OAuth2PasswordRequestForm` ile calisir; `username` alaninda email veya TC no kullanilabilir.
- Yetki kontrolu dependency katmaninda `require_roles(...)` ile yapilir.

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

Mevcut uygulama durumu:

- Login islemi `IslemLog` kaydina yazilmaktadir.
- Audit log yazimi servis katmaninda `log_action(...)` fonksiyonu ile merkezilestirilmistir.

## Durum Makinesi Notlari

- `Ihbar`: `Bekliyor` -> `GoreveAtandi` -> `Islemde` -> `Cozuldu` veya `Gecersiz`.
- `Konteyner`: `Normal` -> `Izleniyor` -> `Kritik` -> `GoreveAtandi` -> `Bosaltildi`.
- `BakimKaydi`: `Acildi` -> `Incelemede` -> `Tamamlandi` veya `Iptal`.
- `GiderKaydi` / `GelirKaydi`: `Beklemede` -> `Onaylandi` veya `Reddedildi`.
- `MaasOdeme`: `Bekliyor` -> `Odendi` veya `Iptal`.

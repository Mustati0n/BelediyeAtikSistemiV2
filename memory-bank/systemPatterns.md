# System Patterns

## Mimari Yaklasim

Sistem uc ana katmandan olusacak:

- Backend/API: FastAPI servisleri, JWT auth, RBAC, domain servisleri, audit log.
- Veri katmani: PostgreSQL, SQLAlchemy 2.0 modelleri, Alembic migrasyonlari.
- Arayuzler: React + Vite web personel paneli, PySide6 masaustu personel ekranlari ve ayri vatandas ihbar portali.

Frontend ve masaustu ekranlari sonraki fazlarda eklenecegi icin backend once API-first yaklasimla kurulacak:

- Her ekran ihtiyaci icin net endpoint, Pydantic request/response schema'lari ve role gore yetki kontrolu.
- Liste endpoint'lerinde filtreleme, sayfalama ve durum bazli sorgu alanlari.
- Detay endpoint'lerinde UI'nin tekrar sorgu yapmak zorunda kalmayacagi iliskili ozet bilgiler.
- Aksiyon endpoint'lerinde durum gecislerini servis katmaninda toplayan tek sorumluluklu fonksiyonlar.

Gecici gosterim/desen kuralı:

- Demo amacli UI, ornek ekran veya test paneli eklenirse bu katman yalnizca API istemcisi gibi davranacak.
- Is kurallari endpoint icine gomulmeyecek; servis katmani kalici entegrasyon noktasi olacak.
- Gecici arayuz silindiginde backend, testler ve API sozlesmesi ayakta kalmali.
- Demo seed tekrar calistirilabilir/idempotent tasarlanacak; benzersiz alanlar (`plaka`, `kod`, `email`, `bolge.ad`) ile mevcut kayit kontrolu yapilacak.
- Demo seed operasyonel zinciri gosterecek minimum canli veri uretir: arac, bolge, konteyner, acik gorev, bakim/gider, tesis teslimi, stok ve gelir.

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
- Web `/vatandas` ve `/ihbar` sayfalari uyeliksiz vatandas ihbar formudur; konum tarayicidan alinabilir veya elle girilebilir.
- `POST /api/v1/operations/konteynerler/{id}/doluluk` kritik esik gecildiginde gorev uretir.
- `POST /api/v1/operations/gorevler/{id}/ata` ile yonetici sofor ve arac atayabilir.
- `GET /api/v1/operations/gorevler` ile yonetici acik gorev havuzunu listeler.
- `GET /api/v1/operations/sofor/gorevler/gunluk` atanan gorevleri sira ve oncelige gore listeler.
- `POST /api/v1/operations/gorevler/{id}/baslat` ve `.../sonuclandir` ile sofor durum gecislerini yapar.
- Gorev sonucu `Ihbar` ve `Konteyner` durumlarini servis katmaninda gunceller.
- Web admin `Gorevler` ekrani acik gorev havuzunu listeler ve atama endpoint'ini kullanir.
- Web admin `Konteyner` ekraninda doluluk guncellemesi operasyon endpoint'ini kullanir; kritik esik gorev uretirse gorev numarasi kullaniciya gosterilir.
- `GET /api/v1/admin/dashboard` admin denetim merkezinin tek okuma endpoint'idir; arac, personel, konteyner, gorev, bakim, tesis, stok, finans ve audit log ozetlerini birlestirir.
- Web `/admin` ana ekrani bu endpoint'i kullanir; kartlar ilgili detay sayfalarina navigasyon verir, operasyonel islem yine ilgili modullerden yapilir.

## Finansal Onay Deseni

Operasyonel islem finansal kaydi dogrudan kesinlestirmez.

- Bakim kaydi, `GiderKaydi` uretir ve durum `Beklemede` olur.
- Fiziksel bakim sureci ile muhasebe gider onayi ayridir. Muhasebe onayi mali kaydin kabuludur; aracin tekrar operasyona donmesi teknik bakim tamamlanma aksiyonuna baglanir.
- Satis kaydi MVP'de dogrudan yapilabilir. Stok satis aninda duser, `GelirKaydi` raporlama/onay icin olusur.
- Satis icin stok rezervasyon veya reddedilince stok geri alma detayi simdilik uygulanmayacak.
- Muhasebe onayi sonrasi durum `Onaylandi` veya `Reddedildi` olur.
- Onaylanan kayitlar raporlamaya dahil edilir.

Mevcut uygulama durumu:

- `POST /api/v1/maintenance/bakim-kayitlari` bakim kaydi ile birlikte bekleyen `GiderKaydi` uretir.
- `GET /api/v1/maintenance/bakim-kayitlari` teknik ekip ve admin icin bakim gecmisini arac/gider ozetleriyle listeler.
- `POST /api/v1/maintenance/bakim-kayitlari/{id}/teknik-tamamla` araci teknik olarak tekrar aktif hale getirir.
- `GET /api/v1/finance/giderler/bekleyen`, `.../onayla` ve `.../reddet` muhasebe akislarini yurutur.
- `GET /api/v1/finance/maas/personeller/{id}/hesapla` maas hesap ozeti dondurur.
- `POST /api/v1/finance/maas/tekli` avans ve tekli odemeleri alir.
- `POST /api/v1/finance/maas/toplu` ayin 15'i kuralini uygular.
- `GET /api/v1/finance/raporlar/kar-zarar` onayli gelir/gider ozetini dondurur.
- Web muhasebe sayfasi gider/gelir onay kartlari, maas formu ve finans ozet kartlarini ayni ekranda toplar.

Tesis/stok/satis uygulama durumu:

- `POST /api/v1/recycling/teslimler` soforun tesis teslim kaydi acmasini saglar.
- `GET /api/v1/recycling/teslimler` operatorun tesis teslimlerini listelemesini saglar.
- `POST /api/v1/recycling/teslimler/{id}/onayla` operator teslimi devralir.
- `POST /api/v1/recycling/teslimler/{id}/ayristir` teslim edilen atigi stok hareketlerine donusturur.
- `GET /api/v1/recycling/stoklar` mevcut stok durumunu listeler.
- `POST /api/v1/recycling/satislar` stoktan duserek satis ve bekleyen `GelirKaydi` olusturur.
- `GET /api/v1/recycling/gelirler/bekleyen`, `.../onayla` ve `.../reddet` muhasebe gelir akislarini yurutur.
- Web geri donusum operatoru sayfasi teslim onay, ayristirma, stok ve satisi tek operasyon ekraninda toplar.

## RBAC Deseni

- Her personel bir role baglanir.
- Login sonrasi token icinde kullanici kimligi ve rol bilgisi tasinir.
- API endpoint'leri role gore korunur.
- Web panel ve masaustu ekranlari rol bazli acilir.
- Web panelde admin disindaki roller sadece kendi section'larini gorebilir; URL guard yetkisiz section'a girisi role ana sayfasina yonlendirir.
- Admin, kendi yonetim section'inda islem yapar; bakim/muhasebe/tesis gibi cross-module ekranlari izleme modunda gorur ve operasyon butonlari pasiftir.
- Admin disi roller icin section kok path'leri ara ozet ekraninda kalmaz; login ve ana menu ilgili canli is ekranina yonlenir.
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

# Active Context

## Guncel Odak

Git/GitHub akisi, Faz 1 backend iskeleti, Faz 2 domain modeli, Faz 3 auth/RBAC/audit temeli ve Faz 4 operasyon/gorev havuzu temeli tamamlandi. Sonraki adim Faz 5 kapsaminda bakim ve muhasebe akislarini API seviyesinde kurmak olacak.

## Son Degisiklikler

- Tasarim raporu okundu ve ana basliklar cikarildi.
- Core Memory Bank dosyalari olusturuldu.
- UML gorsellerindeki use-case, domain modeli ve sequence akislari ilk dogrulama icin notlandi.
- Kullanici backend/API + veritabani ile baslamayi onayladi.
- Kullanici PostgreSQL icin Docker Compose yaklasimini onayladi.
- Kullanici bakim teknik sureci ile muhasebe gider onay surecinin ayrik tutulmasini onayladi.
- Kullanici vatandas fotograf yuklemenin opsiyonel olmasini onayladi.
- Kullanici PySide6 sofor ekraninda haritanin sonraki faza alinmasini onayladi.
- Kullanici projenin git deposu olarak baslatilmasini onayladi.
- Yerel Git deposu `main` dali ile baslatildi.
- `.gitignore` ve `docs/git-remote-setup.md` eklendi.
- GitHub remote bilgisi alindi: `https://github.com/Mustati0n/BelediyeAtikSistemiV2.git`.
- Ilk commit atildi: `f2e2501 Initialize project memory bank and Git setup`.
- Remote `origin` eklendi.
- Push basarili oldu; `main` dali `origin/main` ile eslesiyor.
- Faz 1 backend/API iskeleti kuruldu.
- FastAPI app factory, `/api/v1/health`, SQLAlchemy base/session, Alembic, Docker Compose PostgreSQL, `.env.example`, `pyproject.toml`, backend dokumani ve test altyapisi eklendi.
- Bagimlilikler `.venv` icine kuruldu.
- Dogrulama: `pytest` 2 test geçti, `ruff check .` geçti, `python3 -m compileall backend` geçti, `docker compose config` geçti.
- Python 3.14 ortaminda `TestClient` tabanli ilk test askida kaldigi icin health testi simdilik handler/app sozlesmesi uzerinden yazildi.
- Faz 2 domain modelleri eklendi: enumlar, `Personel`, `Rol`, `Bolge`, `Konteyner`, `Ihbar`, `Gorev`, `Arac`, `BakimKaydi`, `MaasOdeme`, `GiderKaydi`, `GelirKaydi`, `TesisTeslim`, `Stok`, `StokHareketi`, `Satis`, `IslemLog`, `SistemParametresi`.
- SQLAlchemy iliskileri, check constraint'ler, index'ler ve nullability kurallari modellere islendi.
- Alembic autogenerate ile ilk migration olusturuldu: `00f31c245a1a_create_initial_schema.py`.
- `alembic upgrade head` uygulandi ve `alembic check` ile model-DB senkronu dogrulandi.
- Toplam test sayisi 5 oldu; hepsi gecti.
- JWT tabanli auth katmani eklendi; `POST /api/v1/auth/login`, `GET /api/v1/auth/me` ve `GET /api/v1/auth/admin-check` endpoint'leri yazildi.
- `OAuth2PasswordBearer` tabanli mevcut kullanici ve rol kontrol dependency'leri eklendi.
- Sifre hashleme `pbkdf2_sha256` ile kuruldu; Python 3.14 ortaminda `passlib+bcrypt` uyumsuzlugu yuzunden bu yontem secildi.
- Audit servis katmani eklendi ve login islemi `IslemLog` tablosuna yazilacak sekilde baglandi.
- Roller ve demo personeller icin seed betigi eklendi: `python -m backend.app.db.seed`.
- Auth/RBAC testleri eklendi; toplam backend test sayisi 9 oldu ve hepsi gecti.
- Gercek PostgreSQL veritabaninda seed komutu calistirildi.
- Vatandas ihbari icin public endpoint eklendi: `POST /api/v1/public/ihbarlar`.
- Ihbar olusunca otomatik `Gorev` kaydi ureten servis katmani yazildi.
- Konteyner doluluk guncelleme ve kritik seviyede gorev olusturma akisi eklendi.
- Ayni konteyner icin acik gorev varsa ikinci kritik gorev olusmasini engelleyen kontrol servis katmanina eklendi.
- Sistem yoneticisi icin gorev atama endpoint'i eklendi.
- Sofor icin gunluk gorev listeleme, gorev baslatma ve gorev sonuclandirma endpoint'leri eklendi.
- Gorev sonuclari ihbar ve konteyner durumlarini guncelleyecek sekilde baglandi.
- Operasyon testleri eklendi; toplam backend test sayisi 13 oldu ve hepsi gecti.

## Aktif Kararlar

- Yeni domain modeli esas alinacak; eski modeldeki rol bazli kalitim yerine `Personel` + `Rol` yapisi kullanilacak.
- Vatandas ihbari ve kritik konteyner olaylari dogrudan sofore atanmayacak; once `Gorev` havuzuna girecek.
- MVP'de IoT verisi arka plan simulasyon servisiyle uretilecek.
- Backend FastAPI, ORM SQLAlchemy 2.0, veritabani PostgreSQL, personel masaustu ekranlari PySide6 olacak.
- PostgreSQL Docker Compose ile ayaga kaldirilacak.
- Frontend sonradan eklenecek; backend once API sozlesmesi, Pydantic schema'lari ve UI dostu response yapilariyla kurulacak.
- Sistem moduler tutulacak; backend, servis katmani ve schema sozlesmeleri kalici olacak, gosterim icin gerekirse gecici/demo UI katmani kolayca sokulebilir sekilde eklenecek.
- Vatandas portali FastAPI + Jinja2 ile hafif web katmani olarak daha sonraki fazda baslatilacak.
- Bakim kaydi olustugunda muhasebeye bekleyen gider kaydi hemen duser; ancak fiziksel bakim tamamlanmasi muhasebe onayindan ayridir.
- Satis MVP'de dogrudan yapilabilir olacak; stok satis aninda duser, gelir kaydi muhasebe raporlama/onay akisi icin olusur. Stok rezervasyon/geri alma detayi simdilik eklenmeyecek.
- Vatandas fotograf yukleme opsiyonel olacak.
- Sofor ekraninda ilk MVP gorev listesi + koordinat ile ilerleyebilir; harita entegrasyonu sonraki UI fazina yazildi.
- Login akisi ilk asamada OAuth2 password form (`username` alaninda email veya TC no) ile calisacak.
- JWT icinde kullanici kimligi `sub` alaninda tutulacak; rol bilgisi DB'den yuklenerek yetki kontrolu yapilacak.
- Demo seed kullanicilari proje ici gelistirme amacli tutulacak; sifreleri `.env` ile degistirilebilir olacak.
- Gecici gosterim ekranlari veya demo endpoint'leri asil is kurallarindan ayrik tutulacak; arkadasin frontend'i geldiginde backend'i yeniden yazma ihtiyaci olmadan entegrasyon yapilacak.
- Operasyon tarafinda test ve demo ihtiyaci icin public/report ve role-protected endpoint'ler kuruldu; bunlar kalici API sozlesmesinin parcasi olarak tasarlandi.

## Dikkat Edilecek Noktalar

- Memory Bank her yeni gorevin basinda tamamen okunmali.
- Rapor disindaki kod uygulanmadan once veri modeli ve akislardaki belirsizlikler netlestirilmeli.
- API endpoint'leri markdown raporundaki UI ekranlarina gore ayrilmali; frontend sonra gelse de ekranlarin ihtiyac duyacagi liste, filtre, detay ve aksiyon cevaplari bastan dusunulmeli.
- Tesis/stok/satis sequence diyagraminin PlantUML kodu raporda gorunmuyor; gorselden yeniden yazilmasi gerekebilir.

## Sonraki Adim

Faz 5'e gecilecek: arac CRUD, bakim kaydi, bakimdan gider kaydi uretimi, muhasebe gider onay/red akisi, maas/avans/tekli/toplu odeme endpoint'leri ve gelir-gider ozetleri.

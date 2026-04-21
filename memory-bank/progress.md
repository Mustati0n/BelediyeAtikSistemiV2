# Progress

## Durum Ozeti

Faz 6 tamamlandi. Backend/API iskeleti ve domain modeli ustune auth, gorev havuzu, bakim, muhasebe, tesis teslim, stok ve satis endpoint'leri kuruldu. Sonraki adim Faz 7: arayuzler ve demo deneyimi.

## Tamamlananlar

- [x] Repo baslangic durumu incelendi.
- [x] Tasarim raporu satir sayisi ve ana basliklari kontrol edildi.
- [x] Kapsam, roller, moduller ve teknoloji stack'i cikarildi.
- [x] Memory Bank klasoru olusturuldu.
- [x] Core Memory Bank dosyalari yazildi.
- [x] UML tutarlilik raporu yazildi.
- [x] Fazlara ayrilmis is akisi planı yazildi.
- [x] Backend/API ile baslama karari alindi.
- [x] Frontend'in sonradan eklenecegi ve backend'in API-first tasarlanacagi karari alindi.
- [x] PostgreSQL icin Docker Compose karari alindi.
- [x] Bakim teknik sureci ile muhasebe gider onayinin ayrilmasi karari alindi.
- [x] Satisin MVP'de dogrudan yapilmasi karari alindi.
- [x] Vatandas fotograf yuklemenin opsiyonel olmasi karari alindi.
- [x] Sofor haritasinin sonraki UI iterasyonuna alinmasi karari alindi.
- [x] Git deposu kullanma karari alindi.
- [x] Yerel Git deposu baslatildi.
- [x] `.gitignore` eklendi.
- [x] Uzak Git repo baglama dokumani eklendi.
- [x] GitHub remote URL ve commit kimligi alindi.
- [x] Ilk commit atildi: `f2e2501 Initialize project memory bank and Git setup`.
- [x] Remote `origin` eklendi.
- [x] GitHub push basarili; `main` dali `origin/main` ile eslesiyor.
- [x] Python proje yapisi kuruldu.
- [x] Backend klasor yapisi olusturuldu.
- [x] FastAPI uygulama girisi ve `/api/v1/health` endpoint'i eklendi.
- [x] SQLAlchemy `Base`, engine ve session altyapisi eklendi.
- [x] Docker Compose PostgreSQL servis tanimi eklendi.
- [x] Alembic migrasyon altyapisi eklendi.
- [x] `.env.example` ve ayar katmani eklendi.
- [x] API-first klasor ayrimi, base schema ve servis katmani yerleri eklendi.
- [x] Sanal ortamda bagimlilik kurulumu dogrulandi.
- [x] Test, lint, compile ve compose config kontrolleri yapildi.
- [x] Tum domain enumlari eklendi.
- [x] SQLAlchemy domain modelleri ve iliskiler yazildi.
- [x] Check constraint, unique constraint, index ve nullable kararları modellere islendi.
- [x] Ilk Alembic migration olusturuldu: `00f31c245a1a_create_initial_schema.py`.
- [x] `alembic upgrade head` ile veritabani semasi olusturuldu.
- [x] `alembic check` ile model ve migration senkronu dogrulandi.
- [x] Backend test sayisi 5'e cikti ve hepsi gecti.
- [x] JWT tabanli sifreleme ve token uretim altyapisi eklendi.
- [x] `POST /api/v1/auth/login`, `GET /api/v1/auth/me` ve `GET /api/v1/auth/admin-check` endpoint'leri yazildi.
- [x] Rol bazli endpoint koruma dependency'leri eklendi.
- [x] Login islemi icin audit log yazimi eklendi.
- [x] Roller ve demo personeller icin seed betigi yazildi.
- [x] `.env.example` seed sifre ayarlariyla guncellendi.
- [x] Auth/RBAC testleri eklendi; backend test sayisi 9'a cikti ve hepsi gecti.
- [x] Gercek PostgreSQL veritabaninda seed komutu calistirildi.
- [x] Vatandas ihbari icin public endpoint yazildi.
- [x] Ihbardan otomatik gorev olusturma akisi eklendi.
- [x] Konteyner doluluk guncelleme ve kritik gorev uretme servisi eklendi.
- [x] Ayni konteyner icin tekrar acik gorev olusmasini engelleyen kontrol eklendi.
- [x] Sistem yoneticisi icin gorev atama endpoint'i eklendi.
- [x] Sofor gunluk gorev listeleme endpoint'i eklendi.
- [x] Sofor gorev baslatma ve sonuclandirma endpoint'leri eklendi.
- [x] Operasyon/gorev havuzu testleri eklendi; backend test sayisi 13'e cikti ve hepsi gecti.
- [x] Swagger ve test icin temel operasyon endpoint listesi dokumante edildi.
- [x] Arac listeleme, olusturma ve guncelleme endpoint'leri eklendi.
- [x] Bakim kaydi olusturma ve teknik tamamlama endpoint'leri eklendi.
- [x] Bakim kaydindan bekleyen gider kaydi uretimi eklendi.
- [x] Muhasebe bekleyen gider listeleme ve gider onay/red endpoint'leri eklendi.
- [x] Maas hesaplama endpoint'i eklendi.
- [x] Avans/tekli odeme ve toplu maas odemesi endpoint'leri eklendi.
- [x] Toplu odemede ayin 15'i kuralı eklendi.
- [x] Kar-zarar rapor ozeti endpoint'i eklendi.
- [x] Bakim/muhasebe testleri eklendi; backend test sayisi 18'e cikti ve hepsi gecti.
- [x] Soforun tesis teslim endpoint'i eklendi.
- [x] Operator teslim onayi endpoint'i eklendi.
- [x] Ayristirma ve stok hareketi endpoint'i eklendi.
- [x] Stok listeleme endpoint'i eklendi.
- [x] Satis kaydi ve stok dusumu eklendi.
- [x] Bekleyen gelir kaydi uretimi eklendi.
- [x] Muhasebe gelir onay/red endpoint'leri eklendi.
- [x] Geri donusum testleri eklendi; backend test sayisi 22'ye cikti ve hepsi gecti.
- [x] Swagger ve test icin geri donusum endpoint listesi dokumante edildi.

## Devam Edenler

- [ ] Faz 7 arayuzler ve demo deneyimi.

## Siradakiler

- [ ] Vatandas ihbar portalinin hafif arayuzu.
- [ ] Gecici demo ekranlari veya test panelleri.
- [ ] PySide6 personel ekranlari icin adapter dusuncesi.
- [ ] Arkadas frontend'i ile entegrasyon icin ornek veri akislari.
- [ ] Vatandas ihbar portali.
- [ ] PySide6 personel ekranlari.

## Bilinen Riskler

- Python 3.14 ortaminda `fastapi.testclient.TestClient` ile ilk health testi askida kaldi; Faz 1 testi simdilik handler/app sozlesmesi uzerinden dogrulandi. Uygulama gelistikce ASGI/HTTP test yaklasimi tekrar degerlendirilecek.
- Python 3.14 ortaminda `passlib+bcrypt` uyumsuzlugu goruldu; sifre hashleme `pbkdf2_sha256` ile kurulup test edildi.
- Tesis/stok/satis sequence diyagraminin PlantUML kodu raporda yok; uygulama oncesi yeniden yazilmasi iyi olur.
- `MaasOdeme` icin `personel + donem + odeme_tipi` unique constraint DB seviyesinde tanimli; avans icin coklu odeme ihtiyaci dogarsa bu kural yeniden ele alinabilir.
- Masaustu harita gosterimi icin PySide6 tarafinda teknik secim net degil; ilk MVP'de gorev listesi + koordinat ile ilerlenebilir.
- Satisin dogrudan yapilmasi stok rezervasyon/geri alma detayini disarida birakir; sonraki versiyonda gerekirse genisletilecek.

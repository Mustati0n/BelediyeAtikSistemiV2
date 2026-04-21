# Progress

## Durum Ozeti

Faz 2 tamamlandi. Backend/API iskeleti ustune tam domain modeli, SQLAlchemy iliskileri, enumlar, ilk Alembic migration ve PostgreSQL semasi kuruldu. Sonraki adim Faz 3: auth, RBAC ve audit altyapisi.

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

## Devam Edenler

- [ ] Faz 3 auth, RBAC ve audit altyapisi.

## Siradakiler

- [ ] Auth/RBAC altyapisinin kurulmasi.
- [ ] Ilk API endpoint'leri ve testleri.
- [ ] Vatandas ihbar portali.
- [ ] PySide6 personel ekranlari.

## Bilinen Riskler

- Python 3.14 ortaminda `fastapi.testclient.TestClient` ile ilk health testi askida kaldi; Faz 1 testi simdilik handler/app sozlesmesi uzerinden dogrulandi. Uygulama gelistikce ASGI/HTTP test yaklasimi tekrar degerlendirilecek.
- Tesis/stok/satis sequence diyagraminin PlantUML kodu raporda yok; uygulama oncesi yeniden yazilmasi iyi olur.
- `MaasOdeme` icin `personel + donem + odeme_tipi` unique constraint DB seviyesinde tanimli; avans icin coklu odeme ihtiyaci dogarsa bu kural yeniden ele alinabilir.
- Masaustu harita gosterimi icin PySide6 tarafinda teknik secim net degil; ilk MVP'de gorev listesi + koordinat ile ilerlenebilir.
- Satisin dogrudan yapilmasi stok rezervasyon/geri alma detayini disarida birakir; sonraki versiyonda gerekirse genisletilecek.

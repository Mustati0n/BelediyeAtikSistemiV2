# Active Context

## Guncel Odak

Proje hafizasi kuruldu, kullanici ilk teknik kararları onayladi, Git/GitHub akisi tamamlandi ve Faz 1 backend iskeleti kuruldu. Sonraki adim Faz 2 kapsaminda domain modelleri, enumlar, iliskiler ve ilk veritabani semasini kurmak olacak.

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

## Aktif Kararlar

- Yeni domain modeli esas alinacak; eski modeldeki rol bazli kalitim yerine `Personel` + `Rol` yapisi kullanilacak.
- Vatandas ihbari ve kritik konteyner olaylari dogrudan sofore atanmayacak; once `Gorev` havuzuna girecek.
- MVP'de IoT verisi arka plan simulasyon servisiyle uretilecek.
- Backend FastAPI, ORM SQLAlchemy 2.0, veritabani PostgreSQL, personel masaustu ekranlari PySide6 olacak.
- PostgreSQL Docker Compose ile ayaga kaldirilacak.
- Frontend sonradan eklenecek; backend once API sozlesmesi, Pydantic schema'lari ve UI dostu response yapilariyla kurulacak.
- Vatandas portali FastAPI + Jinja2 ile hafif web katmani olarak daha sonraki fazda baslatilacak.
- Bakim kaydi olustugunda muhasebeye bekleyen gider kaydi hemen duser; ancak fiziksel bakim tamamlanmasi muhasebe onayindan ayridir.
- Satis MVP'de dogrudan yapilabilir olacak; stok satis aninda duser, gelir kaydi muhasebe raporlama/onay akisi icin olusur. Stok rezervasyon/geri alma detayi simdilik eklenmeyecek.
- Vatandas fotograf yukleme opsiyonel olacak.
- Sofor ekraninda ilk MVP gorev listesi + koordinat ile ilerleyebilir; harita entegrasyonu sonraki UI fazina yazildi.

## Dikkat Edilecek Noktalar

- Memory Bank her yeni gorevin basinda tamamen okunmali.
- Rapor disindaki kod uygulanmadan once veri modeli ve akislardaki belirsizlikler netlestirilmeli.
- API endpoint'leri markdown raporundaki UI ekranlarina gore ayrilmali; frontend sonra gelse de ekranlarin ihtiyac duyacagi liste, filtre, detay ve aksiyon cevaplari bastan dusunulmeli.
- Tesis/stok/satis sequence diyagraminin PlantUML kodu raporda gorunmuyor; gorselden yeniden yazilmasi gerekebilir.

## Sonraki Adim

Faz 2'ye gecilecek: enumlar, SQLAlchemy domain modelleri, foreign key iliskileri, nullability kararları, ilk Alembic migration ve model testleri.

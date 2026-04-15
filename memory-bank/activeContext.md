# Active Context

## Guncel Odak

Proje hafizasi kuruldu, kullanici ilk teknik kararları onayladi ve yerel Git deposu baslatildi. Sonraki adim Faz 1 kapsaminda backend/API, veritabani, Docker Compose ve test altyapisini kurmak olacak. Frontend ve PySide6 ekranlari daha sonra eklenecek; bu nedenle backend kolay entegre edilebilir API sozlesmeleriyle tasarlanacak.

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

Faz 1 devam edecek: ilk Git commit ve push islemi tamamlandiktan sonra FastAPI uygulama yapisi, SQLAlchemy ayarlari, Docker Compose PostgreSQL, Alembic hazirligi ve test altyapisi kurulacak.

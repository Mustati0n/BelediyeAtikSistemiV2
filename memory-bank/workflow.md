# Workflow and Phase Plan

Bu dosya is akisinin ana takip panosudur. Her faz ilerledikce kutular isaretlenecek ve `progress.md` guncellenecek.

## Faz 0 - Kesif, Dogrulama ve Proje Hafizasi

Durum: Tamamlandi

- [x] Raporun kapsam ve modul basliklarini oku.
- [x] Repo baslangic durumunu kontrol et.
- [x] Memory Bank klasorunu olustur.
- [x] Core Memory Bank dosyalarini yaz.
- [x] UML ilk dogrulama notlarini cikar.
- [x] Kullanici ile kritik karar sorularini netlestir.

Teslim: `memory-bank/` dokumantasyonu, UML notlari, faz planı, acik sorular.

## Faz 1 - Proje Iskeleti ve Altyapi

Durum: Tamamlandi

- [x] Python proje yapisini kur.
- [x] Git deposunu baslat.
- [x] Backend klasor yapisini olustur.
- [x] FastAPI uygulama girisini hazirla.
- [x] SQLAlchemy 2.0 ve veritabani oturum altyapisini kur.
- [x] Docker Compose ile PostgreSQL servis tanimini ekle.
- [x] Alembic migrasyon altyapisini kur.
- [x] Test altyapisini kur.
- [x] Ortam degiskenleri ve konfig yapisini ekle.
- [x] API-first sozlesme yapisini kur: request/response schema'lari, servis katmani ve UI dostu endpoint ayrimi.

Teslim: Calisan bos API, health endpoint, test komutu, migrasyon altyapisi.

## Faz 2 - Domain Modeli ve Veritabani

Durum: Tamamlandi

- [x] Enumlari tanimla.
- [x] Rol ve Personel modelini yaz.
- [x] Bolge, Konteyner, Ihbar ve Gorev modelini yaz.
- [x] Arac ve BakimKaydi modelini yaz.
- [x] MaasOdeme, GiderKaydi, GelirKaydi modelini yaz.
- [x] TesisTeslim, Stok, StokHareketi ve Satis modelini yaz.
- [x] IslemLog ve SistemParametresi modelini yaz.
- [x] Iliskileri, benzersizlikleri ve nullable kurallarini netlestir.
- [x] Ilk migrasyonu uret ve uygula.

Teslim: Veritabani semasi, migrasyon, model testleri.

## Faz 3 - Auth, RBAC ve Audit

Durum: Tamamlandi

- [x] Sifre hashleme altyapisini ekle.
- [x] JWT login endpoint'ini yaz.
- [x] Rol bazli endpoint korumasini kur.
- [x] Seed roller ve demo personeller ekle.
- [x] Audit log servis katmanini ekle.
- [x] Kritik islemler icin log yazma desenini yerlestir.

Teslim: Rol bazli login, korunmus endpoint ornegi, audit log kaydi.

## Faz 4 - Operasyon ve Gorev Havuzu

Durum: Tamamlandi

- [x] Vatandas ihbari API'sini yaz.
- [x] Ihbardan gorev olusturma kuralini ekle.
- [x] Konteyner doluluk guncelleme servisini yaz.
- [x] Kritik konteynerden gorev olusturma kuralini ekle.
- [x] Ayni konteyner icin tekrar acik gorev olusmasini engelle.
- [x] Gunluk gorev listesi ve basit rota siralama endpoint'ini yaz.
- [x] Gorev baslatma ve sonuclandirma endpoint'lerini yaz.

Teslim: Ihbar + kritik konteyner -> gorev -> sofor rota -> sonuc akisi.

## Faz 5 - Bakim ve Muhasebe

Durum: Tamamlandi

- [x] Arac CRUD ve durum yonetimini yaz.
- [x] Bakim kaydi olusturma endpoint'ini yaz.
- [x] Bakimdan bekleyen gider kaydi uret.
- [x] Muhasebe gider onay/red endpoint'lerini yaz.
- [x] Maas hesaplama, tekli odeme ve avans endpoint'lerini yaz.
- [x] Toplu maas odemesi icin ayin 15'i kuralini ekle.
- [x] Kar/zarar raporu icin gelir-gider ozetini yaz.

Teslim: Bakim-gider onayi, maas odeme, finans raporu.

## Faz 6 - Tesis, Stok ve Satis

Durum: Siradaki

- [ ] Sofor tesise atik teslim endpoint'ini yaz.
- [ ] Operator teslim alma akisini yaz.
- [ ] Ayristirma ve stok hareketi akisini yaz.
- [ ] Stok goruntuleme endpoint'lerini yaz.
- [ ] Satis kaydi olustur ve stoktan dus.
- [ ] Satistan bekleyen gelir kaydi uret.
- [ ] Muhasebe gelir onay/red endpoint'lerini yaz.

Teslim: Teslim -> ayristirma -> stok -> satis -> gelir onayi akisi.

## Faz 7 - Arayuzler

Durum: Bekliyor

- [ ] Vatandas ihbar portalini Jinja2 ile yap.
- [ ] Login ve rol yonlendirme ekranlarini yap.
- [ ] Yonetici dashboard ve tanim ekranlarini yap.
- [ ] Sofor operasyon ekranlarini yap.
- [ ] Sofor ekranina ilk MVP'de gorev listesi + koordinat gosterimini ekle.
- [ ] Sofor harita entegrasyonunu sonraki UI iterasyonuna ayir ve teknik secimi netlestir.
- [ ] Bakim teknisyeni ekranlarini yap.
- [ ] Muhasebe ekranlarini yap.
- [ ] Geri donusum operatoru ekranlarini yap.

Teslim: Rol bazli kullanilabilir MVP arayuzleri.

## Faz 8 - Entegrasyon, Test ve Demo

Durum: Bekliyor

- [ ] Uctan uca test senaryolarini yaz.
- [ ] Demo seed verilerini tamamla.
- [ ] API dokumantasyonunu kontrol et.
- [ ] UI akislari ile API entegrasyonlarini test et.
- [ ] Bilinen hatalari gider.
- [ ] Kisa kullanim dokumani hazirla.

Teslim: Calisan demo, test raporu, kullanim notlari.

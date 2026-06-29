# Desktop UI

PySide6 masaustu uygulamasi bu klasore alinip backend reposu ile ayni proje icine toplandi.

## Mevcut Durum

- `desktop/app/` altinda login, yonetici, sofor ve bakim ekranlari bulunur.
- Canli backend baglantisi ilk turda su roller icin baglandi:
  - `admin@belediye.local`
  - `sofor@belediye.local`
  - `bakim@belediye.local`
- Su ekranlar gercek API ile konusur:
  - login
  - yonetici `Filo` sayfasi
  - sofor vardiya / gorev / teslim sayfalari
  - bakim arac durum listesi
- Su sayfalar halen mock veri kullanir:
  - dashboard
  - personel
  - konteyner
  - parametre
  - audit log

## Calistirma

Backend ayakta olmali:

```bash
cd /home/mustati0n/code-blocks/BelediyeAtikSistemi
source .venv/bin/activate
python -m uvicorn backend.app.main:app --host 127.0.0.1 --port 8000
```

Masaustu uygulamasi ayri terminalde:

```bash
cd /home/mustati0n/code-blocks/BelediyeAtikSistemi/desktop/app
python main.py
```

Gerekirse API adresi degistirilebilir:

```bash
export BELEDIYE_API_URL=http://127.0.0.1:8000/api/v1
```

## Notlar

- Linux icin `.venv/bin/python` yolu desteklenir.
- Ilk MVP'de sofor ekraninda gorev listesi + koordinat yeterli kabul edildi; harita entegrasyonu sonraki UI iterasyonuna ayrildi.
- Operator ve muhasebe masaustu ekranlari zip'te bulunmadigi icin bu roller icin login sonrasi canli pencere yonlendirmesi henuz yapilmadi.

# Belediye Atik Sistemi Frontend

Bu klasor sadece PySide6 masaustu frontend uygulamasini icerir.
Backend bu paketin icinde degildir; uygulama varsayilan olarak su sunucuya baglanir:

```text
http://77.83.37.48:8000/api/v1
```

## Windows

```bat
calistir.bat
```

## Linux / macOS

```bash
chmod +x calistir.sh
./calistir.sh
```

## Manuel Calistirma

```bash
python -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.txt
python app/main.py
```

Windows PowerShell icin:

```powershell
py -3 -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
python app\main.py
```

## API Adresini Degistirme

Gerekirse calistirmadan once `BELEDIYE_API_URL` degiskenini ver:

```bash
export BELEDIYE_API_URL=http://SUNUCU_IP:8000/api/v1
```

Windows CMD:

```bat
set BELEDIYE_API_URL=http://SUNUCU_IP:8000/api/v1
```

## Demo Hesaplar

- `admin@belediye.local` / `Admin123!`
- `sofor@belediye.local` / `Sofor123!`
- `bakim@belediye.local` / `Bakim123!`

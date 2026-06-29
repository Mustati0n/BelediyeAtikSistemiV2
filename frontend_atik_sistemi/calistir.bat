@echo off
cd /d "%~dp0"

if not exist ".venv" (
  py -3 -m venv .venv
)

call .venv\Scripts\activate.bat
python -m pip install -r requirements.txt

if "%BELEDIYE_API_URL%"=="" set BELEDIYE_API_URL=http://77.83.37.48:8000/api/v1
python app\main.py

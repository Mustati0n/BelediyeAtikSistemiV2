#!/usr/bin/env bash
set -e

cd "$(dirname "$0")"

if [ ! -d ".venv" ]; then
  python3 -m venv .venv
fi

. .venv/bin/activate
python -m pip install -r requirements.txt

export BELEDIYE_API_URL="${BELEDIYE_API_URL:-http://77.83.37.48:8000/api/v1}"
python app/main.py

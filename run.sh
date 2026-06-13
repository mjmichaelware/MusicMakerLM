#!/usr/bin/env bash
set -euo pipefail
[ -f .env ] || cp .env.example .env
pip install -r requirements.txt --quiet
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload

#!/usr/bin/env sh
set -eu
ROOT="$(CDPATH= cd -- "$(dirname "$0")/.." && pwd)"
cd "$ROOT"
if [ ! -d .venv ]; then
  python3 -m venv .venv
  .venv/bin/pip install -r backend/requirements.txt
fi
if [ ! -d frontend/node_modules ]; then
  (cd frontend && npm install)
fi
if [ ! -f .env ]; then
  cp .env.example .env
fi
export PYTHONPATH="$ROOT/backend"
.venv/bin/uvicorn app.main:app --app-dir "$ROOT/backend" --host 0.0.0.0 --port 8000 &
BACK_PID=$!
trap 'kill $BACK_PID' EXIT
cd frontend
npm run dev

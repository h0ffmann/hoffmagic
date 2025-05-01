#!/usr/bin/env bash
# scripts/docker-entrypoint.sh
set -e

echo "Running Alembic migrations..."
# Rely on PATH to find python and use -m
python -m alembic upgrade head

echo "Starting Uvicorn..."
HOST=${HOST:-0.0.0.0}
PORT=${PORT:-8000}
# Rely on PATH to find python and use -m
python -m uvicorn hoffmagic.main:app --host "$HOST" --port "$PORT"

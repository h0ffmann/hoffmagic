#!/usr/bin/env bash
# scripts/docker-entrypoint.sh
set -e

echo "Running Alembic migrations..."
# Use python -m to ensure the module is found via PYTHONPATH
/usr/bin/env python -m alembic upgrade head

echo "Starting Uvicorn..."
HOST=${HOST:-0.0.0.0}
PORT=${PORT:-8000}
# Use python -m for uvicorn too, for consistency and robustness
/usr/bin/env python -m uvicorn hoffmagic.main:app --host "$HOST" --port "$PORT"
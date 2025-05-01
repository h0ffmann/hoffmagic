#!/bin/bash
# scripts/docker-entrypoint.sh

set -e

echo "Waiting for database to be ready..."
# Add a simple wait loop (optional but good practice)

until pg_isready -h db -U hoffmagic; do
    echo >&2 "Postgres is unavailable - sleeping"
    sleep 2
done
echo >&2 "Postgres is up - executing command"

echo "Running Alembic migrations..."
cd /app
# Alembic will now read alembic.ini, which gets DATABASE_URL from the environment
python -m alembic upgrade head

echo "Starting Uvicorn..."
HOST=${HOST:-0.0.0.0}
PORT=${PORT:-8000}
# Ensure PYTHONPATH includes the src directory if needed, although '-e .' install might handle it
# export PYTHONPATH=/app/src:$PYTHONPATH
python -m uvicorn hoffmagic.main:app --host "$HOST" --port "$PORT"
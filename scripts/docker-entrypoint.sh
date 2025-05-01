#!/bin/bash
# scripts/docker-entrypoint.sh

set -e

echo "Waiting for database to be ready..."
# Use pg_isready for a more robust check, include database name
until pg_isready -h db -U hoffmagic -d hoffmagic; do
    echo >&2 "Postgres is unavailable - sleeping"
    sleep 2
done

echo >&2 "Postgres is up - executing command"
echo "Running Alembic migrations..."
# No need to cd if WORKDIR is /app in Dockerfile
python -m alembic upgrade head

echo "Starting Uvicorn..."
HOST=${HOST:-0.0.0.0}
PORT=${PORT:-8000}
# Use exec to replace the shell process with uvicorn
exec python -m uvicorn hoffmagic.main:app --host "$HOST" --port "$PORT"

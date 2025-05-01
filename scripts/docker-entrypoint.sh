#!/usr/bin/env bash
set -e

# PYTHONPATH is implicitly handled by the Nix environment wrapper
# PATH is also handled by the wrapper, but we use absolute paths for clarity

# Apply database migrations using python from PATH
echo "Running Alembic migrations..."
python -m alembic upgrade head

# Start the application using python from PATH
echo "Starting Uvicorn..."
# Use environment variables for host and port if set, otherwise default
HOST=${HOST:-0.0.0.0}
PORT=${PORT:-8000}
exec python -m uvicorn hoffmagic.main:app --host "$HOST" --port "$PORT"

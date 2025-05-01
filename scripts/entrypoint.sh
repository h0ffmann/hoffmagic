#!/bin/sh
set -e

# Ensure the Nix package binaries are in the PATH
export PATH="/app/result/bin:$PATH"
# PYTHONPATH is set in Dockerfile

# Apply database migrations using python -m
echo "Running Alembic migrations..."
python -m alembic upgrade head

# Start the application using python -m
echo "Starting Uvicorn..."
exec python -m uvicorn hoffmagic.main:app --host $HOST --port $PORT

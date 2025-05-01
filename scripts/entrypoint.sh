#!/bin/sh
set -e

# Ensure the Nix package binaries are in the PATH
export PATH="/app/result/bin:$PATH"

# Debug: List files in the expected bin directory
echo "Listing /app/result/bin:"
ls -l /app/result/bin || echo "/app/result/bin not found or empty"

# Apply database migrations using absolute path
echo "Running Alembic migrations..."
/app/result/bin/alembic upgrade head

# Start the application using absolute path
echo "Starting Uvicorn..."
exec /app/result/bin/uvicorn hoffmagic.main:app --host $HOST --port $PORT
exec uvicorn hoffmagic.main:app --host $HOST --port $PORT

#!/usr/bin/env bash
set -e

echo "Docker Entrypoint: Starting hoffmagic..."

# Check if DATABASE_URL is set
if [ -z "$DATABASE_URL" ]; then
  echo "Error: DATABASE_URL environment variable is not set."
  exit 1
fi

# Navigate to the directory containing alembic.ini if needed
# cd /app # Set WorkingDir in flake.nix instead if possible

echo "Running Alembic migrations..."
# Use 'alembic' directly as it's in the path from appRuntimeEnv
# Assuming alembic.ini is in the root copied by 'contents' or WorkingDir is set correctly
alembic upgrade head

echo "Starting Uvicorn..."
# Use 'python' directly, it points to the correct interpreter from hoffmagicApp
# Use environment variables for host/port passed into the container
exec python -m uvicorn hoffmagic.main:app --host "$HOST" --port "$PORT"

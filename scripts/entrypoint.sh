#!/bin/sh
set -e

# PYTHONPATH is implicitly handled by the Nix environment wrapper
# PATH is also handled by the wrapper, but we use absolute paths for clarity

# Apply database migrations using the python from the Nix build result
echo "Running Alembic migrations..."
/app/result/bin/python -m alembic upgrade head

# Start the application using the python from the Nix build result
echo "Starting Uvicorn..."
exec /app/result/bin/python -m uvicorn hoffmagic.main:app --host $HOST --port $PORT

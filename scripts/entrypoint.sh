#!/bin/sh
set -e

# Ensure the Nix package binaries are in the PATH
export PATH="/app/result/bin:$PATH"

# Apply database migrations
alembic upgrade head

# Start the application
exec uvicorn hoffmagic.main:app --host $HOST --port $PORT

#!/bin/sh
set -e

# Apply database migrations
alembic upgrade head

# Start the application
exec uvicorn hoffmagic.main:app --host $HOST --port $PORT

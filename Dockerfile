# ---- Builder Stage ----
FROM python:3.12-slim AS builder

# Set environment variables for build stage
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    # Necessary for pip install with some build backends
    PIP_NO_CACHE_DIR=off \
    PIP_DISABLE_PIP_VERSION_CHECK=on

WORKDIR /app

# Install build-time system dependencies (gcc, etc.) and runtime deps needed for build (libpq-dev)
# Also install git if your setup needs it for fetching dependencies during build
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    libpq-dev \
    && apt-get clean && rm -rf /var/lib/apt/lists/*

# Copy only the files needed for dependency installation first
# Ensure pyproject.toml exists and defines the package correctly
COPY pyproject.toml ./

# Install dependencies into a specific prefix directory
# This layer is cached as long as pyproject.toml doesn't change
# Using '.' installs the package defined in pyproject.toml in editable mode (if -e is used)
# or standard mode. For prefix install, standard mode is better.
RUN pip install --no-cache-dir --prefix="/install" .

# Copy the rest of the application code AFTER dependency installation
# This layer is cached unless the application code changes
COPY . /app/


# ---- Final Stage ----
FROM python:3.12-slim AS final

# Set environment variables for runtime
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    ENV=production \
    DEBUG=false \
    PORT=8000 \
    HOST=0.0.0.0 \
    # Add /install/bin to path if scripts are installed there by dependencies
    PATH=/usr/local/bin:$PATH \
    # Point to installed packages within the prefix
    PYTHONPATH=/usr/local/lib/python3.12/site-packages

WORKDIR /app

# Install *runtime* system dependencies
# We need the client tools (pg_isready) and the runtime library (libpq5)
RUN apt-get update && apt-get install -y --no-install-recommends \
    postgresql-client \
    libpq5 \
    && apt-get clean && rm -rf /var/lib/apt/lists/*

# Copy installed Python packages from the builder stage's prefix
COPY --from=builder /install /usr/local/

# Copy necessary application files from the builder stage
# Be specific to potentially improve caching if only scripts change, etc.
COPY --from=builder /app/src /app/src
COPY --from=builder /app/scripts /app/scripts
COPY --from=builder /app/alembic.ini /app/alembic.ini # Copy alembic.ini if needed at runtime
# Ensure migrations directory is created (if alembic runs at entrypoint)
# This RUN command should ideally be after copying src if migrations are inside src
RUN mkdir -p /app/src/hoffmagic/db/migrations

# Copy entrypoint and make executable
COPY --from=builder /app/scripts/docker-entrypoint.sh /app/docker-entrypoint.sh
RUN chmod +x /app/docker-entrypoint.sh

# Expose port
EXPOSE 8000

# Run the entrypoint script
ENTRYPOINT ["/app/docker-entrypoint.sh"]

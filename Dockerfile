FROM python:3.12-slim AS builder

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1

WORKDIR /app

RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    libpq-dev \
    && apt-get clean && rm -rf /var/lib/apt/lists/*

COPY pyproject.toml README.md ./

COPY src /app/src
RUN pip install --no-cache-dir --prefix="/install" .


FROM python:3.12-slim AS final

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    ENV=production \
    DEBUG=false \
    PORT=8000 \
    HOST=0.0.0.0 \
    PATH=/usr/local/bin:$PATH \
    PYTHONPATH=/usr/local/lib/python3.12/site-packages

WORKDIR /app

RUN apt-get update && apt-get install -y --no-install-recommends \
    postgresql-client \
    libpq5 \
    && apt-get clean && rm -rf /var/lib/apt/lists/*

COPY --from=builder /install /usr/local/

COPY --from=builder /app/src /app/src
COPY --from=builder /app/scripts /app/scripts
COPY --from=builder /app/alembic.ini /app/alembic.ini
RUN mkdir -p /app/src/hoffmagic/db/migrations

COPY --from=builder /app/scripts/docker-entrypoint.sh /app/docker-entrypoint.sh
RUN chmod +x /app/docker-entrypoint.sh

EXPOSE 8000

ENTRYPOINT ["/app/docker-entrypoint.sh"]

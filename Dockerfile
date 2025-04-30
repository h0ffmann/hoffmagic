# Stage 1: Base Image with Python and Nix
FROM nixos/nix:latest AS base

# Install Python, Node.js, and UV using Nix
RUN nix-env -iA nixpkgs.python313 nixpkgs.nodejs nixpkgs.uv || nix-env -iA nixpkgs.python312 nixpkgs.nodejs nixpkgs.uv

# UV is now installed via Nix, no need for pip install uv

# Set up working directory
WORKDIR /app

# Stage 2: Build Stage
FROM base AS builder

# Copy project files
COPY pyproject.toml ./
COPY src ./src
COPY flake.nix ./flake.nix

# Create a virtualenv and install dependencies with UV
RUN uv venv /app/.venv
ENV PATH="/app/.venv/bin:$PATH"
RUN uv pip install -e .

# Install tailwindcss to generate CSS
RUN npm install -g tailwindcss
COPY tailwind.config.js ./
COPY src/hoffmagic/static/css/input.css ./src/hoffmagic/static/css/

# Generate production CSS
RUN tailwindcss -i ./src/hoffmagic/static/css/input.css -o ./src/hoffmagic/static/css/main.css --minify

# Stage 3: Final Image
FROM base AS final

# Copy built application from builder stage
COPY --from=builder /app/.venv /app/.venv
COPY --from=builder /app/src /app/src
COPY --from=builder /app/src/hoffmagic/static/css/main.css /app/src/hoffmagic/static/css/main.css

# Add entrypoint script
COPY scripts/entrypoint.sh /entrypoint.sh
RUN chmod +x /entrypoint.sh

# Set environment path
ENV PATH="/app/.venv/bin:$PATH"
ENV PYTHONPATH="/app:$PYTHONPATH"

# Default environment variables
ENV PORT=8000
ENV HOST="0.0.0.0"
ENV ENV="production"

# Expose ports
EXPOSE 8000

# Set entrypoint
ENTRYPOINT ["/entrypoint.sh"]

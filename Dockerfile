# Stage 1: Base Image with Nix and Flake Support
FROM nixos/nix:latest AS base
# Ensure flakes are enabled (might be default in newer nixos/nix images)
RUN mkdir -p /root/.config/nix && echo "experimental-features = nix-command flakes" >> /root/.config/nix/nix.conf

# Stage 2: Builder Stage - Use Flake to build
FROM base AS builder
WORKDIR /app

# Copy flake files first for caching
COPY flake.nix flake.lock ./

# Copy the rest of the source needed for building
COPY pyproject.toml README.md ./
COPY src ./src
COPY tailwind.config.js ./
# Ensure input CSS is copied
COPY src/hoffmagic/static/css/input.css ./src/hoffmagic/static/css/input.css

# Build CSS using the environment defined in the flake
RUN nix develop .#default --command tailwindcss -i ./src/hoffmagic/static/css/input.css -o ./src/hoffmagic/static/css/main.css --minify

# Build the Python application package using the flake
# This installs dependencies based on propagatedBuildInputs
RUN nix build .#default -o /app/result

# Stage 3: Final Image - Minimal runtime
FROM base AS final
WORKDIR /app

# Install GNU sed for fixing line endings
RUN nix-env -iA nixpkgs.gnused

# Copy the built Python package from the builder stage
COPY --from=builder /app/result /app/result

# Copy the built CSS asset
COPY --from=builder /app/src/hoffmagic/static/css/main.css /app/src/hoffmagic/static/css/main.css

# Copy the runtime content directory
COPY content ./content

# Add entrypoint script
COPY scripts/entrypoint.sh /entrypoint.sh
# Ensure LF line endings (remove potential CRLF from Windows)
RUN sed -i 's/\r$//' /entrypoint.sh
RUN chmod +x /entrypoint.sh
RUN ls -l /entrypoint.sh # Optional: Add temporarily to verify file exists during build

# Set environment path to use executables from the built package
# Adjust python version based on your flake.nix (e.g., python3.12)
ENV PATH="/app/result/bin:$PATH"
ENV PYTHONPATH="/app/result/lib/python3.12/site-packages:$PYTHONPATH"

# Default environment variables (can be overridden by docker-compose)
ENV PORT=8000
ENV HOST="0.0.0.0"
ENV ENV="production"

# Expose port
EXPOSE 8000

# Set entrypoint
ENTRYPOINT ["/entrypoint.sh"]

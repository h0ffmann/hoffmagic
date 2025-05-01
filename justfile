# Justfile for hoffmagic blog development

# Default command
default: run

# --- Environment ---

# Enter the Nix development shell using flakes
nix-shell:
    nix develop

# --- Development ---

# Run the FastAPI development server with reload (inside nix develop)
run:
    uvicorn hoffmagic.main:app --host 0.0.0.0 --port 8000 --reload

# Build Tailwind CSS (inside nix develop)
build-css:
    npx tailwindcss -i ./src/hoffmagic/static/css/input.css -o ./src/hoffmagic/static/css/main.css --minify

# Build the Docker image using Nix Flakes (inside nix develop)
build-docker: build-css # Ensure CSS is built first
    nix build .#dockerImage -o ./result-docker-image && docker load < ./result-docker-image && rm ./result-docker-image

# Run using Docker Compose (assumes image is pre-built with build-docker)
compose-up:
    docker-compose up -d

# Stop Docker Compose
compose-down:
    docker-compose down

# Watch Tailwind CSS for changes (inside nix develop)
tailwind-watch:
    npx tailwindcss -i ./src/hoffmagic/static/css/input.css -o ./src/hoffmagic/static/css/main.css --watch

# --- Quality & Testing (inside nix develop) ---

# Run all linters and formatters
lint: check format mypy

check:
    ruff check . && black --check . && isort --check .

format:
    black . && isort .

mypy:
    mypy src

# Run tests with coverage
test:
    pytest -v --cov=hoffmagic tests/

# Generate test coverage report
coverage: test
    coverage report -m && coverage html

# --- Database ---

# Apply Alembic migrations
db-upgrade:
    alembic upgrade head

# Generate a new Alembic migration script (requires message) (inside nix develop)
db-migrate msg='':
    alembic revision --autogenerate -m "{{msg}}"

# Build *just* the application package (no docker image) (inside nix develop)
build-app:
    nix build .#default -o ./result-app

# --- Utility ---
dump-nix:
    cp flake.nix flake.nix.txt


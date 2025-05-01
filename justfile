# Justfile for hoffmagic blog development

# Default command
default: run

# --- Environment ---

# Enter the Nix development shell using flakes
nix-shell:
    nix develop

# --- Development ---

# Run the FastAPI development server with reload
run:
    uvicorn hoffmagic.main:app --host 0.0.0.0 --port 8000 --reload

# Build and run using Docker Compose
compose-up:
    docker-compose up --build -d

# Stop and remove Docker Compose containers
compose-down:
    docker-compose down

# Build Docker Compose services without starting
compose-build:
    docker-compose build

# Watch Tailwind CSS for changes
tailwind-watch:
    npx tailwindcss -i ./src/hoffmagic/static/css/input.css -o ./src/hoffmagic/static/css/main.css --watch

# --- Quality & Testing ---

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

# Generate a new Alembic migration script (requires message)
db-migrate msg='':
    alembic revision --autogenerate -m "{{msg}}"

dump-nix:
    cp flake.nix flake.nix.txt


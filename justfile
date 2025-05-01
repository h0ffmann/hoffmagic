# Justfile for hoffmagic blog development

set unstable
set dotenv-load

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
    tailwindcss -i ./src/hoffmagic/static/css/input.css -o ./src/hoffmagic/static/css/main.css --minify

# Build the Docker image using the Dockerfile (inside nix develop)
build-docker: build-css # Ensure CSS is built first
    docker build -t hoffmagic:latest .

# Run using Docker Compose (will build image if not present)
dev-up:
    DATABASE_URL=postgresql+psycopg://hoffmagic:hoffmagic@db:5432/hoffmagic docker-compose up --build

# Stop Docker Compose
dev-down:
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

# Find the time since the last file modification in the project (excluding common build/VCS dirs)
[script("bash")]
last:
    echo "Calculating time since last file modification (non-ignored files only)..."
    NOW_TS=$(date +%s)
    git_tracked=$(git ls-files)
    git_untracked=$(git ls-files --others --exclude-standard)
    all_non_ignored_files=$(echo "$git_tracked"; echo "$git_untracked")
    
    LATEST_TS=0
    LATEST_FILE=""
    
    for file in $all_non_ignored_files; do
        if [ -f "$file" ]; then
            # Get file modification timestamp (works on both Linux and macOS)
            file_ts=$(stat -c %Y "$file" 2>/dev/null || stat -f %m "$file" 2>/dev/null)
            
            if [ -n "$file_ts" ] && [ "$file_ts" -gt "$LATEST_TS" ]; then
                LATEST_TS=$file_ts
                LATEST_FILE="$file"
            fi
        fi
    done
    
    # Check if any files were found
    if [ "$LATEST_TS" = "0" ]; then
        echo "No relevant files found."
    else
        # Calculate time difference in seconds
        DIFF_SECONDS=$((NOW_TS - LATEST_TS))
        
        # Format the difference using awk (days, hours, minutes, seconds)
        FORMATTED_TIME=$(echo $DIFF_SECONDS | awk '{
            s=$1;
            if (s < 0) s=0; # Handle potential clock skew issues if latest > now
            d=int(s/86400); s=s%86400;
            h=int(s/3600); s=s%3600;
            m=int(s/60); s=s%60;
            printf "%dd %02dh %02dm %02ds", d, h, m, s
        }')
        
        echo "Last modification was: $FORMATTED_TIME ago"
        echo "          Latest file: $LATEST_FILE"
    fi
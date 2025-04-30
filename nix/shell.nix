{ pkgs ? import <nixpkgs> {} }:

let
  python = pkgs.python312;
  pythonEnv = python.withPackages (ps: with ps; [
    # Runtime dependencies
    fastapi
    uvicorn
    jinja2
    sqlalchemy
    alembic
    pydantic
    psycopg
    python-multipart
    markdown
    pygments
    pillow
    python-frontmatter
    email-validator
    typer
    rich
    
    # Development dependencies
    pytest
    pytest-cov
    black
    isort
    mypy
    ruff
  ]);
in

pkgs.mkShell {
  buildInputs = [
    pythonEnv
    pkgs.nodePackages.tailwindcss
    pkgs.nodePackages.postcss
    pkgs.nodePackages.autoprefixer
    pkgs.postgresql
    pkgs.docker
    pkgs.docker-compose # Keep for local dev
    pkgs.kubectl        # Keep for deployment tasks
    pkgs.repomix        # Added Repomix
  ];

  shellHook = ''
    echo "Entering HoffMagic development environment"
    # Create a Python venv if it doesn't exist
    if [ ! -d ".venv" ]; then
      echo "Creating virtual environment..."
      ${python}/bin/python -m venv .venv
    fi
    
    # Activate the venv
    source .venv/bin/activate
    
    # Install dependencies with UV if available, fallback to pip
    if command -v uv &> /dev/null; then
      echo "Using UV for dependency management"
      uv pip install -e ".[dev]"
    else
      echo "UV not found, using pip"
      pip install -e ".[dev]"
    fi
    
    # Set environment variables
    export DATABASE_URL="postgresql+psycopg://hoffmagic:hoffmagic@localhost:5432/hoffmagic"
    export DEBUG=true
    export SECRET_KEY="dev_secret_key_change_in_production"
    export ALLOWED_HOSTS="localhost,127.0.0.1"
    
    echo "Development environment ready!"
  '';
}

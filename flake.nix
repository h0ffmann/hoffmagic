{
  description = "Development environment for the hoffmagic blog";

  inputs = {
    nixpkgs.url = "github:NixOS/nixpkgs/nixos-unstable";
    flake-utils.url = "github:numtide/flake-utils";
  };

  outputs = { self, nixpkgs, flake-utils }:
    flake-utils.lib.eachDefaultSystem (system:
      let
        pkgs = import nixpkgs { inherit system; };
        python = pkgs.python312; # Match the version used in shell.nix
        pythonEnv = python.withPackages (ps: with ps; [
          # Runtime dependencies (from shell.nix & default.nix)
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
          pydantic-settings # Added from pyproject.toml

          # Development dependencies (from shell.nix)
          pytest
          pytest-cov
          black
          isort
          mypy
          ruff
          hatchling # Build dependency from pyproject.toml
        ]);
      in
      {
        # Development Shell
        devShells.default = pkgs.mkShell {
          buildInputs = [
            pythonEnv
            pkgs.uv # Use uv from nixpkgs
            pkgs.nodePackages.tailwindcss
            pkgs.nodePackages.postcss
            pkgs.nodePackages.autoprefixer
            pkgs.postgresql
            pkgs.docker
            pkgs.docker-compose
            pkgs.kubectl
            pkgs.repomix
            pkgs.just # Add just command
          ];

          shellHook = ''
            echo "Entering hoffmagic flake development environment"
            
            # Check if venv exists, create if not
            if [ ! -d ".venv" ]; then
              echo "Creating virtual environment..."
              ${python}/bin/python -m venv .venv
            fi
            
            # Activate venv
            source .venv/bin/activate
            
            # Install/sync dependencies using uv
            echo "Syncing dependencies with uv..."
            uv pip install -e ".[dev]"
            
            # Set environment variables
            export DATABASE_URL="postgresql+psycopg://hoffmagic:hoffmagic@localhost:5432/hoffmagic"
            export DEBUG=true
            export SECRET_KEY="dev_secret_key_change_in_production"
            export ALLOWED_HOSTS="localhost,127.0.0.1"
            
            echo "Development environment ready!"
            echo "Run 'just run' to start the server."
          '';
        };

        # Default package (optional, builds the python package)
        packages.default = pythonPackages.buildPythonPackage rec {
          pname = "hoffmagic";
          version = "0.1.0"; # Ensure this matches pyproject.toml
          format = "pyproject";

          src = ./.;

          nativeBuildInputs = with pythonPackages; [
            setuptools
            hatchling
          ];

          propagatedBuildInputs = with pythonPackages; [
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
            pydantic-settings
          ];

          # No check phase in flake build by default, can be added if needed
          doCheck = false; 

          meta = with pkgs.lib; {
            description = "A Python-based blog application";
            homepage = "https://github.com/yourusername/hoffmagic"; # Replace with actual URL
            license = licenses.mit;
            maintainers = with maintainers; [ ]; # Add maintainers if desired
          };
        };
      });
}

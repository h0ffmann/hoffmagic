{
  description = "A magical Python project called hoffmagic";

  inputs = {
    # Use a specific nixpkgs revision for reproducibility, or a branch like nixos-unstable
    nixpkgs.url = "github:NixOS/nixpkgs/nixos-unstable";
    flake-utils.url = "github:numtide/flake-utils";
  };

  outputs = { self, nixpkgs, flake-utils }:
    flake-utils.lib.eachDefaultSystem (system:
      let
        # 1. Import nixpkgs for the current system
        pkgs = import nixpkgs { inherit system; };

        # 2. Choose your Python version
        #    Using python312 based on previous configuration
        python = pkgs.python312;

        # 3. Define pythonPackages based on the chosen interpreter
        pythonPackages = python.pkgs;

      in
      {
        # --------------------------------------------------------------------
        # Development Environment (for `nix develop` or `nix shell`)
        # --------------------------------------------------------------------
        devShells.default = pkgs.mkShell {
          # Tools available ONLY in the development shell
          buildInputs = [
            python              # The Python interpreter itself
            pythonPackages.pip  # For managing packages during development (if needed)
            pythonPackages.pytest # For running tests

            pkgs.libpq          # <-- Add PostgreSQL client C library
            # Tools from previous configuration:
            pkgs.uv
            pkgs.nodePackages.tailwindcss
            pkgs.nodePackages.postcss
            pkgs.nodePackages.autoprefixer
            pkgs.postgresql
            pkgs.docker
            pkgs.docker-compose
            pkgs.kubectl
            pkgs.repomix
            pkgs.just
            pythonPackages.black
            pythonPackages.isort
            pythonPackages.mypy
            pythonPackages.ruff
            pythonPackages.alembic # Added for db-migrate/db-upgrade
          ];

          # Environment variables for the shell (from previous configuration)
          shellHook = ''
            echo "Entering hoffmagic dev shell!"
            
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
            # Provide as a JSON array string
            export ALLOWED_HOSTS='["localhost", "127.0.0.1"]'
            
            echo "Development environment ready!"
            echo "Run 'just run' to start the server."
          '';
        };

        # --------------------------------------------------------------------
        # Definining the Package(s) to Build (for `nix build`)
        # --------------------------------------------------------------------
        packages.default = pythonPackages.buildPythonPackage rec {
          pname = "hoffmagic";
          # IMPORTANT: Keep this version in sync with your project's version (e.g., pyproject.toml)
          version = "0.1.0";

          # Source code location (usually the directory containing the flake.nix)
          src = ./.;

          # Dependencies needed to *run* the installed package
          # From previous configuration & pyproject.toml
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

          # Dependencies needed only to *build* or *test* the package
          # Often includes testing frameworks
          nativeCheckInputs = [
            pythonPackages.pytestCheckHook # To run pytest tests during the build
          ];
          
          # Build dependencies
          nativeBuildInputs = with pythonPackages; [
            hatchling # From pyproject.toml
          ];

          # Set to True if your package includes tests that Nix should run
          doCheck = true;

          # Required for pytestCheckHook to find tests if they aren't in the root
          # pythonImportsCheck = [ "hoffmagic" ]; # Check if the main module can be imported

          meta = with pkgs.lib; {
            description = "Hoffmann's magical Python library/application";
            homepage = "https://github.com/your-username/hoffmagic"; # Optional: Replace with actual URL
            license = licenses.mit; # Optional: Replace with your actual license (e.g., licenses.gpl3Only)
            maintainers = with maintainers; [ /* your github username */ ]; # Optional
          };
        };

        # You can define other packages here if needed
        # packages.anotherPackage = ...;

      }
    );
}

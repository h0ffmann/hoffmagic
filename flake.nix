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

        # ---- Define the Hoffmagic Python Package ----
        hoffmagicApp = pythonPackages.buildPythonPackage rec {
          pname = "hoffmagic";
          # IMPORTANT: Keep this version in sync with your project's version (e.g., pyproject.toml)
          version = "0.1.0"; # Assuming 0.1.0 based on pyproject.toml

          # Source code location (usually the directory containing the flake.nix)
          src = ./.;

          # Dependencies needed to *run* the installed package
          # From pyproject.toml dependencies section
          propagatedBuildInputs = with pythonPackages; [
            fastapi
            uvicorn
            jinja2
            sqlalchemy
            alembic
            pydantic
            psycopg # Depends on libpq C library
            python-multipart
            markdown
            pygments
            pillow
            python-frontmatter
            email-validator
            typer
            rich
            pydantic-settings
          ] ++ [
            pkgs.libpq # Add PostgreSQL client C library for psycopg runtime
            # pkgs.postgresql # Keep if needed for CLI tools, but libpq is essential for psycopg
          ];

          # Dependencies needed only to *build* or *test* the package
          nativeCheckInputs = [
            pythonPackages.pytestCheckHook # To run pytest tests during the build
          ];

          # Build dependencies
          nativeBuildInputs = with pythonPackages; [
            hatchling # From pyproject.toml build-system
          ];

          # Specify the build format (PEP 517/pyproject.toml)
          format = "pyproject";

          # Disable tests during Nix build (they can be run separately via `just test`)
          doCheck = false;

          meta = with pkgs.lib; {
            description = "Hoffmann's magical Python library/application";
            homepage = "https://github.com/your-username/hoffmagic"; # Optional: Replace with actual URL
            license = licenses.mit; # Optional: Replace with your actual license (e.g., licenses.gpl3Only)
            maintainers = with maintainers; [ /* your github username */ ]; # Optional
          };
        };

        # ---- Define the Runtime Environment for Docker ----
        # This bundles the app with runtime dependencies like alembic command and bash
        appRuntimeEnv = pkgs.buildEnv {
          name = "hoffmagic-runtime";
          paths = [
            hoffmagicApp        # Our built Python package/app
            pkgs.alembic        # The alembic command-line tool (needed by entrypoint)
            pkgs.bash           # For running the entrypoint script
            # pkgs.coreutils      # Basic utils like 'echo' if needed by entrypoint
            pkgs.libpq          # Ensure runtime libpq is present again for psycopg
          ];
          # Ensure binaries like python, alembic, bash are linked into /bin
          pathsToLink = [ "/bin" ];
        };

      in
      { # <-- Start of outputs for the system

        # --------------------------------------------------------------------
        # Development Environment (for `nix develop` or `nix shell`)
        # --------------------------------------------------------------------
        devShells.default = pkgs.mkShell {
          # Tools available ONLY in the development shell
          buildInputs = [
            python              # The Python interpreter itself
            pythonPackages.pip  # For managing packages during development (if needed)
            pythonPackages.pytest # For running tests
            pythonPackages.psycopg # Ensure psycopg is available in shell env

            pkgs.libpq          # <-- Add PostgreSQL client C library
            # Tools from previous configuration:
            pkgs.uv
            pkgs.nodePackages.tailwindcss
            pkgs.nodePackages.postcss
            pkgs.nodePackages.autoprefixer
            pkgs.postgresql     # Re-added, maybe needed alongside libpq for path reasons
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
            
            # Force recreate virtual environment for clean state
            if [ -d ".venv" ]; then
              echo "Removing existing virtual environment..."
              rm -rf .venv
            fi
            echo "Creating virtual environment..."
            ${python}/bin/python -m venv .venv
            
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
        packages.default = hoffmagicApp; # Standard package output, uses the definition from 'let' block

        # You can define other packages here if needed
        # packages.anotherPackage = ...;

        # --------------------------------------------------------
        # ---- Docker Image Definition ----
        # --------------------------------------------------------
        packages.dockerImage = pkgs.dockerTools.buildImage {
          name = "hoffmagic"; # Docker image name (matches docker-compose.yml)
          tag = "latest";     # Docker image tag (matches docker-compose.yml)

          # Copy the runtime environment (app + deps like alembic, bash, libpq) to the root
          copyToRoot = appRuntimeEnv;

          # Copy necessary non-Python source files into the image's /app directory
          contents = [
             ./src/hoffmagic/static                 # Built CSS & other static files
             ./src/hoffmagic/templates              # Jinja templates
             ./alembic.ini                          # Alembic config
             ./src/hoffmagic/db/migrations          # Alembic migration scripts
             ./scripts/docker-entrypoint.sh         # Entrypoint script
             # DO NOT copy ./content here - mount it as a volume in docker-compose.yml
          ];

          # Configure the image
          config = {
            # Use bash from appRuntimeEnv to run the entrypoint script copied via 'contents'
            # Note: The script will be copied to the root of the image by 'contents'
            Cmd = [ ]; # Command is handled by entrypoint
            Entrypoint = [ "${pkgs.bash}/bin/bash" "/docker-entrypoint.sh" ];

            # Default environment variables inside the container
            # These can be overridden by docker-compose.yml environment section
            Env = [
              "ENV=production" # Example: Set environment type
              "DEBUG=false"    # Default to production debug setting
              "PORT=8000"      # Default port (can be overridden)
              "HOST=0.0.0.0"   # Default host (can be overridden)
              # Set DATABASE_URL for docker-compose (adjust if needed)
              "DATABASE_URL=postgresql+psycopg://hoffmagic:hoffmagic@db:5432/hoffmagic"
              "SECRET_KEY=" # Should be set via docker-compose secrets or env_file
              "ALLOWED_HOSTS=[]" # Should be set via docker-compose env_file or similar
              # PATH is automatically handled by copyToRoot of appRuntimeEnv
              # PYTHONPATH is often set automatically by buildPythonPackage wrappers
            ];

            ExposedPorts = { "8000/tcp" = {}; }; # Expose the application port
            WorkingDir = "/app"; # Set a working directory inside the container
          };

          # Create the /app directory and make the entrypoint executable after copying
          runAsRoot = ''
            mkdir -p /app
            chmod +x /docker-entrypoint.sh
          '';
        };
        # -------------------------------------------------------------
        # ---- End of Docker Image Section ----------------------------
        # -------------------------------------------------------------

      } # <-- End of outputs for the system
    );
}

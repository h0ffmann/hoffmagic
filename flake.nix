# flake.nix
{
  description = "A magical Python project called hoffmagic";

  inputs = {
    nixpkgs.url = "github:NixOS/nixpkgs/nixos-unstable";
    flake-utils.url = "github:numtide/flake-utils";
  };

  outputs = { self, nixpkgs, flake-utils }:
    flake-utils.lib.eachDefaultSystem (system:
      let
        pkgs = import nixpkgs { inherit system; };
        python = pkgs.python312;
        pythonPackages = python.pkgs;

        # ---- Define the Hoffmagic Python Package ----
        hoffmagicApp = pythonPackages.buildPythonPackage rec {
          pname = "hoffmagic";
          version = "0.1.0";
          src = ./.;

          # Ensure ALL runtime Python deps are here
          propagatedBuildInputs = with pythonPackages; [
            fastapi
            uvicorn # <<< Keep uvicorn here, needed by the entrypoint later
            jinja2
            sqlalchemy # <<< Ensure sqlalchemy is here
            alembic # <<< Ensure alembic is here
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
          ] ++ [
            pkgs.libpq # Runtime C dependency for psycopg
          ];

          nativeCheckInputs = [ pythonPackages.pytestCheckHook ];
          nativeBuildInputs = with pythonPackages; [ hatchling ];
          buildInputs = [ pkgs.libpq ]; # Build-time C dependency for psycopg

          # Create a proper alembic.ini file in the package
          postInstall = ''
            mkdir -p $out/share/hoffmagic
            cp ${./alembic.ini} $out/share/hoffmagic/alembic.ini
            # If you need to modify it for Docker use, you can do that here:
            substituteInPlace $out/share/hoffmagic/alembic.ini \
              --replace "script_location = /app/migrations" \
              "script_location = /app/src/hoffmagic/db/migrations"
          '';


          format = "pyproject";
          doCheck = false; # Speed up builds, run tests separately

          meta = with pkgs.lib; {
            description = "Hoffmann's magical Python library/application";
            homepage = "https://github.com/your-username/hoffmagic"; # Update if needed
            license = licenses.mit;
          };
        };

        # Create a complete Python environment with all dependencies
        pythonEnv = python.withPackages (ps: with ps; [
          sqlalchemy
          alembic
          uvicorn
          fastapi
          jinja2
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
          # Include hoffmagicApp itself
          hoffmagicApp
          # Add any other direct Python dependencies needed at runtime here
        ]);

        # Create an entrypoint script with absolute paths to binaries
        entrypointScript = pkgs.writeScriptBin "docker-entrypoint.sh" ''
          #!${pkgs.bash}/bin/bash
          set -e
          echo "Running Alembic migrations..."
          cd /app
          ${python}/bin/python -m alembic upgrade head
          echo "Starting Uvicorn..."
          HOST=''${HOST:-0.0.0.0}
          PORT=''${PORT:-8000}
          ${python}/bin/python -m uvicorn hoffmagic.main:app --host "$HOST" --port "$PORT"
        '';

        # ---- Define the Runtime Environment for Docker ----
        # Re-add explicit packages for commands, along with the main app
        appRuntimeEnv = pkgs.buildEnv {
          name = "hoffmagic-runtime";
          paths = [
            pythonEnv  # Use the complete Python environment
            # Bash for the entrypoint
            pkgs.bash
            # Core utilities for commands like 'env'
            pkgs.coreutils # <<< Add coreutils
            # Add our new entrypoint script
            entrypointScript
            # libpq is included via pythonEnv's psycopg dependency
          ];
          # Link the essential directories plus our share directory
          pathsToLink = [ "/bin" "/${python.sitePackages}" "/share" ];
        };

      in
      {
        # <-- Start of outputs for the system

        # --------------------------------------------------------------------
        # Development Environment (for `nix develop` or `nix shell`)
        # --------------------------------------------------------------------
        devShells.default = pkgs.mkShell {
          buildInputs = [
            python
            pythonPackages.pip
            pythonPackages.pytest
            pythonPackages.psycopg
            pkgs.libpq
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
            pythonPackages.alembic # Keep alembic in dev shell for local commands
          ];

          shellHook = ''
            echo "Entering hoffmagic dev shell!"
            if [ -d ".venv" ]; then
              echo "Removing existing virtual environment..."
              rm -rf .venv
            fi
            echo "Creating virtual environment..."
            ${python}/bin/python -m venv .venv
            source .venv/bin/activate
            echo "Syncing dependencies with uv..."
            uv pip install -e ".[dev]"

            # Set environment variables for local dev
            export DATABASE_URL="postgresql+psycopg://hoffmagic:hoffmagic@localhost:5432/hoffmagic"
            export DEBUG=true
            export SECRET_KEY="dev_secret_key_change_in_production"
            export ALLOWED_HOSTS='["localhost", "127.0.0.1"]' # JSON array as string

            echo "Development environment ready!"
            echo "Run 'just run' or 'just compose-up'."
          '';
        };

        # --------------------------------------------------------------------
        # Definining the Package(s) to Build (for `nix build`)
        # --------------------------------------------------------------------
        packages.default = hoffmagicApp; # Standard package output

        # --------------------------------------------------------
        # ---- Docker Image Definition ----
        # --------------------------------------------------------
        # Create a proper entrypoint script using writeShellScriptBin
        entrypointScript = pkgs.writeShellScriptBin "entrypoint" ''
            #!${pkgs.bash}/bin/bash
            set -e

            echo "Working directory: $(pwd)"
            echo "Setting up alembic.ini..."
            cp ${hoffmagicApp}/share/hoffmagic/alembic.ini /app/alembic.ini || echo "Warning: Could not copy alembic.ini"

            echo "Creating migrations directory..."
            mkdir -p /app/src/hoffmagic/db/migrations

            echo "Running Alembic migrations..."
            cd /app
            ${python}/bin/python -m alembic upgrade head || echo "Warning: Alembic migration failed"

            echo "Starting Uvicorn..."
            HOST=''${HOST:-0.0.0.0}
            PORT=''${PORT:-8000}
            ${python}/bin/python -m uvicorn hoffmagic.main:app --host "$HOST" --port "$PORT"
        '';

        packages.dockerImage = pkgs.dockerTools.buildImage {
          name = "hoffmagic";
          tag = "latest";

          # Copy the runtime environment and the entrypoint script to the root of the image
          copyToRoot = pkgs.buildEnv {
            name = "image-root";
            paths = [ appRuntimeEnv entrypointScript ];
          };

          # Configure the image metadata and runtime behavior
          config = {
            # Use the entrypoint script we created
            Entrypoint = [ "/bin/entrypoint" ];
            Cmd = [ ]; # Arguments passed to entrypoint (none needed here)
            Env = [
              # Set defaults for the container environment
              "ENV=production"
              "DEBUG=false"
              "PORT=8000"
              "HOST=0.0.0.0"
              # These should be overridden by docker-compose or k8s typically
              "DATABASE_URL=postgresql+psycopg://hoffmagic:hoffmagic@db:5432/hoffmagic"
              "SECRET_KEY=" # Must be provided at runtime
              "ALLOWED_HOSTS=[]" # Must be provided at runtime
              # Crucial: Tell Python where to find the installed packages from hoffmagicApp
              # appRuntimeEnv points to the merged env, which has sitePackages linked
              "PYTHONPATH=${appRuntimeEnv}/${python.sitePackages}"
              # Explicitly set PATH
              "PATH=/bin:${pythonEnv}/bin:${appRuntimeEnv}/bin"
            ];
            ExposedPorts = { "8000/tcp" = { }; };
            WorkingDir = "/app"; # Set working directory for the application
          };

          # Commands to run as root during image build
          runAsRoot = ''
            # Create the application directory
            mkdir -p /app
            # Create migrations directory needed by alembic
            mkdir -p /app/src/hoffmagic/db
            mkdir -p /app/migrations
            touch /app/alembic.ini.placeholder
          '';
        };
        # -------------------------------------------------------------
        # ---- End of Docker Image Section ----------------------------
        # -------------------------------------------------------------

      } # <-- End of outputs for the system
    );
}

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

          format = "pyproject";
          doCheck = false; # Speed up builds, run tests separately

          meta = with pkgs.lib; {
            description = "Hoffmann's magical Python library/application";
            homepage = "https://github.com/your-username/hoffmagic"; # Update if needed
            license = licenses.mit;
          };
        };

        # ---- Define the Runtime Environment for Docker ----
        # Re-add explicit packages for commands, along with the main app
        appRuntimeEnv = pkgs.buildEnv {
          name = "hoffmagic-runtime";
          paths = [
            # Explicitly add Python packages whose commands are needed directly
            pythonPackages.alembic
            pythonPackages.uvicorn
            # The main app package, bringing its Python deps (sqlalchemy, fastapi, etc.)
            hoffmagicApp
            # Bash for the entrypoint
            pkgs.bash
            # Core utilities for commands like 'env'
            pkgs.coreutils # <<< Add coreutils
            # libpq should be pulled in by hoffmagicApp dependency
          ];
          # Link the essential directories from the paths into the final env
          pathsToLink = [ "/bin" "/${python.sitePackages}" ];
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
        packages.dockerImage = pkgs.dockerTools.buildImage {
          name = "hoffmagic";
          tag = "latest";

          # Copy the simplified runtime environment to the root of the image.
          # This includes python, bash, and hoffmagicApp + all its Python deps.
          copyToRoot = appRuntimeEnv;

          # Configure the image metadata and runtime behavior
          config = {
            # Use the bash interpreter copied from appRuntimeEnv
            Entrypoint = [ "${pkgs.bash}/bin/bash" "/docker-entrypoint.sh" ];
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
              # PATH is automatically constructed by dockerTools based on copyToRoot/appRuntimeEnv
              # It should contain the /bin directory from appRuntimeEnv
            ];
            ExposedPorts = { "8000/tcp" = { }; };
            WorkingDir = "/app"; # Set working directory for the application
          };

          # Commands to run as root during image build
          runAsRoot = ''
            # Create the application directory
            mkdir -p /app
            # Copy the entrypoint script from the host into the image
            cp ${./scripts/docker-entrypoint.sh} /docker-entrypoint.sh
            # Make it executable
            chmod +x /docker-entrypoint.sh
          '';
        };
        # -------------------------------------------------------------
        # ---- End of Docker Image Section ----------------------------
        # -------------------------------------------------------------

      } # <-- End of outputs for the system
    );
}

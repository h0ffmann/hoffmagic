# hoffmagic blog

a beautiful python-based blog application built with fastapi, jinja2, and tailwindcss.

## Features

- Modern and clean blog interface
- Separate sections for Blog Posts and Essays
- About Me and Contact pages
- Markdown support for content (manual sync/management recommended)
- Fully deployable to Kubernetes or VPS
- Built with Python, UV, Nix
- Mobile-responsive design

## Getting Started

### Prerequisites

- Python 3.12+
- Docker and Docker Compose (for containerized development)
- [Nix](https://nixos.org/) (optional, for reproducible development environment). Ensure [Flakes are enabled](https://nixos.wiki/wiki/Flakes#Enable_flakes).
- PostgreSQL
- [Just](https://github.com/casey/just) (optional, command runner)

### Development

1. Clone the repository:
   ```
   git clone https://github.com/yourusername/hoffmagic.git
   cd hoffmagic
   ```

2. Set up the development environment:
   ```
   # Using Python venv & pip/uv
   python -m venv .venv
   source .venv/bin/activate
   pip install -e ".[dev]"
   
   # OR using Nix Flakes (recommended for Nix users)
   # This command enters a shell with all dependencies ready.
   # It will also create/activate a .venv and install Python packages.
   nix develop 
   # Alternatively, if you have 'just' installed:
   just nix-shell
   ```

3. Start the development server (inside the activated environment):
   ```
   # Using Docker Compose (recommended)
   docker-compose up
   
   # OR locally using Justfile
   just run
   ```

4. Visit http://localhost:8000 in your browser

### Justfile Commands

If you have `just` installed, you can use these commands for common tasks:

| Command         | Description                                                  |
|-----------------|--------------------------------------------------------------|
| `just run`      | Run the FastAPI development server with auto-reload.         |
| `just nix-shell`| Enter the Nix Flake development shell.                       |
| `just compose-up`| Build and run the application using Docker Compose.          |
| `just compose-down`| Stop and remove Docker Compose containers.                 |
| `just compose-build`| Build Docker Compose services without starting.            |
| `just tailwind-watch`| Watch Tailwind CSS for changes and rebuild `main.css`.     |
| `just lint`     | Run all linters and formatters (`check`, `format`, `mypy`).  |
| `just check`    | Run linters (`ruff`, `black --check`, `isort --check`).      |
| `just format`   | Format code using `black` and `isort`.                       |
| `just mypy`     | Run `mypy` for static type checking.                         |
| `just test`     | Run tests with `pytest` and generate coverage data.          |
| `just coverage` | Run tests and display/generate coverage reports.             |
| `just db-upgrade`| Apply Alembic database migrations (`alembic upgrade head`).  |
| `just db-migrate msg='...'` | Generate a new Alembic migration script.         |
| `just repomix-md`| Generate the Repomix combined code file (Markdown).        |
| `just repomix-xml`| Generate the Repomix combined code file (XML).             |


### Deployment

#### To Kubernetes (OVH Cloud)

```
./scripts/deploy_k8s.sh
```

#### To VPS

```
./scripts/deploy_vps.sh
```

## License

MIT

## Author

Your Name - [your.email@example.com](mailto:your.email@example.com)

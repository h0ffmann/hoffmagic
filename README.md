# HoffMagic Blog

![HoffMagic Logo](https://via.placeholder.com/150x50?text=HoffMagic)  
*A beautiful Python-based blog application built with FastAPI, Jinja2, and TailwindCSS*

## Table of Contents
- [Features](#features)
- [Getting Started](#getting-started)
  - [Prerequisites](#prerequisites)
  - [Development](#development)
- [Justfile Commands](#justfile-commands)
- [Deployment](#deployment)
- [Contributing](#contributing)
- [License](#license)
- [TODO](#todo)

## Features

### Core Features
- 🚀 FastAPI backend with async database operations
- ✨ Jinja2 templating with TailwindCSS for beautiful, responsive design
- 📝 Dual content types: Blog Posts and Essays
- 🌍 Multi-language support (English/Portuguese)
- 🔍 Full-text search capabilities
- 🏷️ Tagging system for content organization

### Technical Highlights
- 🐳 Docker and Kubernetes ready
- 📦 Nix flakes for reproducible development environments
- 🔄 Automatic database migrations with Alembic
- 📊 Built-in analytics and statistics
- ✉️ Contact form with email validation
- 📰 RSS feed support

### Developer Experience
- ⚡ Justfile for common tasks
- ✅ Comprehensive test suite
- 📈 Code coverage reporting
- 🧹 Pre-commit hooks for code quality
- 📜 Detailed logging configuration

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

## Contributing

We welcome contributions! Please follow these steps:

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/your-feature`)
3. Commit your changes (`git commit -am 'Add some feature'`)
4. Push to the branch (`git push origin feature/your-feature`)
5. Open a Pull Request

### Development Guidelines
- Follow PEP 8 style guide
- Write tests for new features
- Document any API changes
- Keep commit messages clear and descriptive

## License

MIT License - See [LICENSE](LICENSE) for details.

## TODO

### High Priority
- 🔍 Auto-tagging system for content
- ⏱️ Reading time estimation (x minutes, y words)
- 📊 Enhanced analytics dashboard

### Medium Priority
- 🔄 Automated content sync from Markdown files
- 📱 Progressive Web App (PWA) support
- 🔐 OAuth authentication options

### Future Ideas
- 🎨 Theme customization system
- 📚 Series/collections for posts
- 🤖 AI-assisted content suggestions

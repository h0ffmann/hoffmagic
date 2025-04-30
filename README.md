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
- Nix (optional, for reproducible development environment)
- PostgreSQL

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
   
   # OR using Nix
   nix-shell
   ```

3. Start the development server:
   ```
   # Using Docker Compose (recommended)
   docker-compose up
   
   # OR locally using Justfile
   just run
   ```

4. Visit http://localhost:8000 in your browser

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

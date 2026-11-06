# Homelab

[![tasks-api CI/CD](https://github.com/Htet-Myark/homelab/actions/workflows/tasks-api.yml/badge.svg)](https://github.com/Htet-Myark/homelab/actions/workflows/tasks-api.yml)

A self-hosted homelab running on **WSL2 (Ubuntu 24.04) + Docker Engine** on a Windows 11 laptop.
All services are defined as code with Docker Compose and version-controlled in Git.
It includes my own **Tasks API** (FastAPI + PostgreSQL), which is tested, built and published
automatically by a **GitHub Actions** CI/CD pipeline.

## Architecture

```
Windows 11 host (8 GB RAM)
└── WSL2: Ubuntu 24.04 (capped at 4 GB via .wslconfig, systemd enabled)
    └── Docker Engine + Compose
        ├── Homepage     :3000  dashboard
        ├── Uptime Kuma  :3001  uptime monitoring
        ├── Portainer    :9443  container management
        ├── Tasks API    :8000  FastAPI app (image from ghcr.io)
        └── tasks-db            PostgreSQL 16 (internal network only)
```

## CI/CD pipeline

```
git push ──► GitHub Actions
             ├── test job:   ruff lint ─► ruff format check ─► pytest
             └── build job:  docker build (multi-stage) ─► push to ghcr.io   (main branch only)
                                                            │
homelab:  docker compose pull tasks-api && docker compose up -d tasks-api ◄┘
```

- Pull requests run lint, tests and the image build, but **don't publish** anything
- Images are tagged `latest` and `sha-<commit>`, so any version can be rolled back to
- The commit SHA is baked into the image and returned by `GET /health`
- Logs in to the registry with the built-in `GITHUB_TOKEN`: no long-lived secrets stored

## Services

| Service | URL | Purpose |
|---|---|---|
| Homepage | http://localhost:3000 | Dashboard linking all services, live container status |
| Uptime Kuma | http://localhost:3001 | HTTP/port health checks and alerting |
| Portainer | https://localhost:9443 | Web UI for Docker management |
| Tasks API | http://localhost:8000/docs | My REST API: create, list, update and delete tasks |

## Tasks API

Code in [`app/`](app). Python 3.12, FastAPI, SQLAlchemy 2, PostgreSQL.

| Method | Path | Description |
|---|---|---|
| GET | `/health` | App + database check (used by Docker healthcheck and Uptime Kuma) |
| GET | `/tasks` | List tasks |
| POST | `/tasks` | Create a task `{"title": "..."}` |
| GET | `/tasks/{id}` | Get one task |
| PATCH | `/tasks/{id}` | Update `title` and/or `done` |
| DELETE | `/tasks/{id}` | Delete a task |

Container design:
- **Multi-stage Dockerfile**: build stage installs dependencies, runtime stage stays slim
- Runs as a **non-root user** (least privilege)
- **Healthcheck** built into the image; Compose waits for Postgres to be healthy before starting the API
- DB password comes from `.env` (git-ignored), never from the repo

Run the tests locally:

```bash
cd app
python3 -m venv .venv && . .venv/bin/activate
pip install -r requirements-dev.txt
ruff check . && pytest -v
```

## Usage

```bash
cp .env.example .env        # first time only: set TASKS_DB_PASSWORD
docker compose up -d        # start everything
docker compose ps           # status
docker compose logs -f tasks-api
docker compose pull && docker compose up -d   # update images (including the latest CI build)
docker compose down         # stop (data is kept in named volumes)
```

## Roadmap

- [x] Phase 1: WSL2, Docker, core services with Compose, Git
- [x] Phase 2: Custom app + CI/CD with GitHub Actions
- [ ] Phase 3: Prometheus + Grafana observability
- [ ] Phase 4: Terraform + AWS deployment
- [ ] Phase 5: Kubernetes (k3s)

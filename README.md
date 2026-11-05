# Homelab

A self-hosted homelab running on **WSL2 (Ubuntu 24.04) + Docker Engine** on a Windows 11 laptop.
All services are defined as code with Docker Compose and version-controlled in Git.

## Architecture

```
Windows 11 host (8 GB RAM)
└── WSL2: Ubuntu 24.04 (capped at 4 GB via .wslconfig, systemd enabled)
    └── Docker Engine + Compose
        ├── Homepage     :3000  dashboard
        ├── Uptime Kuma  :3001  uptime monitoring
        └── Portainer    :9443  container management
```

## Services

| Service | URL | Purpose |
|---|---|---|
| Homepage | http://localhost:3000 | Dashboard linking all services, live container status |
| Uptime Kuma | http://localhost:3001 | HTTP/port health checks and alerting |
| Portainer | https://localhost:9443 | Web UI for Docker management |

## Usage

```bash
docker compose up -d        # start everything
docker compose ps           # status
docker compose logs -f uptime-kuma
docker compose pull && docker compose up -d   # update images
docker compose down         # stop (data is kept in named volumes)
```

## Roadmap

- [x] Phase 1: WSL2, Docker, core services with Compose, Git
- [ ] Phase 2: Custom app + CI/CD with GitHub Actions
- [ ] Phase 3: Prometheus + Grafana observability
- [ ] Phase 4: Terraform + AWS deployment
- [ ] Phase 5: Kubernetes (k3s)

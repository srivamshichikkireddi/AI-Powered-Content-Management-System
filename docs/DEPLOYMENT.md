# Deployment Guide

AICMS runs as a multi-container stack defined in `docker-compose.yml`.

| Container | Role | Host port |
|-----------|------|-----------|
| `aicms_db` | PostgreSQL with pgvector (metadata and embeddings) | 5433 |
| `aicms_redis` | Message broker for background jobs | 6379 |
| `aicms_backend` | FastAPI REST API (auth, RBAC, upload, search) | 8000 |
| `aicms_worker` | Celery worker (extraction, AI enrichment, indexing) | none |
| `aicms_frontend` | React web UI (Vite) | 5173 |
| `aicms_proxy` | Nginx reverse proxy (HTTP / HTTPS) | 8080 / 8443 |

The database and Redis have healthchecks; the backend and worker only start once both are healthy.

## Start
```
copy .env.example .env      (Windows)   |   cp .env.example .env   (Linux/macOS)
docker compose up --build
```

## Verify
```
docker compose ps
curl http://localhost:8000/health
```
UI: http://localhost:5173 or http://localhost:8080 (via proxy). API docs: http://localhost:8000/docs

## Stop and reset
```
docker compose down         # stop, keep data
docker compose down -v      # stop and delete database and upload volumes
```

## Troubleshooting
- **First build is slow:** the AI dependencies are large. Later builds use the Docker cache.
- **Port already in use:** change the host port in `docker-compose.yml` or stop the other process.
- **Backend not starting:** `docker compose logs backend`; the database must report healthy first.
- **Clean rebuild:** `docker compose build --no-cache`.

## Production notes
Replace `SECRET_KEY` and database credentials via environment secrets, serve over HTTPS at the proxy, and disable `--reload` in the backend command.

# Environment Variables

Copy `.env.example` to `.env` before running. The `.env` file is git-ignored and must never be committed.

| Variable | Purpose |
|----------|---------|
| `ENVIRONMENT` | Runtime mode (`development`, `test`, `production`) |
| `LOG_LEVEL` | Logging verbosity (`INFO`, `DEBUG`, ...) |
| `SECRET_KEY` | JWT signing key. **Must be replaced in production** |
| `ALGORITHM` | JWT signing algorithm (`HS256`) |
| `ACCESS_TOKEN_EXPIRE_MINUTES` | Access token lifetime |
| `POSTGRES_USER` / `POSTGRES_PASSWORD` / `POSTGRES_DB` | Database credentials and name |
| `POSTGRES_HOST` / `POSTGRES_PORT` | Database host and port inside the Docker network |
| `DATABASE_URL` | Async SQLAlchemy connection string (`postgresql+asyncpg://...`) |
| `REDIS_HOST` / `REDIS_PORT` / `REDIS_URL` | Redis connection used by Celery |
| `CELERY_BROKER_URL` / `CELERY_RESULT_BACKEND` | Celery broker and result backend |
| `STORAGE_DIR` | Directory where uploaded documents are stored |
| `MAX_UPLOAD_SIZE_BYTES` | Upload size limit (default 20 MB) |
| `EMBEDDING_MODEL_NAME` | Sentence-transformers model (`all-MiniLM-L6-v2`) |
| `EMBEDDER` | `default` uses the real model; `stub` uses a lightweight fake (used in CI and compose) |
| `SIMULATE_MODEL_FAILURE` | Set to `1` to simulate an AI failure for resilience tests |

## Notes
- `docker-compose.yml` sets container-specific values (hostnames `db` and `redis`) directly.
- CI runs with `EMBEDDER=stub` so tests do not download the model.

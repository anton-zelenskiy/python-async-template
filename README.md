# python-async-template

Async Python service template: FastAPI, SQLAlchemy (async), Alembic, Redis, Celery, structlog, Sentry, uv, Docker.

## Stack

- Python 3.14, [uv](https://docs.astral.sh/uv/) package manager
- FastAPI + Uvicorn
- PostgreSQL + SQLAlchemy 2.0 (asyncpg) + Alembic
- Redis (async client + JSON cache decorator)
- Celery worker + beat (Redis broker)
- structlog, optional Sentry
- Ruff (lint + format), pre-commit, pytest

## Quick start

```bash
cp .env.example .env
cp docker-compose.override.example.yml docker-compose.override.yml
docker compose up --build
```

Apply migrations:

```bash
docker compose run --rm web alembic upgrade head
```

Health check: `GET http://localhost:8001/api/v1/health` (port 8001 when using the override example).

## Local development (without Docker)

```bash
uv sync
export $(grep -v '^#' .env | xargs)  # or use direnv
uv run uvicorn app.main:app --reload
```

Install pre-commit hooks (Ruff lint/format + standard file checks; `alembic/versions/` is excluded globally):

```bash
uv sync
uv run pre-commit install
uv run pre-commit run --all-files   # optional: verify before first push
```

## Tests

The production Docker image installs runtime dependencies only. Run tests on the host (or in CI) with dev dependencies:

```bash
uv sync
uv run pytest
```

## Project layout

```
app/
  core/          # config, logging, sentry, redis, retry, cache, run_in_executor, base models
  db/            # async engine + session
  models/        # SQLAlchemy models (import in alembic/env.py)
  tasks/         # Celery tasks + asyncio_runner
  main.py        # FastAPI app
alembic/         # migrations
```

## Celery

- Worker: `celery -A app.celery_app:celery_app worker -l info`
- Example tasks: `app.tasks.example.ping`, `app.tasks.example.ping_redis_async`
- Use `app.tasks.asyncio_runner.run()` inside sync Celery tasks to call async code on a persistent event loop (do not use `asyncio.run()` in workers).

## CI/CD (GitHub Actions)

The workflow [`.github/workflows/master.yaml`](.github/workflows/master.yaml) runs on push to `main` or `master`:

1. **test** — `uv sync --dev` and `pytest`
2. **build_and_push** — build Docker image and push to `ghcr.io/<owner>/<repo>:latest`
3. **deploy** — SSH to the server, pull images, run migrations, `docker compose up -d`

### One-time setup

**GitHub repository**

1. Enable **Actions** and **Packages** (GHCR) for the repo.
2. Under **Settings → Actions → General**, allow workflows to write packages (or use the default `GITHUB_TOKEN` with `packages: write` in the workflow).
3. Add repository **secrets** (Settings → Secrets and variables → Actions):

| Secret | Description |
|--------|-------------|
| `SSH_HOST` | Deploy server hostname or IP |
| `SSH_USER` | SSH user (e.g. `deploy`) |
| `SSH_KEY` | Private key (PEM) for that user |
| `DEPLOY_PATH` | Absolute path to the app directory on the server (contains `docker-compose.yml` and `.env`) |

**Deploy server**

1. Install Docker and Docker Compose v2.
2. Clone the repo (or copy `docker-compose.yml`, `.env`, and override files) into `DEPLOY_PATH`.
3. Create `.env` from `.env.example` with production values (`POSTGRES_*`, `REDIS_*`, `SENTRY_DSN`, etc.).
4. Log in to GHCR on the server so `docker compose pull` can fetch the image:

   ```bash
   echo "$GITHUB_PAT" | docker login ghcr.io -u YOUR_GITHUB_USER --password-stdin
   ```

   Use a [fine-grained or classic PAT](https://github.com/settings/tokens) with `read:packages`. For private repos the deploy user must have access to the package.

5. First deploy manually once:

   ```bash
   cd "$DEPLOY_PATH"
   export GHCR_IMAGE=ghcr.io/OWNER/REPO:latest
   docker compose pull
   docker compose run --rm web alembic upgrade head
   docker compose up -d
   ```

6. Ensure the SSH user can run `docker` (e.g. membership in the `docker` group).

**Image tag**

Compose services `web`, `worker`, and `beat` use `image: ${GHCR_IMAGE:-python-async-template:local}`. CI sets `GHCR_IMAGE` on deploy; locally you build with `docker compose build` and omit `GHCR_IMAGE`.

**Branch protection (recommended)**

Require the `test` job (or full workflow) to pass before merging to `main`/`master`.

### Customize

- Change workflow branches or add tags (e.g. `v*`) in `on.push`.
- Add staging deploy job with a different `DEPLOY_PATH` / secrets.
- Pin image tags instead of `:latest` for reproducible rollbacks.

## New project from template

1. Copy or fork this repo.
2. Rename `PROJECT_NAME` and defaults in `.env`.
3. Add domain models under `app/models/` and register imports in `alembic/env.py`.
4. Add routers under `app/` and include them in `app/main.py`.
5. Configure GitHub secrets and server deploy path as in **CI/CD** above.

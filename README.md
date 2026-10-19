# flyby

A minimal Fly.io deployment sample: a React (Vite) site and a FastAPI backend in one
container, plus Fly Managed Postgres and a **disabled** Tailscale stub.
Intended as a starting template for small Fly.io apps.

```
Dockerfile     node builds the React site → python:3.12-slim runs FastAPI, which serves the API and the site
start.sh       Tailscale stub (commented out) → exec uvicorn
fly.toml       syd, 512MB shared, scale-to-zero, /health check
compose.yaml   local stand-in: the app container + a throwaway Postgres
backend/       FastAPI: /health, /api/v1/{status,notes,ollama/models}, serves the React site
frontend/      React page: runtime status, Postgres notes, Ollama stub
docs/          tailscale.md — how to enable Tailscale safely, and why it's off
```

| Feature | Turned on by | When unset |
|---|---|---|
| Postgres notes | `DATABASE_URL` (set by `fly mpg attach`) | `/api/v1/notes` → 503 |
| Ollama over Tailscale | `OLLAMA_BASE_URL` plus enabling the stub | `/api/v1/ollama/models` → 503 |

`/health` never touches the database, so a Postgres outage doesn't make Fly restart the machine.

## Run locally

```bash
docker compose up --build          # app + Postgres → http://localhost:8080

# or with hot reload:
cd backend && uv run uvicorn flyby.main:app --reload --port 8000   # (STATIC_DIR=../frontend/dist)
cd frontend && npm install && npm run dev                          # proxies /api → :8000

cd backend && uv run --group dev pytest                            # tests
```

## Deploy to Fly.io

```bash
fly auth login
fly apps create flyby-<yourname>   # names are global; put the same name in fly.toml `app`

# Postgres: create a managed cluster, then attach it. Attaching sets the DATABASE_URL secret.
fly mpg create                     # choose region syd to sit next to the app
fly mpg list                       # copy the cluster ID
fly mpg attach <cluster-id> -a flyby-<yourname>

fly deploy
fly scale count 1                  # optional: deploy creates 2 machines by default
fly open
```

Useful afterwards: `fly logs`, `fly status`, `fly ssh console`, `fly mpg connect`.

The app machine stops when idle and wakes on the next request, so the first hit
has a short cold start. Managed Postgres is billed separately and runs all the
time. Check Fly's current pricing, and run `fly mpg destroy` when you're done
experimenting.

The table is created on startup (`CREATE TABLE IF NOT EXISTS`). A real app would
use migrations (e.g. Alembic). Database connections turn off prepared statements
because Fly's managed Postgres sits behind PgBouncer.

## Tailscale

Off by design. A public app on your tailnet is a path to your private devices.
See [docs/tailscale.md](docs/tailscale.md) for how to enable it safely: tagged key,
access rule limited to one port, `--shields-up`, no `--accept-routes`.

## Secrets

Nothing secret lives in this repo. Set real values with `fly secrets set` (or
`fly mpg attach` for the database). `.env` is git-ignored; `.env.example` only
lists the variable names.

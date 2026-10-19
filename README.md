# flyby

A minimal Fly.io deployment sample: a static React (Vite) site served by Caddy,
with an **optional** Tailscale stub. Distilled from the `bind` / `bound` deploys.

```
Dockerfile   node build → caddy:2-alpine (+ tailscale binaries)
start.sh     optional tailscaled → writes /srv/status.json → exec caddy
Caddyfile    /health for Fly checks, SPA fallback, static files
fly.toml     syd, 256MB shared, scale-to-zero, health check
frontend/    Vite + React; reads /status.json to show region/machine/tailscale
```

## Run locally

```bash
# dev server (uses frontend/public/status.json placeholder)
cd frontend && npm install && npm run dev

# the real container
docker build -t flyby .
docker run --rm -p 8080:8080 flyby          # http://localhost:8080
```

## Deploy to Fly.io

```bash
fly auth login
# app names are global — pick your own and update `app` in fly.toml to match
fly apps create flyby-<yourname>
fly deploy
fly open                                    # https://flyby-<yourname>.fly.dev
```

Useful afterwards:

```bash
fly logs                 # startup output from start.sh
fly status               # machines + health checks
fly ssh console          # shell into the machine
fly scale count 1        # (deploy creates 2 machines by default; 1 is plenty here)
```

The machine stops when idle and wakes on the next request (`auto_stop_machines`),
so expect a short cold start on the first hit.

## Tailscale (optional)

Skipped entirely unless `TS_AUTHKEY` is set. With it, the Fly machine joins your
tailnet so the app could reach private services (e.g. an Ollama box at `100.x.y.z`),
as `bind` does.

1. Tailscale admin → Settings → Keys → generate an auth key, **Reusable + Ephemeral**.
   (State is in-memory, so ephemeral keys stop dead nodes piling up in your admin.)
2. `fly secrets set TS_AUTHKEY=tskey-auth-...` (this redeploys)
3. Optional: `fly secrets set TS_HOSTNAME=my-name` (default `flyby-fly`)

The homepage will show `tailscale: connected (100.x.y.z)`. A Tailscale failure
is logged but never stops the site.

This is a stub: nothing in the static site *uses* the tailnet. To actually call a
private service you'd add a backend (or a Caddy `reverse_proxy` to the tailnet IP).
If you want a stable node identity instead of ephemeral, add a volume
(`[[mounts]]` in fly.toml, as in `bind`) and change `--state=mem:` to a file on it.

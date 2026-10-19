#!/bin/sh
# Do NOT use set -e — a Tailscale failure must not stop the website.

echo "=== flyby startup ==="

TS_STATUS="disabled"
TS_IP=""

if [ -n "$TS_AUTHKEY" ]; then
    echo "Starting tailscaled..."
    # In-memory state: pair with an *ephemeral* auth key so stopped machines drop off the tailnet.
    tailscaled --state=mem: --socket=/var/run/tailscale/tailscaled.sock &

    _ts_wait=0
    while [ ! -S /var/run/tailscale/tailscaled.sock ] && [ $_ts_wait -lt 10 ]; do
        sleep 1
        _ts_wait=$((_ts_wait + 1))
    done

    if tailscale up --authkey="$TS_AUTHKEY" --hostname="${TS_HOSTNAME:-flyby-fly}" --accept-routes; then
        TS_STATUS="connected"
        TS_IP="$(tailscale ip -4 2>/dev/null)"
        echo "Tailscale connected: $TS_IP"
    else
        TS_STATUS="error"
        echo "WARNING: Tailscale failed — site still serving"
    fi
else
    echo "TS_AUTHKEY not set — Tailscale disabled"
fi

# Expose runtime info to the frontend (demo of container -> static site)
cat > /srv/status.json <<JSON
{
  "region": "${FLY_REGION:-local}",
  "machine": "${FLY_MACHINE_ID:-local}",
  "app": "${FLY_APP_NAME:-local}",
  "tailscale": { "status": "$TS_STATUS", "ip": "$TS_IP" },
  "started": "$(date -u +%Y-%m-%dT%H:%M:%SZ)"
}
JSON

echo "Starting Caddy on :${PORT:-8080}..."
exec caddy run --config /etc/caddy/Caddyfile --adapter caddyfile

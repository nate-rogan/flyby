#!/bin/sh
# Do NOT use set -e — an optional integration failing must not stop the website.

echo "=== flyby startup ==="

export TS_STATUS="disabled"
export TS_IP=""

# ---------------------------------------------------------------------------
# Tailscale — STUB, intentionally disabled.
# Joining a public app to your tailnet gives it a path to your private devices.
# Read docs/tailscale.md (tagged key + ACL + shields-up) before enabling.
# To enable: uncomment the tailscale COPY lines in the Dockerfile and this block.
# ---------------------------------------------------------------------------
# if [ -n "$TS_AUTHKEY" ]; then
#     tailscaled --state=mem: --socket=/var/run/tailscale/tailscaled.sock &
#     _ts_wait=0
#     while [ ! -S /var/run/tailscale/tailscaled.sock ] && [ $_ts_wait -lt 10 ]; do
#         sleep 1
#         _ts_wait=$((_ts_wait + 1))
#     done
#     # --shields-up: nothing on the tailnet may connect INTO this machine.
#     # No --accept-routes: don't pick up subnet routes to a private LAN.
#     if tailscale up --authkey="$TS_AUTHKEY" --hostname="${TS_HOSTNAME:-flyby-fly}" \
#             --advertise-tags=tag:fly --shields-up; then
#         TS_STATUS="connected"
#         TS_IP="$(tailscale ip -4 2>/dev/null)"
#     else
#         TS_STATUS="error"
#         echo "WARNING: Tailscale failed — site still serving"
#     fi
# fi

echo "Tailscale: $TS_STATUS"
echo "Starting flyby on :${PORT:-8080}..."
exec uvicorn flyby.main:app --host 0.0.0.0 --port "${PORT:-8080}"

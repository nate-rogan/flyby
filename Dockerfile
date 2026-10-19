# ---- Stage 1: build the React static site ----
FROM node:22-alpine AS frontend
WORKDIR /app
COPY frontend/package.json frontend/package-lock.json* ./
RUN npm install
COPY frontend/ ./
RUN npm run build

# ---- Stage 2: Caddy serves the static files (+ optional Tailscale) ----
FROM caddy:2-alpine

# Tailscale binaries copied from the official image (only used if TS_AUTHKEY is set)
COPY --from=docker.io/tailscale/tailscale:stable /usr/local/bin/tailscaled /usr/local/bin/tailscaled
COPY --from=docker.io/tailscale/tailscale:stable /usr/local/bin/tailscale  /usr/local/bin/tailscale
RUN apk add --no-cache ca-certificates iptables ip6tables && \
    mkdir -p /var/run/tailscale /var/lib/tailscale

COPY Caddyfile /etc/caddy/Caddyfile
COPY --from=frontend /app/dist /srv
COPY start.sh /start.sh
RUN chmod +x /start.sh

EXPOSE 8080
CMD ["/start.sh"]

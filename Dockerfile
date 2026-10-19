# ---- Stage 1: build the React static site ----
FROM node:22-alpine AS frontend
WORKDIR /app
COPY frontend/package.json frontend/package-lock.json* ./
RUN npm install
COPY frontend/ ./
RUN npm run build

# ---- Stage 2: FastAPI serves the API + the built site ----
FROM python:3.12-slim
WORKDIR /app

# Tailscale — STUB, disabled. See docs/tailscale.md before uncommenting.
# RUN apt-get update && apt-get install -y --no-install-recommends ca-certificates iptables \
#     && rm -rf /var/lib/apt/lists/* && mkdir -p /var/run/tailscale
# COPY --from=docker.io/tailscale/tailscale:stable /usr/local/bin/tailscaled /usr/local/bin/tailscaled
# COPY --from=docker.io/tailscale/tailscale:stable /usr/local/bin/tailscale  /usr/local/bin/tailscale

COPY backend/pyproject.toml backend/
COPY backend/src/ backend/src/
RUN pip install --no-cache-dir ./backend

COPY --from=frontend /app/dist ./frontend/dist
COPY start.sh .
RUN chmod +x start.sh

ENV STATIC_DIR=/app/frontend/dist
EXPOSE 8080
CMD ["./start.sh"]

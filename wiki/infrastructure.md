# Infrastructure

## Docker Compose

The entire application is orchestrated via `docker-compose.yml` with 6 services on a shared bridge network (`hackathon-network`).

### Services Overview

| Service | Build | Ports | Dependencies | Volumes |
|---------|-------|-------|-------------|---------|
| `db` | postgres:16-alpine | 5432:5432 | — | `postgres_data:/var/lib/postgresql/data` |
| `backend` | `./backend/Dockerfile` | 8000:8000 | db (healthy) | `./backend:/app` |
| `nanobot` | `./nanobot/Dockerfile` | 8001:8000 | — | `./nanobot:/app`, `./mcp:/app/mcp:ro` |
| `client` | `./client-web-react/Dockerfile` | 3000:3000 | backend, nanobot | `./client-web-react:/app`, `/app/node_modules` |
| `caddy` | caddy:2.8-alpine | 80:80, 443:443 | backend, client, nanobot | `./caddy/Caddyfile:/etc/caddy/Caddyfile:ro`, `caddy_data:/data`, `caddy_config:/config` |
| `otel-collector` | otel/opentelemetry-collector-contrib:0.104.0 | 4317:4317, 4318:4318 | — | `./otel-collector/otel-collector.yaml:/etc/otel-collector.yaml:ro` |

### Health Checks

PostgreSQL has a health check:
```yaml
healthcheck:
  test: ["CMD-SHELL", "pg_isready -U ${POSTGRES_USER:-tourstats}"]
  interval: 10s
  timeout: 5s
  retries: 5
```

The backend waits for the database to be healthy before starting.

### Volume Management

**Persistent data:**
- `postgres_data` — PostgreSQL database files
- `caddy_data` — TLS certificates (if HTTPS enabled)
- `caddy_config` — Caddy runtime config

**Development mounts:**
- `./backend:/app` — Hot-reload for backend code
- `./nanobot:/app` — Hot-reload for nanobot code
- `./client-web-react:/app` — Hot-reload for React code

## Caddy Reverse Proxy

Caddy routes incoming requests to the appropriate service based on URL path.

### Caddyfile Configuration

```caddy
localhost {
    handle {
        reverse_proxy /api/* backend:8000
        reverse_proxy /ws/* nanobot:8000
        reverse_proxy /* client:3000
    }
}
```

### Routing Rules

| Path Pattern | Target Service | Purpose |
|-------------|---------------|---------|
| `/api/*` | backend:8000 | REST API endpoints |
| `/ws/*` | nanobot:8000 | WebSocket connections |
| `/*` | client:3000 | Static files (React app) |

**Note:** Currently configured for `localhost`. For production deployment, replace `localhost` with the actual domain name and Caddy will automatically provision TLS certificates via Let's Encrypt.

## OpenTelemetry Collector

The OTel collector receives telemetry data (traces, metrics, logs) from all services and exports them for debugging and monitoring.

### Configuration (`otel-collector.yaml`)

```yaml
receivers:
  otlp:
    protocols:
      grpc:
        endpoint: 0.0.0.0:4317
      http:
        endpoint: 0.0.0.0:4318

processors:
  batch:

exporters:
  debug:
    verbosity: detailed

service:
  pipelines:
    traces:
      receivers: [otlp]
      processors: [batch]
      exporters: [debug]
    metrics:
      receivers: [otlp]
      processors: [batch]
      exporters: [debug]
    logs:
      receivers: [otlp]
      processors: [batch]
      exporters: [debug]
```

### How It Works

1. Services send telemetry to `http://otel-collector:4317` (gRPC) or `:4318` (HTTP)
2. The `batch` processor groups data for efficiency
3. The `debug` exporter logs everything to the collector's stdout

**Currently:** Used for development/debugging. Can be extended with exporters for Jaeger, Prometheus, Grafana, etc.

## Environment Variables

All services load configuration from `.env` file (see `.env.example` for template).

| Variable | Default | Used By | Description |
|----------|---------|---------|-------------|
| `POSTGRES_USER` | tourstats | db | Database user |
| `POSTGRES_PASSWORD` | changeme_password_123 | db | Database password |
| `POSTGRES_DB` | tourstats_db | db | Database name |
| `DATABASE_URL` | postgresql+asyncpg://... | backend | SQLAlchemy connection string |
| `MISTRAL_API_KEY` | — | backend, nanobot | Mistral AI API key (required) |
| `NANOBOT_ACCESS_KEY` | changeme_nanobot_key_123 | nanobot, client | WebSocket authentication |
| `REACT_APP_WS_URL` | ws://localhost:8001/ws | client | WebSocket endpoint |
| `REACT_APP_API_URL` | http://localhost:8000 | client | REST API endpoint |

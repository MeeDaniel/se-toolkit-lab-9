# Deployment

## Prerequisites

| Requirement | Minimum | Recommended |
|-------------|---------|-------------|
| **OS** | Ubuntu 24.04 LTS | Ubuntu 24.04 LTS |
| **RAM** | 2 GB | 4 GB |
| **Disk** | 5 GB | 10 GB |
| **Docker** | 20.10+ | Latest stable |
| **Ports** | 80, 443 | 80, 443 |

## Installation

### 1. Install Docker

```bash
curl -fsSL https://get.docker.com | sudo sh
sudo usermod -aG docker $USER
# Log out and back in for group change to take effect
```

### 2. Clone Repository

```bash
git clone <repository-url>
cd se-toolkit-hackathon
```

### 3. Configure Environment

```bash
cp .env.example .env
```

Edit `.env` and set the following **required** values:

```env
# Mistral AI API key (REQUIRED - get from https://console.mistral.ai/)
MISTRAL_API_KEY=your_actual_api_key_here

# Database password (change from default)
POSTGRES_PASSWORD=your_secure_password

# Nanobot access key (change from default)
NANOBOT_ACCESS_KEY=your_secure_nanobot_key

# Backend secret (change from default)
BACKEND_SECRET=your_secure_backend_secret
```

### 4. Start Services

```bash
docker compose up -d
```

This starts all 6 services:
- `db` — PostgreSQL database
- `backend` — FastAPI REST API
- `nanobot` — WebSocket AI agent
- `client` — React web interface
- `caddy` — Reverse proxy
- `otel-collector` — OpenTelemetry collector

### 5. Verify

```bash
docker compose ps
```

All services should show `Up` or `running` status.

### 6. Access the Application

| Service | URL |
|---------|-----|
| **Web App** | http://localhost |
| **API Docs** | http://localhost/api/docs |
| **Health Check** | http://localhost/api/health |

## First Use

1. Open http://localhost in a browser
2. Register a new account (login ≥ 3 chars, password ≥ 4 chars)
3. Go to the **Chat** tab
4. Type a message describing an excursion, e.g.:
   > "Just finished a tour with 15 people, mostly young adults around 25. They were really energetic and super interested in tech parts, especially robotics and AI."
5. The AI will extract statistics and save them
6. Switch to the **Statistics** tab to view your data

## Management

### View Logs

```bash
# All services
docker compose logs -f

# Specific service
docker compose logs -f backend
docker compose logs -f nanobot
docker compose logs -f client
```

### Restart a Service

```bash
docker compose restart backend
```

### Rebuild After Code Changes

```bash
# Rebuild all
docker compose up -d --build

# Rebuild specific service
docker compose up -d --build nanobot
```

### Stop All Services

```bash
docker compose down
```

### Stop and Remove Volumes (⚠️ Deletes all data)

```bash
docker compose down -v
```

## Troubleshooting

### Service Won't Start

```bash
# Check logs for error details
docker compose logs backend

# Common issues:
# 1. Invalid MISTRAL_API_KEY → Get valid key from console.mistral.ai
# 2. Port already in use → Change port mapping in docker-compose.yml
# 3. Database not ready → Wait for db health check to pass
```

### API Key Errors

If you see `401 - Incorrect API key provided`:
1. Verify `MISTRAL_API_KEY` in `.env` is correct
2. Rebuild backend container: `docker compose up -d --build backend`

### WebSocket Connection Fails

1. Verify `NANOBOT_ACCESS_KEY` matches in `.env` and client config
2. Check nanobot logs: `docker compose logs nanobot`
3. Test WebSocket: open `client-web-react/public/ws-test.html` in browser

### Database Connection Errors

1. Ensure `DATABASE_URL` in `.env` matches PostgreSQL credentials
2. Check db is healthy: `docker compose ps db`
3. Reset database: `docker compose down -v && docker compose up -d`

### Caddy Errors

1. Check Caddy logs: `docker compose logs caddy`
2. Verify Caddyfile syntax (no env var syntax in site blocks)
3. Ensure ports 80/443 are not in use by other services

### Frontend Shows Blank Page

1. Check browser console for errors (F12)
2. Verify React dev server is running: `docker compose ps client`
3. Rebuild: `docker compose up -d --build client`

## Production Deployment

For production deployment:

1. **Change all default secrets** in `.env`
2. **Update Caddyfile** — replace `localhost` with your domain:
   ```caddy
   your-domain.com {
       handle {
           reverse_proxy /api/* backend:8000
           reverse_proxy /ws/* nanobot:8000
           reverse_proxy /* client:3000
       }
   }
   ```
   Caddy will automatically provision TLS certificates via Let's Encrypt.

3. **Build frontend for production:**
   ```bash
   cd client-web-react
   npm run build
   ```
   Then configure Caddy to serve the static `build/` directory instead of proxying to port 3000.

4. **Restrict CORS** in `backend/app/main.py` — replace `allow_origins=["*"]` with your domain.

5. **Set up database backups** — use `pg_dump` on a schedule.

6. **Monitor with OpenTelemetry** — extend `otel-collector.yaml` with production exporters (Prometheus, Jaeger, etc.).

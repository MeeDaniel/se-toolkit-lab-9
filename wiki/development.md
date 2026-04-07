# Development

## Local Development Workflow

### Prerequisites

- Python 3.11+ (for backend/nanobot)
- Node.js 18+ (for frontend)
- Docker and Docker Compose
- Mistral API key

### Project Structure

```
se-toolkit-hackathon/
├── backend/              # FastAPI REST API
│   ├── app/
│   │   ├── main.py       # App entry, routers, CORS
│   │   ├── models.py     # SQLAlchemy models
│   │   ├── schemas.py    # Pydantic schemas
│   │   ├── database.py   # DB connection
│   │   ├── config.py     # Settings
│   │   ├── routes/       # API endpoints
│   │   └── services/     # Business logic (AI service)
│   ├── Dockerfile
│   └── pyproject.toml
├── nanobot/              # WebSocket AI agent
│   ├── app/
│   │   ├── agent.py      # WebSocket server
│   │   ├── config.py
│   │   ├── llm_client.py
│   │   └── mcp_tools.py
│   ├── Dockerfile
│   └── pyproject.toml
├── client-web-react/     # React frontend
│   ├── src/
│   │   ├── App.js
│   │   └── components/
│   ├── Dockerfile
│   └── package.json
├── mcp/                  # MCP tool definitions (empty)
├── caddy/                # Reverse proxy
│   └── Caddyfile
├── otel-collector/       # Observability
│   └── otel-collector.yaml
├── wiki/                 # Project documentation
├── docker-compose.yml
├── .env.example
└── README.md
```

## Backend Development

### Run with Docker (Recommended)

```bash
docker compose up -d backend
docker compose logs -f backend
```

Code changes auto-reload thanks to volume mount `./backend:/app`.

### Run Locally (Without Docker)

```bash
cd backend
pip install -e .
uvicorn app.main:app --reload --port 8000
```

### Run Tests

```bash
cd backend
pytest
```

### Add New Endpoint

1. Create route file in `app/routes/` or add to existing one
2. Define Pydantic schema in `schemas.py`
3. Register router in `main.py`:
   ```python
   app.include_router(new_router, prefix="/api/new", tags=["new"])
   ```

## Nanobot Development

### Run with Docker

```bash
docker compose up -d nanobot
docker compose logs -f nanobot
```

### Test WebSocket

1. Open `client-web-react/public/ws-test.html` in browser
2. Enter WebSocket URL: `ws://localhost:8001/ws?access_key=changeme_nanobot_key_123`
3. Send test messages

## Frontend Development

### Run with Docker

```bash
docker compose up -d client
```

Access at http://localhost:3000 (or via Caddy at http://localhost)

### Run Locally

```bash
cd client-web-react
npm install
npm start
```

### Build for Production

```bash
npm run build
```

Outputs static files to `build/` directory.

### Test WebSocket Integration

```bash
# Start backend + nanobot
docker compose up -d backend nanobot

# Start frontend locally
cd client-web-react
npm start
```

## Git Workflow

This project follows **GitFlow** conventions:

1. Create feature branch from `main`:
   ```bash
   git checkout -b feature/description
   ```

2. Make changes and commit with conventional messages:
   ```bash
   git commit -m "feat: add correlation analysis"
   git commit -m "fix: resolve pagination bug"
   ```

3. Push and create PR:
   ```bash
   git push origin feature/description
   ```

4. Squash merge into `main`

### Commit Message Convention

| Type | Description |
|------|-------------|
| `feat:` | New feature |
| `fix:` | Bug fix |
| `docs:` | Documentation changes |
| `refactor:` | Code restructuring (no behavior change) |
| `chore:` | Maintenance tasks |
| `test:` | Test additions or changes |

## API Development

### Test Endpoints

```bash
# Health check
curl http://localhost:8000/api/health

# Register user
curl -X POST http://localhost:8000/api/users/register \
  -H "Content-Type: application/json" \
  -d '{"login":"testuser","password":"test1234"}'

# List excursions
curl "http://localhost:8000/api/excursions?user_id=1"

# AI extraction
curl -X POST http://localhost:8000/api/excursions/from-message \
  -H "Content-Type: application/json" \
  -d '{"user_id":1,"message":"Tour with 10 people, age 30, loved it"}'
```

### Swagger UI

Interactive API documentation at http://localhost:8000/api/docs

## Database

### Connect to PostgreSQL

```bash
docker compose exec db psql -U tourstats -d tourstats_db
```

### Common Queries

```sql
-- List all users
SELECT * FROM users;

-- Count excursions per user
SELECT user_id, COUNT(*) FROM excursions GROUP BY user_id;

-- View recent excursions
SELECT * FROM excursions ORDER BY created_at DESC LIMIT 10;

-- Average statistics
SELECT
  AVG(number_of_tourists) as avg_tourists,
  AVG(average_age) as avg_age,
  AVG(vivacity_after - vivacity_before) as avg_energy_boost
FROM excursions;
```

### Reset Database

```bash
docker compose down -v
docker compose up -d db
# Database will be recreated on next backend start
```

## Environment Variables

Copy `.env.example` to `.env` and customize. Key variables:

| Variable | Description |
|----------|-------------|
| `MISTRAL_API_KEY` | **Required** — Mistral AI API key |
| `DATABASE_URL` | PostgreSQL connection string |
| `NANOBOT_ACCESS_KEY` | WebSocket authentication key |
| `REACT_APP_WS_URL` | Frontend WebSocket URL |
| `REACT_APP_API_URL` | Frontend API URL |

## Adding Dependencies

### Backend / Nanobot

Add to `pyproject.toml` dependencies, then rebuild:

```bash
docker compose up -d --build backend
```

### Frontend

```bash
cd client-web-react
npm install <package>
docker compose up -d --build client
```

## OpenTelemetry

Services send telemetry to the OTel collector at `http://otel-collector:4317`.

Currently configured for debug output. To extend:

1. Edit `otel-collector/otel-collector.yaml`
2. Add exporters (Prometheus, Jaeger, etc.)
3. Restart collector: `docker compose up -d --build otel-collector`

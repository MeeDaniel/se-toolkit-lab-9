# Tour Statistics Assistant

AI-powered analytics app that helps Innopolis tour guides transform natural language descriptions of excursions into structured statistics and discover correlations between tourist demographics and their interests.

## Demo

<img width="2560" height="1391" alt="image" src="https://github.com/user-attachments/assets/4d64f1dd-0020-490a-bb71-67ed97334ce8" />
<img width="2560" height="1337" alt="image" src="https://github.com/user-attachments/assets/64280912-944e-4408-9ad7-be1fe770f74f" />
<img width="2560" height="1388" alt="image" src="https://github.com/user-attachments/assets/2b196031-e5bf-469d-9d0d-9fa4c37a1bad" />
<img width="2560" height="1381" alt="image" src="https://github.com/user-attachments/assets/c1cf5e94-5899-4d25-aabb-d029de85beba" />


## Context

**End Users:** Innopolis tour guides who lead excursions through the university campus and need to track tourist engagement, demographics, and topic preferences.

**Problem Solved:** Tour guides currently have no tool to systematically analyze the relationship between tourist characteristics (age, group size, energy level) and their interests (IT topics, engagement level, vivacity). After each tour, guides would need to manually record data and perform analysis — a tedious process that rarely happens. Without structured data, guides cannot answer questions like *"Do younger tourists engage more with robotics?"* or *"Which of my tours had the highest energy boost?"*

**Solution:** A web application where tour guides simply type natural language messages about completed excursions (e.g., *"Just finished a tour with 15 people, mostly young adults around 25. They were really energetic and super interested in robotics and AI"*). An AI agent (Mistral LLM) automatically extracts structured statistics, stores them in a database, and provides a dashboard with trends, correlations, and insights — all without manual data entry.

## Features

### Implemented (Version 1 & 2)
- ✅ AI-powered text-to-statistics extraction (Mistral LLM)
- ✅ Real-time chat interface with AI assistant (WebSocket-based)
- ✅ Automatic excursion data extraction: tourist count, average age, energy levels, IT interest, topic keywords
- ✅ Statistics dashboard with paginated excursion history
- ✅ Edit and delete excursions (via UI buttons or natural language commands)
- ✅ Correlation analysis between demographic and interest metrics (12 correlation pairs with human-readable interpretations)
- ✅ Natural language queries about excursion data
- ✅ User registration and authentication (bcrypt password hashing)
- ✅ Session persistence across page refreshes
- ✅ REST API with FastAPI backend
- ✅ PostgreSQL database with automatic schema migration
- ✅ Docker Compose orchestration (6 services)
- ✅ Caddy reverse proxy
- ✅ OpenTelemetry collector for observability

### Not Implemented (Future Versions)
- ❌ Export to CSV/PDF
- ❌ Advanced machine learning insights (beyond correlation analysis)
- ❌ Multi-guide team collaboration
- ❌ Mobile application
- ❌ Telegram bot (blocked on university VMs)

## Usage

### For Tour Guides (End Users)

1. **Open the web application** in your browser at the deployed URL
2. **Register an account** with a login name and password
3. **Describe a completed excursion** in the Chat tab using natural language:
   > *"Just finished a tour with 15 people, mostly young adults around 25. They were really energetic and super interested in tech parts, especially robotics and AI. Less interested in the education history part."*
4. **The AI automatically extractss:**
   - Number of tourists: 15
   - Average age: 25
   - Vivacity (energy) before: ~0.6
   - Vivacity (energy) after: ~0.9
   - Interest in IT: ~0.85
   - Keywords: `robotics AI tech`
5. **Switch to the Statistics tab** to view all your excursions in a table, edit or delete entries, and see correlation insights
6. **Ask natural language questions** in the chat, such as *"What's the average interest in IT across all my tours?"*

### For Developers

See the Deployment section below to run the full stack locally.

Additional developer documentation is available in the [wiki](wiki/) directory:

| Document | Content |
|----------|---------|
| [Architecture](wiki/architecture.md) | System overview, service topology, data flow |
| [Backend](wiki/backend.md) | FastAPI API, routes, AI service, database models |
| [Nanobot Agent](wiki/nanobot.md) | WebSocket AI agent, message processing |
| [Frontend](wiki/frontend.md) | React components, state management, API communication |
| [Data Model](wiki/data-model.md) | Database schema, field semantics |
| [API Reference](wiki/api-reference.md) | Complete REST + WebSocket API documentation |
| [Development](wiki/development.md) | Local dev workflow, testing, Git workflow |

## Deployment

### Target OS
Ubuntu 24.04 LTS (same as university VMs)

### Prerequisites
- Docker and Docker Compose
- Git
- Mistral API key (free tier available at [console.mistral.ai](https://console.mistral.ai/))
- At least 2 GB RAM
- Ports 80 and 443 available

### VM Setup

```bash
# Update system
sudo apt update && sudo apt upgrade -y

# Install Docker
curl -fsSL https://get.docker.com | sudo sh
sudo usermod -aG docker $USER
# Log out and back in for group changes to take effect

# Verify installation
docker --version
docker compose version
```

### Step-by-Step Deployment

1. **Clone the repository**
   ```bash
   git clone https://github.com/MeeDaniel/se-toolkit-hackathon.git
   cd se-toolkit-hackathon
   ```

2. **Configure environment variables**
   ```bash
   cp .env.example .env
   ```
   Edit `.env` and set at minimum:
   - `MISTRAL_API_KEY` — your Mistral AI API key
   - `POSTGRES_PASSWORD` — a secure database password
   - `NANOBOT_ACCESS_KEY` — a secure random string for WebSocket auth
   - `BACKEND_SECRET` — a secure random string for internal service auth

3. **Start all services**
   ```bash
   docker compose up -d
   ```
   This launches 6 services:
   - **PostgreSQL** — database
   - **Backend** (FastAPI) — REST API + AI service integration
   - **Nanobot** — WebSocket AI agent
   - **Client** (React) — web interface
   - **Caddy** — reverse proxy
   - **OpenTelemetry Collector** — observability

4. **Verify services are running**
   ```bash
   docker compose ps
   ```
   All services should show `Up` status.

5. **Access the application**
   - Web interface: `http://your-server-ip` (or `http://localhost` locally)
   - API documentation: `http://your-server-ip/api/docs`
   - Health check: `http://your-server-ip/api/health`

6. **View logs**
   ```bash
   docker compose logs -f         # all services
   docker compose logs -f backend  # specific service
   ```

### Troubleshooting

| Issue | Solution |
|-------|----------|
| Service won't start | Check logs: `docker compose logs <service>` |
| Invalid API key error | Verify `MISTRAL_API_KEY` in `.env` is correct |
| Port conflict | Change port mapping in `docker-compose.yml` |
| Database connection error | Ensure db is healthy: `docker compose ps db` |
| WebSocket fails | Check `NANOBOT_ACCESS_KEY` matches in `.env` and client config |

See [wiki/deployment.md](wiki/deployment.md) for detailed troubleshooting.

## Project Structure

```
se-toolkit-hackathon/
├── backend/              # FastAPI REST API + AI service
│   ├── app/
│   │   ├── main.py       # App entry, routers, CORS, DB migration
│   │   ├── models.py     # SQLAlchemy models (User, Excursion)
│   │   ├── schemas.py    # Pydantic request/response schemas
│   │   ├── database.py   # Async database connection
│   │   ├── config.py     # Settings from environment
│   │   ├── routes/       # API endpoints (users, excursions, chat, stats)
│   │   └── services/     # Business logic (Mistral AI integration)
│   ├── Dockerfile
│   └── pyproject.toml
├── nanobot/              # WebSocket AI agent
│   ├── app/
│   │   ├── agent.py      # WebSocket server, message handler
│   │   ├── config.py     # Settings
│   │   ├── llm_client.py # LLM client wrapper
│   │   └── mcp_tools.py  # MCP tool registry
│   ├── Dockerfile
│   └── pyproject.toml
├── client-web-react/     # React web interface
│   ├── src/
│   │   ├── App.js        # Root component (auth, tabs)
│   │   └── components/   # Auth, ChatInterface, StatisticsDashboard
│   ├── Dockerfile
│   └── package.json
├── mcp/                  # MCP tool definitions
├── caddy/                # Reverse proxy
│   └── Caddyfile         # Routing rules
├── otel-collector/       # Observability
│   └── otel-collector.yaml
├── wiki/                 # Extended project documentation
├── docker-compose.yml    # Service orchestration
├── .env.example          # Environment template
└── README.md
```

## Tech Stack

| Component | Technology |
|-----------|-----------|
| Backend | Python, FastAPI, SQLAlchemy (async), PostgreSQL 16 |
| AI/LLM | Mistral AI API (via OpenAI-compatible SDK) |
| Agent | Nanobot (WebSocket-based message processor) |
| Frontend | React 18, WebSocket, CSS |
| Infrastructure | Docker Compose, Caddy 2.8 (reverse proxy) |
| Observability | OpenTelemetry Collector |
| Security | bcrypt password hashing via passlib |

## License

MIT

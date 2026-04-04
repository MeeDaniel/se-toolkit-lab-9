# TourStats

AI-powered statistics app that helps Innopolis tour guides analyze tourist demographics and interests from excursion data.

## Demo

> *[Screenshots will be added after deployment]*

## Context

**End Users:** Innopolis tour guides who lead excursions and need to track tourist engagement and interests.

**Problem Solved:** Tour guides currently lack tools to systematically analyze the correlation between tourist demographics (age, interests, engagement levels) and their preferences. Manual tracking is tedious and insights are hard to extract.

**Solution:** An AI-powered app where tour guides can simply type natural language messages about completed excursions, and the system automatically extracts, structures, and analyzes statistics. The AI helps find correlations between tourist demographics and their interests (e.g., "tourists aged 20-30 were more interested in tech parts than education").

## Features

### Implemented (Version 1)
- ✅ AI-powered text-to-statistics transformation
- ✅ Web-based chat interface (chat simulator)
- ✅ Store and retrieve excursion data
- ✅ Basic statistics dashboard
- ✅ Natural language queries about tourist data
- ✅ Dockerized deployment
- ✅ REST API with FastAPI backend
- ✅ PostgreSQL database

### Not Implemented (Future Versions)
- ❌ Telegram bot integration (blocked on university VMs)
- ❌ Advanced analytics with machine learning
- ❌ Export to CSV/PDF
- ❌ Multi-user support with authentication
- ❌ Real-time collaboration

## Usage

### For Tour Guides (End Users)

1. **Access the web interface** at your deployed URL
2. **Chat with the AI assistant** - describe your completed excursion in natural language
3. **Example input:** "Just finished a tour with 15 people, mostly young adults around 25. They were really energetic and super interested in tech parts, especially robotics and AI. Less interested in the education history part."
4. **The AI will extract:**
   - Number of tourists: 15
   - Average age: 25
   - Vivacity before/after: high
   - Interest in IT: high
   - Keywords: tech parts, robotics, AI
5. **View statistics** - query past excursions, see trends, find correlations
6. **Ask questions** like "What's the average interest in IT across all my tours?" or "Show me excursions with high tourist engagement"

### For Developers

See deployment section below.

## Deployment

### Target OS
Ubuntu 24.04 (LTS)

### Prerequisites
- Docker and Docker Compose
- Git
- Qwen API key (for AI functionality)
- At least 2GB RAM
- Ports 80 and 443 available

### Step-by-Step Deployment

1. **Clone the repository**
   ```bash
   git clone <your-repo-url>
   cd se-toolkit-hackathon
   ```

2. **Configure environment**
   ```bash
   cp .env.example .env
   # Edit .env and add your Qwen API key
   ```

3. **Start all services**
   ```bash
   docker compose up -d
   ```

4. **Verify services are running**
   ```bash
   docker compose ps
   ```

5. **Access the application**
   - Web interface: `http://your-server-ip`
   - API documentation: `http://your-server-ip/api/docs`

6. **View logs**
   ```bash
   docker compose logs -f
   ```

### Required VM Installations

```bash
# Update system
sudo apt update && sudo apt upgrade -y

# Install Docker
curl -fsSL https://get.docker.com | sudo sh
sudo usermod -aG docker $USER

# Install Docker Compose (usually included with Docker)
docker compose version

# Clone and deploy
git clone <your-repo-url>
cd <repo>
docker compose up -d
```

## Tech Stack

- **Backend:** Python, FastAPI, SQLAlchemy, PostgreSQL
- **AI Agent:** Nanobot framework, Qwen API, MCP (Model Context Protocol)
- **Frontend:** React (TypeScript), WebSocket
- **Infrastructure:** Docker Compose, Caddy (reverse proxy)
- **Observability:** OpenTelemetry (basic)

## Project Structure

```
se-toolkit-hackathon/
├── backend/              # FastAPI application
│   ├── app/
│   │   ├── main.py
│   │   ├── models.py
│   │   ├── schemas.py
│   │   ├── database.py
│   │   ├── routes/
│   │   └── services/
│   ├── Dockerfile
│   └── pyproject.toml
├── nanobot/              # AI agent service
│   ├── app/
│   ├── Dockerfile
│   └── pyproject.toml
├── client-web-react/     # Web chat interface
│   ├── src/
│   ├── Dockerfile
│   └── package.json
├── mcp/                  # MCP tool definitions
├── caddy/                # Reverse proxy config
│   └── Caddyfile
├── docker-compose.yml
├── .env.example
└── README.md
```

## Data Model

### Excursion
- `number_of_tourists` (INT) - Total number of tourists
- `average_age` (DOUBLE) - Average age of tourists
- `age_distribution` (DOUBLE) - Standard deviation of ages
- `vivacity_before` (DOUBLE) - Tourist energy level before excursion (0-1)
- `vivacity_after` (DOUBLE) - Tourist energy level after excursion (0-1)
- `interest_in_it` (DOUBLE) - Interest in IT topics (0-1)
- `interests_list` (STRING) - Space-separated keywords of interests

## License

MIT

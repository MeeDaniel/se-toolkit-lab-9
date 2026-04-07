# Architecture

## System Overview

TourStats is a Docker-compose application consisting of 6 interconnected services that transform natural language descriptions of excursions into structured statistics for Innopolis tour guides.

```
┌─────────────────────────────────────────────────────────┐
│                     User (Browser)                       │
│                    Port 80 / 443                         │
└────────────────────────┬────────────────────────────────┘
                         │
                         ▼
              ┌──────────────────────┐
              │       Caddy          │
              │   Reverse Proxy      │
              │     (Port 80)        │
              └──────┬───────┬───────┘
                     │       │
          /api/*     │       │   /*
          /ws/*      │       │
                     ▼       ▼
         ┌──────────────┐  ┌──────────────────┐
         │   Backend     │  │  React Client    │
         │  (FastAPI)    │  │   (Port 3000)    │
         │  (Port 8000)  │  │                  │
         └──────┬───────┘  └──────────────────┘
                │
                │ HTTP
                ▼
         ┌──────────────┐
         │   Nanobot     │
         │  (WebSocket)  │
         │  (Port 8001)  │
         └──────┬───────┘
                │
                ▼
         ┌──────────────┐      ┌──────────────────┐
         │  PostgreSQL   │      │ OpenTelemetry    │
         │  (Port 5432)  │      │ Collector        │
         └──────────────┘      └──────────────────┘
```

## Services

| Service | Technology | Internal Port | External Port | Purpose |
|---------|-----------|---------------|---------------|---------|
| **Backend** | Python/FastAPI | 8000 | 8000 | REST API, database, AI service integration |
| **Nanobot** | Python/websockets | 8000 | 8001 | WebSocket AI agent, message processing |
| **Client** | React | 3000 | 3000 | Web UI (chat + statistics) |
| **Database** | PostgreSQL 16 | 5432 | 5432 | Persistent data storage |
| **Caddy** | Caddy 2.8 | 80/443 | 80/443 | Reverse proxy, routing |
| **otel-collector** | OpenTelemetry | 4317/4318 | 4317/4318 | Observability (traces, metrics, logs) |

## Data Flow

### 1. Excursion Submission (Chat)
```
User types message → React Client → WebSocket → Nanobot Agent
  → HTTP POST → Backend → AI Service (Mistral API)
    → Parse JSON → Save to PostgreSQL → Return confirmation
      → Nanobot → WebSocket → React Client → Display response
```

### 2. Statistics Retrieval
```
User opens Statistics tab → React Client → HTTP GET → Backend
  → Query PostgreSQL → Calculate correlations → Return JSON
    → React Client → Render tables, charts, insights
```

### 3. Authentication Flow
```
User opens app → Auth component → POST /api/users/register or /login
  → Backend hashes password (bcrypt) → Store in PostgreSQL
    → Return user data → React stores in localStorage
      → Subsequent requests include user_id
```

## Technology Stack

| Layer | Technology |
|-------|-----------|
| **Backend Framework** | FastAPI (Python 3.11+) |
| **Database** | PostgreSQL 16 with asyncpg |
| **ORM** | SQLAlchemy (async) |
| **AI/LLM** | Mistral AI API (OpenAI-compatible SDK) |
| **Frontend** | React 18 (JavaScript) |
| **WebSocket** | websockets library |
| **Reverse Proxy** | Caddy 2.8 |
| **Containerization** | Docker Compose |
| **Observability** | OpenTelemetry Collector |
| **Password Hashing** | bcrypt via passlib |

## Network Topology

All services run on a single Docker bridge network (`hackathon-network`). Internal communication uses service names as hostnames (e.g., `http://backend:8000`). External access goes through Caddy reverse proxy which routes:
- `/api/*` → Backend (FastAPI)
- `/ws/*` → Nanobot (WebSocket)
- `/*` → React Client (static files + dev server)

# Backend

## Overview

The backend is a FastAPI application that provides REST API endpoints for user authentication, excursion management, chat integration, and statistics retrieval. It also integrates with the Mistral AI API for natural language processing.

## Structure

```
backend/
├── app/
│   ├── __init__.py
│   ├── main.py              # FastAPI app, lifespan, CORS, routers
│   ├── models.py             # SQLAlchemy ORM models
│   ├── schemas.py            # Pydantic request/response schemas
│   ├── database.py           # Async database connection
│   ├── config.py             # Settings from environment variables
│   ├── routes/
│   │   ├── users.py          # Registration, login endpoints
│   │   ├── excursions.py     # CRUD operations, AI extraction endpoint
│   │   ├── chat.py           # Chat message processing
│   │   └── statistics.py     # Statistics and correlations
│   └── services/
│       └── ai_service.py     # Mistral AI integration
├── Dockerfile
└── pyproject.toml
```

## Database Models

### User
| Field | Type | Description |
|-------|------|-------------|
| `id` | Integer | Primary key, auto-increment |
| `login` | String(100) | Unique login name, indexed |
| `password_hash` | String(255) | bcrypt hashed password (required) |
| `created_at` | DateTime | Account creation timestamp |
| `excursions` | Integer | Total excursion count |

### Excursion
| Field | Type | Description |
|-------|------|-------------|
| `id` | Integer | Primary key, auto-increment |
| `user_id` | Integer | Foreign key to users |
| `number_of_tourists` | Integer | Number of tourists on tour |
| `average_age` | Float | Average tourist age |
| `age_distribution` | Float | Standard deviation of ages (0-20) |
| `vivacity_before` | Float | Energy level before excursion (0-1) |
| `vivacity_after` | Float | Energy level after excursion (0-1) |
| `interest_in_it` | Float | Interest in IT topics (0-1) |
| `interests_list` | Text | Space-separated interest keywords |
| `created_at` | DateTime | Creation timestamp |
| `updated_at` | DateTime | Last update timestamp |
| `raw_message` | Text | Original user message |

## API Endpoints

### Users (`/api/users`)
| Method | Path | Description |
|--------|------|-------------|
| POST | `/api/users/register` | Register new user (login + password) |
| POST | `/api/users/login` | Authenticate user |

### Excursions (`/api/excursions`)
| Method | Path | Description |
|--------|------|-------------|
| GET | `/api/excursions?user_id=X&offset=0&limit=10` | Get paginated excursions |
| GET | `/api/excursions/{id}?user_id=X` | Get single excursion |
| DELETE | `/api/excursions/{id}?user_id=X` | Delete excursion (ownership verified) |
| PUT | `/api/excursions/{id}?user_id=X` | Update excursion fields |
| POST | `/api/excursions` | Bulk save excursions |
| POST | `/api/excursions/from-message` | AI extract + save + respond (single call) |

### Chat (`/api/chat`)
| Method | Path | Description |
|--------|------|-------------|
| POST | `/api/chat/query` | Natural language query about statistics |

### Statistics (`/api/statistics`)
| Method | Path | Description |
|--------|------|-------------|
| GET | `/api/statistics/overview?user_id=X` | Summary statistics |
| GET | `/api/statistics/correlations?user_id=X` | Correlation analysis |

### Health
| Method | Path | Description |
|--------|------|-------------|
| GET | `/api/health` | Health check |
| GET | `/api/docs` | Swagger UI |
| GET | `/` | API info |

## AI Service

The `AIService` class (`ai_service.py`) integrates with Mistral AI via the OpenAI-compatible SDK.

### Key Methods

#### `extract_excursion_data(message)`
Parses natural language text and extracts excursion data. Returns `ExcursionBatch` with 0+ excursions. Only returns results with confidence >= 0.5.

#### `extract_and_respond(message)`
**Primary method used in production.** Single API call that:
1. Extracts excursion data from text
2. Detects update requests ("Change excursion #26...")
3. Detects delete requests ("Delete excursion #25")
4. Generates conversational response

Returns: `(ExcursionBatch, ai_response_text, update_data, delete_data)`

#### `analyze_statistics(query, context)`
Answers natural language questions about excursion data.

### AI Prompt Design

The AI is instructed with strict rules:
- Return empty list `[]` for non-excursion messages
- Convert multi-word keywords to single words/acronyms ("machine learning" → "ML")
- Use confidence threshold to filter unreliable extractions
- Detect update/delete intent from user messages

## Configuration

Environment variables (from `.env`):

| Variable | Description |
|----------|-------------|
| `DATABASE_URL` | PostgreSQL connection string |
| `MISTRAL_API_KEY` | Mistral AI API key |
| `MISTRAL_BASE_URL` | API base URL (https://api.mistral.ai/v1) |
| `MISTRAL_MODEL` | Model name (mistral-small-latest) |
| `NANOBOT_WS_URL` | WebSocket URL for nanobot service |
| `BACKEND_SECRET` | Internal service secret |
| `OTEL_EXPORTER_OTLP_ENDPOINT` | OpenTelemetry collector endpoint |

## Database Migration

The application handles automatic schema migration on startup:
- Renames `telegram_alias` → `login` (legacy column)
- Adds `password_hash` column if missing
- Ensures `login` and `password_hash` are NOT NULL

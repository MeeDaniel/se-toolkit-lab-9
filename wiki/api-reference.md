# API Reference

Complete documentation for the TourStats REST API. Base URL: `http://localhost:8000/api`

**Swagger UI:** Available at `http://localhost:8000/api/docs`

## Authentication

### Register User
```
POST /api/users/register
Content-Type: application/json

{
  "login": "string (min 3 chars)",
  "password": "string (min 4 chars)"
}
```

**Response (200):**
```json
{
  "id": 1,
  "login": "string",
  "created_at": "2024-01-01T00:00:00"
}
```

**Errors:**
- `409` — Login already exists
- `422` — Validation error (too short, missing fields)

### Login
```
POST /api/users/login
Content-Type: application/json

{
  "login": "string",
  "password": "string"
}
```

**Response (200):**
```json
{
  "id": 1,
  "login": "string",
  "created_at": "2024-01-01T00:00:00"
}
```

**Errors:**
- `401` — Invalid login or password (generic message for security)
- `422` — Validation error

---

## Excursions

### List Excursions
```
GET /api/excursions?user_id={int}&offset={int}&limit={int}
```

**Query Parameters:**
| Param | Type | Required | Default | Description |
|-------|------|----------|---------|-------------|
| `user_id` | int | Yes | — | User ID |
| `offset` | int | No | 0 | Pagination offset |
| `limit` | int | No | 10 | Number of results |

**Response (200):**
```json
{
  "excursions": [
    {
      "id": 1,
      "user_id": 1,
      "number_of_tourists": 15,
      "average_age": 25.0,
      "age_distribution": 5.0,
      "vivacity_before": 0.6,
      "vivacity_after": 0.9,
      "interest_in_it": 0.8,
      "interests_list": "robotics AI tech",
      "created_at": "2024-01-01T00:00:00",
      "raw_message": "Just finished a tour..."
    }
  ],
  "total": 25
}
```

### Get Single Excursion
```
GET /api/excursions/{id}?user_id={int}
```

**Response (200):** Excursion object

**Errors:**
- `404` — Excursion not found
- `403` — Not owner of this excursion

### Create Excursions (Bulk)
```
POST /api/excursions
Content-Type: application/json

{
  "user_id": 1,
  "excursions": [
    {
      "number_of_tourists": 15,
      "average_age": 25.0,
      "vivacity_before": 0.6,
      "vivacity_after": 0.9,
      "interest_in_it": 0.8,
      "interests_list": "robotics AI"
    }
  ]
}
```

**Response (201):**
```json
{
  "message": "Excursions saved successfully",
  "count": 1
}
```

### AI Extract + Save + Respond
```
POST /api/excursions/from-message
Content-Type: application/json

{
  "user_id": 1,
  "message": "Just finished a tour with 15 people..."
}
```

This is the **primary endpoint** used by the chat. It:
1. Calls Mistral AI to extract excursion data
2. Detects update/delete intent
3. Saves/updates/deletes in database
4. Generates AI conversational response

**Response (200):**
```json
{
  "excursion_stored": true,
  "excursion_count": 1,
  "excursion_updated": false,
  "excursion_deleted": false,
  "updated_excursion_id": null,
  "delete_message": "",
  "ai_response": "Great tour! I've recorded 15 tourists..."
}
```

### Update Excursion
```
PUT /api/excursions/{id}?user_id={int}
Content-Type: application/json

{
  "number_of_tourists": 20,
  "average_age": 30.0
}
```

Only provided fields are updated. Unspecified fields remain unchanged.

**Response (200):** Updated excursion object

**Errors:**
- `404` — Excursion not found
- `403` — Not owner

### Delete Excursion
```
DELETE /api/excursions/{id}?user_id={int}
```

**Response (200):**
```json
{
  "message": "Excursion deleted successfully"
}
```

**Errors:**
- `404` — Excursion not found
- `403` — Not owner

---

## Chat

### Natural Language Query
```
POST /api/chat/query
Content-Type: application/json

{
  "user_id": 1,
  "query": "What's the average interest in IT across my tours?"
}
```

**Response (200):**
```json
{
  "response": "Based on your 25 excursions, the average IT interest is 0.73..."
}
```

---

## Statistics

### Overview
```
GET /api/statistics/overview?user_id={int}
```

**Response (200):**
```json
{
  "total_excursions": 25,
  "avg_tourists": 14.2,
  "avg_age": 28.5,
  "avg_vivacity_before": 0.55,
  "avg_vivacity_after": 0.82,
  "avg_interest_in_it": 0.73,
  "top_keywords": ["AI", "robotics", "tech", "ML", "datascience"]
}
```

### Correlations
```
GET /api/statistics/correlations?user_id={int}
```

**Response (200):**
```json
{
  "correlations": [
    {
      "pair": "interest_in_it vs vivacity_after",
      "correlation": 0.82,
      "interpretation": "Strong positive: tourists who are more interested in IT tend to be more energized after the tour"
    }
  ],
  "summary": {
    "avg_group_size": 14.2,
    "avg_energy_boost": 0.27,
    "best_tour_id": 12,
    "worst_tour_id": 3
  }
}
```

---

## Health & Info

### Health Check
```
GET /api/health
```

**Response (200):**
```json
{
  "status": "healthy"
}
```

### API Info
```
GET /
```

**Response (200):**
```json
{
  "message": "Hackathon API",
  "docs": "/api/docs",
  "health": "/api/health"
}
```

---

## WebSocket API (Nanobot)

**Endpoint:** `ws://localhost:8001/ws?access_key={key}`

### Authentication
Connect with `access_key` query parameter matching `NANOBOT_ACCESS_KEY` in `.env`.

### Welcome Message (on connect)
```json
{
  "type": "welcome",
  "message": "Connected to Hackathon AI Assistant"
}
```

### Send Chat Message
```json
{
  "type": "chat",
  "message": "Just finished a tour with 15 people..."
}
```

### Receive Response
```json
{
  "type": "chat_response",
  "message": "Great tour! I've recorded...",
  "excursion_stored": true,
  "excursion_updated": false,
  "excursion_deleted": false,
  "delete_message": ""
}
```

### Error Response
```json
{
  "type": "error",
  "message": "Description of the error"
}
```

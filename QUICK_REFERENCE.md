# Quick Reference - TourStats Commands

## Start/Stop Services

```bash
# Start all services
docker compose up -d

# Stop all services
docker compose down

# Restart specific service
docker compose restart backend

# Rebuild and restart after code changes
docker compose build backend && docker compose up -d backend
```

## View Logs

```bash
# All services
docker compose logs -f

# Specific service
docker compose logs -f backend
docker compose logs -f telegram-bot
docker compose logs -f client
docker compose logs -f nanobot

# Last 50 lines
docker compose logs --tail=50 backend
```

## Test API Endpoints

```bash
# Health check
curl http://localhost:8000/api/health

# Create user
curl -X POST http://localhost:8000/api/users/ \
  -H "Content-Type: application/json" \
  -d '{"telegram_alias":"username"}'

# Set password
curl -X POST http://localhost:8000/api/users/set-password \
  -H "Content-Type: application/json" \
  -d '{"telegram_alias":"username","password":"mypassword"}'

# Login
curl -X POST http://localhost:8000/api/users/login \
  -H "Content-Type: application/json" \
  -d '{"telegram_alias":"username","password":"mypassword"}'

# Remove password
curl -X POST http://localhost:8000/api/users/remove-password/username
```

## Access Services

- **Web Frontend:** http://localhost:3000
- **Backend API:** http://localhost:8000
- **API Docs:** http://localhost:8000/api/docs
- **Nanobot WebSocket:** ws://localhost:8001/ws
- **Telegram Bot:** @setoolkitdchernykhhackathonbot

## Database

```bash
# Connect to PostgreSQL
docker compose exec db psql -U tourstats -d tourstats_db

# List users
docker compose exec db psql -U tourstats -d tourstats_db -c "SELECT * FROM users;"

# List excursions
docker compose exec db psql -U tourstats -d tourstats_db -c "SELECT * FROM excursions LIMIT 10;"

# Count excursions by user
docker compose exec db psql -U tourstats -d tourstats_db -c "SELECT user_id, COUNT(*) FROM excursions GROUP BY user_id;"
```

## Troubleshooting

```bash
# Check service status
docker compose ps

# Check if Docker is running
docker info

# Restart Docker Desktop (Windows)
# Task Manager → Services → Docker Desktop → Restart

# Clean restart (removes all data)
docker compose down -v
docker compose up -d

# Rebuild all images
docker compose build
```

## Common Issues

### Backend won't start
```bash
docker compose build backend
docker compose up -d backend
docker compose logs backend
```

### Database connection error
```bash
# Check if DB is healthy
docker compose ps db

# Wait for DB to be ready
docker compose logs db | grep "ready to accept connections"
```

### Telegram bot not responding
```bash
# Check bot logs
docker compose logs telegram-bot

# Verify token in .env file
grep TELEGRAM_BOT_TOKEN .env
```

### Frontend not loading
```bash
# Check client logs
docker compose logs client

# Rebuild client
docker compose build client
docker compose up -d client
```

## Development Workflow

```bash
# 1. Make code changes
# 2. Rebuild affected service
docker compose build backend

# 3. Restart service
docker compose up -d backend

# 4. Check logs
docker compose logs -f backend

# 5. Test changes
curl http://localhost:8000/api/health
```

## Password Security Testing

```bash
# 1. Create new user (no password)
curl -X POST http://localhost:8000/api/users/ \
  -H "Content-Type: application/json" \
  -d '{"telegram_alias":"testuser"}'

# 2. Set password via API
curl -X POST http://localhost:8000/api/users/set-password \
  -H "Content-Type: application/json" \
  -d '{"telegram_alias":"testuser","password":"secure123"}'

# 3. Login with password
curl -X POST http://localhost:8000/api/users/login \
  -H "Content-Type: application/json" \
  -d '{"telegram_alias":"testuser","password":"secure123"}'

# 4. Try wrong password
curl -X POST http://localhost:8000/api/users/login \
  -H "Content-Type: application/json" \
  -d '{"telegram_alias":"testuser","password":"wrong"}'

# 5. Remove password
curl -X POST http://localhost:8000/api/users/remove-password/testuser
```

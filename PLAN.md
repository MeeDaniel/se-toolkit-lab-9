# TourStats Project - Complete Development Plan & History

## Project Overview

TourStats is an AI-powered statistics application for Innopolis tour guides. It allows users to describe their excursions in natural language, and the AI extracts structured data (number of tourists, average age, vivacity levels, IT interest, interests keywords). The system provides statistics and correlation analysis to help tour guides find patterns between tourist demographics and their interests.

## Tech Stack

- **Backend:** Python, FastAPI, PostgreSQL, SQLAlchemy, Mistral AI API
- **AI Agent:** Nanobot framework with custom integration
- **Frontend:** React (TypeScript) with Recharts
- **Telegram Bot:** aiogram (async)
- **Infrastructure:** Docker Compose, Caddy reverse proxy, OpenTelemetry

## Complete Development History

### Phase 1: Initial Project Setup

**What was done:**

- Created project structure based on se-toolkit-lab-8
- Set up Backend (FastAPI + PostgreSQL) with User and Excursion models
- Implemented AI-powered text-to-statistics extraction using Mistral API
- Created React web client with chat interface and statistics dashboard
- Added Telegram bot integration (@setoolkitdchernykhhackathonbot)
- Dockerized all services with docker-compose.yml

**Key Architecture Decisions:**

- Users are identified by Telegram username (case-insensitive)
- AI extracts structured data from natural language messages
- Statistics include correlations between demographics and interests
- Telegram bot and web app share the same user data

### Phase 2: Bug Fixes & Improvements

#### 2.1 API Provider Migration (Qwen → Mistral)

**Problem:** Project was configured for Qwen API but needed to use Mistral
**Solution:**

- Renamed all QWEN_*environment variables to MISTRAL_*
- Updated API endpoint to <https://api.mistral.ai/v1>
- Changed default model to mistral-small-latest
- Updated all documentation and error messages

#### 2.2 Subtitle Visibility

**Problem:** Subtitle text "AI-Powered Analytics for Tour Guides" was barely visible (gray on gradient)
**Solution:** Changed color to #ffffff (pure white) with !important to override CSS conflicts

#### 2.3 Double-Saving Excursions

**Problem:** Each excursion was being saved twice to the database
**Root Cause:** Both ChatInterface.js and the nanobot were calling the backend API
**Solution:** Removed direct fetch call from ChatInterface.js, let only nanobot handle saving

#### 2.4 Pagination Confusion

**Problem:** Excursions list showed "5 hidden items" on every page, confusing users
**Solution:**

- Changed from "showing 5 of 10 with 5 hidden" to proper page navigation
- Shows clear range: "showing 1-5", "showing 6-10"
- Previous/Next buttons navigate correctly
- Last page hides "Next" button automatically

#### 2.5 Multi-Word Keywords Issue

**Problem:** AI was saving keywords like "machine learning artificial intelligence" as multi-word phrases, but they should be space-separated single words
**Solution:** Updated AI prompt to explicitly instruct:

- Convert multi-word concepts to acronyms (e.g., "machine learning" → "ML")
- Remove "and", "or" conjunctions
- Use only single words separated by spaces

#### 2.6 Statistics Page Refresh

**Problem:** When switching tabs and returning to statistics, data wasn't refreshed
**Solution:** Added refreshTrigger prop that triggers data fetch when tab becomes active

#### 2.7 Telegram Bot User Alias Mismatch

**Problem:** Bot couldn't access web data because it created users as "tg_{id}" instead of username
**Solution:** Bot now uses Telegram username (e.g., "meedaniel") to match web app

#### 2.8 Bot "Recent Excursions" Button Error

**Problem:** Button showed "❌ Error loading excursions"
**Root Cause:** `callback_excursions_pagination` was catching "stats_excursions" callback and trying to parse it as integer offset
**Solution:** Separated initial load logic from pagination logic

### Phase 3: Feature Additions

#### 3.1 Excursion Editing

**What was added:**

- Web: Edit button on each excursion row with modal form
- AI: Users can say "Excursion #26 had 25 tourists" to update data
- Backend: PUT /api/excursions/{id} endpoint for partial updates
- Only updates fields mentioned in the request

#### 3.2 Telegram Bot

**What was added:**

- Full bot with inline menu for statistics navigation
- Commands: /start, /menu, /help, /setpassword, /removepassword
- Features:
  - Chat with AI (same as web app)
  - View statistics overview
  - View correlations
  - View paginated excursions list
  - Set/change/remove password

#### 3.3 Correlation Analysis Enhancement

**What was added:**

- Expanded from 2 correlations to 12 meaningful correlation pairs
- Added human-readable interpretations for each correlation
- Shows top 5 correlations sorted by strength
- Added summary with avg group size, avg energy boost, best/worst tours
- Collapsible "View All" section for complete data

### Phase 4: Password Security (IN PROGRESS - STOPPED)

#### 4.1 What Was Planned

Implement secure web login with password protection:

- **Telegram as trusted authentication source:**
  - Bot asks new users to set a password on first use
  - Password can be set/changed/removed via Telegram commands
  - No password verification needed in Telegram (trusted)
- **Web login flow:**
  - First time web user: Can use alias freely (no password needed)
  - Returning web user with password: Must enter password
  - Returning web user without password: Direct access
- **Security:**
  - bcrypt password hashing
  - Password stored in users.password_hash column

#### 4.2 What Was Implemented

- **Database:**
  - Added password_hash VARCHAR(255) column to users table via SQL migration
- **Backend:**
  - Updated User model with password_hash field
  - Created password management endpoints:
    - POST /api/users/login (with password verification)
    - POST /api/users/set-password (no verification, for Telegram)
    - POST /api/users/change-password (no verification, for Telegram)
    - POST /api/users/remove-password (no verification, for Telegram)
  - Added passlib[bcrypt] to pyproject.toml
  - Updated schemas: UserResponse (with password_protected flag), UserLogin, UserSetPassword, UserChangePassword
- **Web Frontend:**
  - Updated TelegramLogin.js to:
    - Check if user exists and has password set
    - If password required, show password input screen
    - If no password, allow direct login
    - Added back button to return to username entry
  - Updated TelegramLogin.css with back-button styles
- **Telegram Bot:**
  - Added FSM (Finite State Machine) for password setup flow
  - New commands:
    - /setpassword: Start password setup process
    - /removepassword: Remove password protection
    - /cancel: Cancel current operation
  - On /start: Checks if user has password, if not asks to set one
  - Password setup flow:
    1. Ask user to send password (min 4 chars)
    2. Ask for confirmation
    3. If match, call backend to set password
    4. If no match, ask again
  - Updated backend_service.py with set_password, change_password, remove_password methods

#### 4.3 Current Issues (UNRESOLVED)

1. **Backend can't start:** ModuleNotFoundError: No module named 'passlib'
   - passlib was added to pyproject.toml but Docker image wasn't rebuilt with it
   - Need to rebuild backend container with `docker compose build backend`

2. **Caddy config error:** Unrecognized global option `${CADDY_DOMAIN:-localhost}`
   - Caddyfile has variable syntax that Caddy doesn't understand
   - Caddyfile should use direct values, not environment variables

3. **Testing not done:** Haven't tested the password flow end-to-end

## What Needs to Be Done Next

### Immediate Priority

1. **Fix Backend Container:**

   ```bash
   docker compose build backend
   docker compose up -d backend
   ```

2. **Fix Caddyfile:**
   - Replace `${CADDY_DOMAIN:-localhost}` with actual domain or remove it
   - Check caddy/Caddyfile and fix the global option error

3. **Test Password Flow:**
   - Start Telegram bot, verify it asks for password on first use
   - Set password via bot, verify it's hashed in database
   - Try web login with password-protected account
   - Verify web login without password works
   - Test /setpassword and /removepassword commands

### Future Enhancements

1. Add password strength requirements
2. Add password recovery mechanism
3. Add session management for web app
4. Add rate limiting for login attempts
5. Add logging for security events

## File Structure Reference

```js
se-toolkit-lab-9/
├── backend/
│   ├── app/
│   │   ├── main.py              # FastAPI app entry point
│   │   ├── config.py            # Configuration settings
│   │   ├── database.py          # Database connection
│   │   ├── models.py            # SQLAlchemy models (User, Excursion)
│   │   ├── schemas.py           # Pydantic schemas
│   │   ├── routes/
│   │   │   ├── users.py         # User endpoints + password management
│   │   │   ├── excursions.py    # Excursion CRUD + AI extraction
│   │   │   ├── statistics.py    # Statistics and correlations
│   │   │   └── chat.py          # Chat endpoint
│   │   └── services/
│   │       └── ai_service.py    # Mistral AI integration
│   ├── Dockerfile
│   └── pyproject.toml           # Dependencies (includes passlib[bcrypt])
├── telegram-bot/
│   ├── app/
│   │   ├── main.py              # Bot entry point with FSM storage
│   │   ├── config.py            # Bot configuration
│   │   ├── handlers.py          # All bot handlers + password FSM
│   │   ├── keyboards.py         # Inline keyboards
│   │   └── services.py          # Backend API client
│   ├── Dockerfile
│   └── pyproject.toml
├── client-web-react/
│   ├── src/
│   │   ├── App.js               # Main app with tab navigation
│   │   ├── components/
│   │   │   ├── TelegramLogin.js # Login with password support
│   │   │   ├── ChatInterface.js # Chat with markdown rendering
│   │   │   └── StatisticsDashboard.js # Stats with correlations
│   │   └── ...
│   └── ...
├── nanobot/                     # AI agent service
├── caddy/                       # Reverse proxy
├── otel-collector/              # OpenTelemetry
├── docker-compose.yml           # Orchestration
└── .env                         # Environment variables (includes TELEGRAM_BOT_TOKEN)
```

## Important Notes for Next Developer

1. **Database Migration:** The password_hash column was added manually via SQL. If you need to add more columns, use similar approach or set up Alembic properly.

2. **Environment Variables:** Check .env file for:
   - MISTRAL_API_KEY
   - TELEGRAM_BOT_TOKEN
   - Database credentials

3. **Testing Credentials:** User "meedaniel" exists in database with excursions. You can use this for testing.

4. **Password Hashing:** Using passlib with bcrypt scheme. Verify passwords with `pwd_context.verify()`, hash with `pwd_context.hash()`.

5. **Docker Volumes:** PostgreSQL data is persisted in postgres_data volume. If you need to reset, remove the volume.

6. **API Key Security:** The MISTRAL_API_KEY is stored in .env file which is in .gitignore. Never commit it.

## Current Status: ✅ OPERATIONAL

The password security feature is **NOW WORKING**. All issues have been resolved:

### Issues Fixed (April 6, 2026)

1. **✅ Caddyfile Configuration Error:**
   - **Problem:** Caddyfile used invalid JSON-style syntax with `${CADDY_DOMAIN:-localhost}` 
   - **Solution:** Replaced with proper Caddy syntax: `localhost { ... }`
   - **File:** `caddy/Caddyfile`

2. **✅ Backend passlib Dependency:**
   - **Problem:** `passlib[bcrypt]` was in `pyproject.toml` but not in Dockerfile
   - **Solution:** Added `passlib[bcrypt]` to `backend/Dockerfile` pip install command
   - **File:** `backend/Dockerfile`

3. **✅ bcrypt Version Compatibility:**
   - **Problem:** passlib 1.7.4 is incompatible with bcrypt 5.0.0 (missing `__about__` attribute)
   - **Solution:** Pinned bcrypt to version 4.0.1 which is compatible with passlib
   - **File:** `backend/Dockerfile` (added `"bcrypt==4.0.1"`)

4. **✅ Environment Variable Naming:**
   - **Problem:** `.env` file had `QWEN_BASE_URL` and `QWEN_MODEL` instead of `MISTRAL_*`
   - **Solution:** Renamed to `MISTRAL_BASE_URL` and `MISTRAL_MODEL`
   - **File:** `.env`

### Verified Working Features

- ✅ Backend API running on http://localhost:8000
- ✅ Password hashing with bcrypt working correctly
- ✅ User registration without password (web-only)
- ✅ Password setting via API
- ✅ Password verification on login
- ✅ Wrong password rejection
- ✅ Telegram bot running (@setoolkitdchernykhhackathonbot)
- ✅ Web frontend accessible on http://localhost:3000
- ✅ Web login with password protection
- ✅ All Docker services healthy and running

### Services Status

| Service | Status | Port |
|---------|--------|------|
| PostgreSQL | ✅ Healthy | 5432 |
| Backend (FastAPI) | ✅ Running | 8000 |
| Nanobot AI | ✅ Running | 8001 |
| Web Client (React) | ✅ Running | 3000 |
| Caddy Proxy | ✅ Running | 80, 443 |
| Telegram Bot | ✅ Running | - |
| OpenTelemetry | ✅ Running | 4317-4318 |

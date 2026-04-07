# Frontend

## Overview

The frontend is a React 18 application that provides a web-based interface for tour guides to chat with the AI assistant and view excursion statistics.

## Structure

```
client-web-react/
├── public/
│   ├── index.html          # HTML template
│   └── ws-test.html        # Standalone WebSocket test page
├── src/
│   ├── App.js              # Main app: auth, tabs, routing
│   ├── App.css             # Global styles
│   ├── components/
│   │   ├── Auth.js         # Registration / Login page
│   │   ├── Auth.css        # Auth page styles
│   │   ├── ChatInterface.js  # Chat with AI assistant
│   │   ├── ChatInterface.css
│   │   ├── StatisticsDashboard.js  # Statistics tables & correlations
│   │   ├── StatisticsDashboard.css
│   │   └── TelegramLogin.js  # (deprecated, replaced by Auth.js)
│   └── index.js            # React entry point
├── Dockerfile
└── package.json
```

## Components

### Auth (`Auth.js`)
**Registration/Login page** shown when no user session exists.
- Toggle between Login and Register modes
- Form validation: login ≥ 3 chars, password ≥ 4 chars, confirm password match
- On success: stores user data in `localStorage` key `hackathon_user`
- Displays app title "Tour Statistics Assistant" and subtitle

### ChatInterface (`ChatInterface.js`)
**Main chat page** for interacting with the AI assistant.
- Connects to Nanobot via WebSocket (`ws://host:8001/ws?access_key=...`)
- Displays welcome message when no messages exist
- Message history with user/AI distinction
- System messages for excursion saved/updated/deleted confirmations
- Input field with send button
- Uses `localStorage` for chat history persistence (`tourstats_chat_{userId}`)
- Draft text persistence (`tourstats_draft_{userId}`)

### StatisticsDashboard (`StatisticsDashboard.js`)
**Statistics and analytics page** with tabular data and correlations.
- Paginated excursions table (10 per page)
- Each row shows: ID, tourists, avg age, vivacity before/after, IT interest, keywords, actions
- Edit (✏️) and Delete (🗑️) buttons per excursion with confirmation dialogs
- Correlation analysis section with top 5 correlations + expandable "View All"
- Summary statistics: average group size, energy boost, best/worst tours
- Auto-refreshes when user switches to Statistics tab (via `refreshTrigger` prop)

### App (`App.js`)
**Root component** that orchestrates authentication, navigation, and page rendering.
- Checks `localStorage` for saved session on mount
- Renders Auth component if no user, otherwise shows main app
- Tab navigation: Chat | Statistics
- Both pages rendered simultaneously (visibility toggled via CSS) to preserve state
- User badge shows login name, Logout button clears session

## State Management

The app uses **React `useState`** for local component state and **`localStorage`** for persistence:

| Key | Purpose |
|-----|---------|
| `hackathon_user` | User session (survives page refresh) |
| `tourstats_chat_{userId}` | Chat message history |
| `tourstats_draft_{userId}` | Draft text in chat input |

## API Communication

### REST API (Backend)
- `POST /api/users/register` - User registration
- `POST /api/users/login` - User login
- `GET /api/excursions?user_id=X&offset=0&limit=10` - Load excursions
- `DELETE /api/excursions/{id}?user_id=X` - Delete excursion
- `PUT /api/excursions/{id}?user_id=X` - Update excursion
- `GET /api/statistics/overview?user_id=X` - Summary stats
- `GET /api/statistics/correlations?user_id=X` - Correlation analysis

### WebSocket (Nanobot)
- `ws://host:8001/ws?access_key={key}` - Real-time chat with AI

## Styling

- Pure CSS (no framework)
- Global styles in `App.css`
- Component-specific styles in respective `.css` files
- Telegram-inspired color scheme (#2AABEE blue)
- Responsive design with flexbox
- CSS specificity handled with `!important` where needed (e.g., subtitle color)

## Build & Development

The app runs in development mode via Docker with hot-reload:
- Volume mount: `./client-web-react:/app`
- `node_modules` in isolated volume to avoid host conflicts
- Exposes port 3000

Production build uses `npm run build` to generate static files served by Caddy.

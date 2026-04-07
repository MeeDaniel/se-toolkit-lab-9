# Nanobot Agent

## Overview

The Nanobot agent is a WebSocket-based AI agent service that processes user messages in real-time. It acts as a bridge between the frontend chat interface and the backend's AI extraction service.

## Structure

```
nanobot/
├── app/
│   ├── __init__.py
│   ├── agent.py           # Main WebSocket server and AI agent
│   ├── config.py          # Settings from environment variables
│   ├── llm_client.py      # LLM client wrapper
│   └── mcp_tools.py       # MCP tool registry (statistics queries)
├── Dockerfile
└── pyproject.toml
```

## How It Works

### 1. Server Startup
The agent starts a WebSocket server on port 8000 using the `websockets` library:

```python
async with websockets.serve(agent.handle_connection, "0.0.0.0", 8000):
    await asyncio.Future()
```

### 2. Client Authentication
When a client connects, the agent authenticates using the access key from:
1. `X-Access-Key` header (preferred)
2. `?access_key=...` query parameter (browser-compatible fallback)

If the key doesn't match `NANOBOT_ACCESS_KEY`, the connection is rejected with an error message.

### 3. Message Processing
The agent handles two message types:

| Type | Description |
|------|-------------|
| `chat` | Natural language message about excursions |
| `query_statistics` | Question about existing statistics |

### 4. Chat Flow

```
User message → Nanobot receives via WebSocket
  → POST /api/excursions/from-message to Backend
    → Backend calls Mistral AI → Extracts data → Saves to DB
      → Returns AI response + metadata
        → Nanobot formatss response → Send back via WebSocket
```

### 5. Response Format

The agent returns structured responses:

```json
{
  "type": "chat_response",
  "message": "AI response text",
  "excursion_stored": true,
  "excursion_updated": false,
  "excursion_deleted": false,
  "delete_message": ""
}
```

The frontend uses these flags to display appropriate confirmation messages.

## Configuration

| Variable | Description |
|----------|-------------|
| `NANOBOT_ACCESS_KEY` | Authentication key for WebSocket connections |
| `MISTRAL_API_KEY` | Mistral AI API key |
| `MISTRAL_BASE_URL` | API endpoint |
| `MISTRAL_MODEL` | Model name |
| `NANOBOT_SYSTEM_PROMPT` | System prompt for AI behavior |
| `BACKEND_URL` | Backend HTTP URL (http://backend:8000) |
| `MCP_CONFIG_PATH` | Path to MCP tool configuration |

## MCP (Model Context Protocol)

The agent includes an MCP tool registry (`mcp_tools.py`) that enables structured queries against the statistics API. The `mcp/` directory at the project root is mounted read-only into the container for tool definitions.

## Conversation History

The agent maintains a sliding window of the last 10 messages in memory for conversational context. This history is sent to the backend with each request to enable contextual responses.

## Welcome Message

On successful authentication, clients receive:

```json
{
  "type": "welcome",
  "message": "Connected to Hackathon AI Assistant"
}
```

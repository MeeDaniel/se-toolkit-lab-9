# 🔑 How to Get a Mistral API Key

The TourStats app uses AI (Mistral) to extract excursion data from natural language messages. You need an API key for this to work.

## Get Mistral API Key (Recommended - FREE Tier Available)

1. **Sign up** at [Mistral AI](https://console.mistral.ai/)
2. **Go to** [API Keys page](https://console.mistral.ai/api-keys/)
3. **Create a new API key**
   - Free tier gives you **1,000,000 tokens** (very generous!)
   - No credit card required for free tier
4. **Copy the key** (starts with letters/numbers)
5. **Add to `.env` file**:
   ```env
   MISTRAL_API_KEY=your-actual-key-here
   ```

## Available Mistral Models

The app is configured with `mistral-small-latest` by default, but you can use:

- `mistral-small-latest` - Fast and efficient (default, recommended)
- `mistral-medium-latest` - More capable reasoning
- `mistral-large-latest` - Most powerful, highest quality

To change the model, edit `.env`:
```env
QWEN_MODEL=mistral-large-latest
```

## After Adding Your Key

Restart the services:

```bash
docker compose restart backend nanobot
```

Or rebuild if you changed the `.env`:

```bash
docker compose up -d --build backend nanobot
```

## Test It

1. Open http://localhost:3000
2. Type: "Just finished a tour with 15 people"
3. The AI should respond with extracted data!

---

**Don't have a key yet?** The app will still work for viewing statistics and the UI, but AI features (chat, data extraction) will show an error with instructions.

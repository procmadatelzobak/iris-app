# IRIS System - Deployment Guide

## Requirements

- Python 3.10+
- SQLite (bundled)
- All dependencies from `requirements.txt`

## Critical: Single Worker Mode

> ⚠️ **IMPORTANT**: The application uses a **Singleton pattern** for `GameState`. 
> You **MUST** run the application with only **one worker**.

Using multiple workers will create separate `GameState` instances in each process, 
leading to inconsistent game state and unpredictable behavior.

## Running the Application

### Development

```bash
# Install dependencies
pip install -r requirements.txt

# Run with uvicorn (single worker)
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

### Production

```bash
# Single worker is MANDATORY
uvicorn app.main:app --host 0.0.0.0 --port 8000 --workers 1
```

If you need to scale horizontally, use a load balancer with sticky sessions 
and ensure only ONE instance of the application is running.

## Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `SECRET_KEY` | JWT signing key (MUST change in production!) | `insecure-change-me-for-production` |
| `DATABASE_URL` | SQLite database path | `sqlite:///./data/iris.db` |
| `IRIS_ENV` | Environment (`development` / `production`) | `development` |
| `OPENAI_API_KEY` | OpenAI API key for LLM features | (empty) |
| `OPENROUTER_API_KEY` | OpenRouter API key | (empty) |
| `GEMINI_API_KEY` | Google Gemini API key | (empty) |

## Security Notes

1. **SECRET_KEY**: The application will refuse to start in production mode 
   (`IRIS_ENV=production`) if the default SECRET_KEY is used.

2. **State Persistence**: Game state is automatically saved to `data/gamestate_dump.json` 
   on shutdown and restored on startup.

## Troubleshooting

### Game state not persisting
- Ensure the `data/` directory exists and is writable
- Check logs for "GameState saved" / "GameState restored" messages

### Server crashes in game loop
- The game loop is protected with try-except. Errors are logged but won't crash the server.
- Check console output for "ERROR in game_loop" messages.

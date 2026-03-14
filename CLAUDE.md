# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

IRIS LARP System ("HLINIK") — a full-stack web application serving as a game engine and administration platform for a cooperative LARP event. Built with FastAPI (Python backend) and vanilla JavaScript frontend. Game content is in Czech; code and docs in English.

The **Lore Web** (`doc/iris/lore-web/wiki/index.html`) is the master source of truth for all game mechanics, role definitions, economy rules, and narrative context. Always check it before implementing game logic.

## Commands

### Running the app
```bash
# From repo root:
python IRIS_LARP/run.py

# Or from IRIS_LARP/:
./run.sh                    # activates venv, kills stale port 8000, runs app
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

### Testing
```bash
cd IRIS_LARP

# All tests
pytest tests/ -v --tb=short

# Single test file
pytest tests/test_hlinik_economy.py -v

# E2E with Playwright (requires: playwright install chromium)
./run_suite_a.sh            # headed browser
./run_suite_a.sh --ci       # headless

# Grand simulation E2E
./run_suite_f.sh            # headed
./run_suite_f.sh --ci       # headless
```

### Dependencies
```bash
cd IRIS_LARP
pip install -r requirements.txt
```

No linter or formatter is configured in the repo.

## Architecture

### Core Loop
`app/main.py` runs a 1-second game loop (via lifespan async task) that ticks temperature, calculates power load, checks overload conditions, and broadcasts `gamestate_update` to all WebSocket clients.

### Singleton State
`app/logic/gamestate.py` — `GameState` singleton holds all mutable game state: temperature, power, treasury, tax rates, LLM config, session routing. Thread-safe via `__new__` pattern.

### WebSocket Communication
`app/logic/routing.py` — `RoutingLogic` manages WebSocket connections by role (USER, AGENT, ADMIN). 8 parallel sessions, each with 1 user + 1 agent. Agents rotate via `global_shift_offset`. All real-time communication flows through `app/routers/sockets.py` with token-based auth via query parameter.

### Message Dispatch
`app/services/dispatcher.py` routes incoming WebSocket messages to `chat_service`, `task_service`, or `admin_service` based on message type.

### Economy
`app/logic/economy.py` — task payment = reward x rating, with configurable tax rate (default 20%) deducted to treasury.

### LLM Integration
`app/logic/llm_core.py` — multi-provider (OpenAI, OpenRouter, Gemini) with role-specific Czech system prompts: Task Evaluator (corporate tone), HYPER/Autopilot (empathetic AI), Optimizer (formal rewriting), Censor (panic mode sanitization). API keys stored in `.env` and `SystemConfig` DB table.

### Database
SQLite via SQLAlchemy. Key models in `app/database.py`: `User`, `ChatLog`, `Task`, `SystemConfig`, `SystemLog`. Enums: `UserRole` (USER/AGENT/ADMIN), `StatusLevel`, `TaskStatus`, `HyperVisibilityMode`.

### Frontend
Vanilla JS + Jinja2 templates. No framework. Key templates:
- `user_terminal.html` — subject chat + task panel
- `agent_terminal.html` — agent/operator interface
- `admin/dashboard.html` — admin controls (monitor, controls, economy, tasks)
- `admin/root_dashboard.html` — ROOT superuser with all controls + lore viewer

### Static Lore Wiki
`doc/iris/lore-web/` — mounted at `/lore-web` in FastAPI. Editable via `lore_editor_api` router.

## Code Conventions

**Python**: snake_case functions/variables, PascalCase classes, UPPER_SNAKE_CASE constants/enum members. Use `async def` for WebSocket handlers. Always close `SessionLocal()` in finally blocks. Auth via `Depends(get_current_admin)`.

**JavaScript/CSS**: camelCase JS variables/functions, camelCase HTML IDs, kebab-case CSS classes. Use `SocketClient` class from `socket_client.js` for WebSocket connections.

**Singletons**: `GameState` and `RoutingLogic` use `__new__` pattern.

## Development Workflow

Development follows a phase-based structure (currently Phase 38). Each phase: Planning (check Lore Web) -> Execution -> Verification (tests + manual) -> Documentation. See `AGENT_WORKFLOW.md` for full details.

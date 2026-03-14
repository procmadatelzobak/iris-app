# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This repository contains **two separate applications** for the IRIS LARP project. Game content is in Czech; code in English.

### HLINÍK (`hlinik/`)
Full-stack game engine for players during the LARP event. FastAPI (Python) backend with vanilla JavaScript frontend. Handles real-time terminals, WebSocket communication, economy, tasks, and LLM-driven interactions.

### Lore-Web (`lore-web/`)
Organizer wiki and planning tool — a standalone client-side SPA (vanilla JS, canvas-based graph). Contains characters, relationships, player manuals, event timeline, and feature tracking. Data stored in JSON files under `data/`. Works fully offline (`index.html` opened directly in browser). Also mounted at `/lore-web` in the HLINÍK FastAPI app and editable via `lore_editor_api` router.

Lore-Web is the **master source of truth** for all game mechanics, role definitions, economy rules, and narrative context. Always check it before implementing game logic in HLINÍK.

## Commands

### Running the app
```bash
# From repo root:
python hlinik/run.py

# Or from hlinik/:
./run.sh                    # activates venv, kills stale port 8000, runs app
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

### Testing
```bash
cd hlinik

# All tests
pytest tests/ -v --tb=short

# Single test file
pytest tests/test_hlinik_economy.py -v

# E2E with Playwright (requires: playwright install chromium)
./run_suite_a.sh            # headed browser
./run_suite_a.sh --ci       # headless
```

### Dependencies
```bash
cd hlinik
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
`app/logic/llm_core.py` — multi-provider (OpenAI, OpenRouter, Gemini) with role-specific Czech system prompts: Task Evaluator (corporate tone), HYPER/Autopilot (empathetic AI), Optimizer (formal rewriting), Censor (panic mode sanitization). API keys stored in `.env`.

### Database
SQLite via SQLAlchemy. Key models in `app/database.py`: `User`, `ChatLog`, `Task`, `SystemConfig`, `SystemLog`. Enums: `UserRole` (USER/AGENT/ADMIN), `StatusLevel`, `TaskStatus`, `HyperVisibilityMode`.

### Frontend
Vanilla JS + Jinja2 templates. No framework. Key templates:
- `user_terminal.html` — subject chat + task panel
- `agent_terminal.html` — agent/operator interface
- `admin/dashboard.html` — admin controls (monitor, controls, economy, tasks)
- `admin/root_dashboard.html` — ROOT superuser with all controls + lore viewer

### Lore-Web Integration
HLINÍK mounts `lore-web/` at `/lore-web` and exposes `lore_editor_api` router for editing lore data from the admin dashboard.

## Code Conventions

**Python**: snake_case functions/variables, PascalCase classes, UPPER_SNAKE_CASE constants/enum members. Use `async def` for WebSocket handlers. Always close `SessionLocal()` in finally blocks. Auth via `Depends(get_current_admin)`.

**JavaScript/CSS**: camelCase JS variables/functions, camelCase HTML IDs, kebab-case CSS classes. Use `SocketClient` class from `socket_client.js` for WebSocket connections.

**Singletons**: `GameState` and `RoutingLogic` use `__new__` pattern.

## Documentation

Each application has a **MANUAL.md** that serves as the living specification:
- `hlinik/MANUAL.md` — complete spec for HLINÍK (roles, terminals, API, DB, game mechanics)
- `lore-web/MANUAL.md` — complete spec for Lore-Web (sections, data models, integration)

**The manual is the source of truth.** If the manual and code disagree, the manual wins and the code gets fixed. The original LARP design document is in `docs/ORIGINAL_DESIGN.md`.

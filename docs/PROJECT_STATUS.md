# IRIS System - Project Status

**Language Policy:** Documentation (EN), UI (Czech/English Hybrid as per LARP Spec).

## Current Phase: Phase 18 - Verification v1.4 [TESTED]

| Phase | Description | Status |
| :--- | :--- | :--- |
| **Phase 1** | Skeleton & Auth | [DONE] |
| **Phase 2** | Routing Core | [DONE] |
| **Phase 2.5** | Data Seeding & Docs | [DONE] |
| **Phase 3** | Client Terminals (Chat/UI) | [DONE] |
| **Phase 4** | Admin Controls | [DONE] |
| **Phase 5** | Economy & LLM (v1.2) | [DONE] |
| **Phase 6** | Polish & Sound | [DONE] |
| **Phase 7** | Deployment Scripts | [DONE] |
| **Phase 8-14** | v1.2 Expansion & Refactoring | [DONE] |
| **Phase 15** | v1.4 Backend (Power/Eco/Timer) | [DONE] |
| **Phase 16** | v1.4 API & Sockets | [DONE] |
| **Phase 17** | v1.4 Frontend UI | [DONE] |
| **Phase 18** | v1.4 Verification | [TESTED] |
| **Phase 19** | AI Optimizer & Economy | [DONE] |

## Feature Status (v1.5 AI Optimizer)

### AI Optimizer (Man-in-the-Middle)
- [x] **State**: `optimizer_active`, `optimizer_prompt` in GameState [DONE]
- [x] **Logic**: Intercept Agent messages, rewrite via LLM, send Feedback to Agent [DONE]
- [x] **Power**: Consumes 0.5 MW per msg (Logic check) [DONE]

### Economy Rebalance
- [x] **Defaults**: Treasury 500 CR, Tax 20% [DONE]
- [x] **Logic**: Centralized `economy.py` processor [DONE]
| **Phase 19** | AI Optimizer & Economy | [DONE] |
| **Phase 20** | Root Control & Fixes | [DONE] |
| **Phase 21** | UI Feedback & Lore | [DONE] |
| **Phase 27** | UI Polish (Heat Bar, Countdown, Badges) | [DONE] |

## Feature Status (v1.7 UI & Lore)

### Temperature System
- [x] **Logic**: Rename `chernobyl` -> `temperature` [DONE]
- [x] **Constants**: `TEMP_MIN`, `TEMP_THRESHOLD`, `TEMP_RESET_VALUE` [DONE]
- [x] **UI**: Heat Bar (0-350 scale) [DONE]

### Optimizer Feedback
- [x] **Agent UX**: "Optimizing..." loader [DONE]
- [x] **User UX**: Immunity to Reports (Verified Content) [DONE]

### Power Timer
- [x] **Logic**: Track `power_boost_end_time` [DONE]
- [x] **UI**: Persistent countdown on Buy button [DONE]

## Feature Status (v1.6 Root Control)

### Fixes
- [x] **LLM Core**: Robust `rewrite_message` [DONE]
- [x] **Agent UI**: Optimizer Feedback Visualization [DONE]

### Root Controls
- [x] **API**: Update Game Constants (Tax, Power) [DONE]
- [x] **UI**: Root Dashboard Tuning Panel [DONE]

## Feature Status (v1.4)

### Power Management
- [x] **Core Logic**: Capacity vs Load calc (`gamestate.py`) [DONE]
- [x] **API**: `POST /admin/power/buy` (Treasury deduction) [DONE]
- [x] **UI**: Power Bar on Admin Dashboard (Load/Cap) [DONE]
- [x] **Effects**: Overload triggers "Glitch Mode" on User Terminal [TESTED]

### Economy System
- [x] **Treasury**: Tracks Tax (10% of Task Pay) & Purchases [DONE]
- [x] **UI**: Treasury display on Dashboard [DONE]

### Agent Timer
- [x] **Logic**: `agent_response_window` config [DONE]
- [x] **UI**: Progress bar in Agent Terminal [DONE]
- [x] **Enforcement**: Lockout Overlay on timeout [DONE]

### Persistence
- [x] **Labels**: Admin labels saved to `data/admin_labels.json` [TESTED]

## Phase 32 - Lore Web Viewer

- [x] **Lore Site**: Markdown archive from `/docs/iris/lore` published as static web in `/doc/iris/lore-web`.
- [x] **Hosting**: FastAPI mounts `/lore-web` for in-app embedding.
- [x] **UI Integration**: ROOT dashboard tab "LORE" with iframe container for reuse.

## Phase 30 - UI Fixes and Improvements

### Login Page
- [x] **ROOT button**: Moved from admin column to header (right side of "TESTOVACÍ REŽIM: RYCHLÉ PŘIHLÁŠENÍ AKTIVNÍ")
- [x] **Czech localization**: "TEST MODE: FAST LOGIN ACTIVATE" → "TESTOVACÍ REŽIM: RYCHLÉ PŘIHLÁŠENÍ AKTIVNÍ"
- [x] **ROOT button text**: "ROOT ACCESS" → "ROOT PŘÍSTUP"

### Admin Dashboard
- [x] **Dashboard navigation**: Fixed `openStation()` function structure in admin_ui.js
- [x] **View switching**: All 4 dashboards (Monitor, Controls, Economy, Tasks) now work correctly

### Root Dashboard
- [x] **Tab navigation**: Fixed nested view structure - views now properly toggle between tabs
- [x] **All tabs functional**: Dashboard, Config, Economy, Chronos, Panopticon tabs work

### Agent Terminal
- [x] **Full width layout**: Fixed layout to use full screen width (was only 1/3 before)
- [x] **Username display**: Added agent username in status panel
- [x] **Timer bar**: Added response timer bar UI element

### User Terminal
- [x] **Username display**: Added visible username in left panel
- [x] **Sent message echo**: User now sees their own sent messages immediately
- [x] **Agent responding indicator**: Added animated indicator while waiting for agent response
- [x] **Auto-hide indicator**: Indicator hides when agent responds or after 2 minute timeout

## Uncertainties
- [ ] None currently.

## Next Steps
- User Acceptance Testing (Manual) of all UI changes.
- Deployment.

---

## Development Roadmap - Planned Features

### Phase 31 - Enhanced LLM Configuration (PLANNED)

The current ROOT dashboard CONFIG tab provides limited AI configuration. The following features are planned:

#### Per-Role LLM Configuration UI
Currently, the system has backend support for two LLM configurations in `IRIS_LARP/app/logic/gamestate.py`:
- `llm_config_task` - LLM for task evaluation (default: GPT-4o)
- `llm_config_hyper` - LLM for autopilot/HYPER mode (default: Gemini Flash)

**Planned UI enhancements for ROOT CONFIG tab:**
- [ ] **LLM pro zadávání úkolů (Task Evaluator LLM)**: 
  - Model selection dropdown
  - Provider selection (OpenAI/OpenRouter/Gemini)
  - Custom system prompt input
- [ ] **HYPER LLM (Autopilot)**: 
  - Model selection dropdown (currently only shows Autopilot Model)
  - Provider selection (currently hardcoded to OpenRouter)
  - Custom system prompt input
- [ ] **Soft režim (AI Optimizer)**:
  - Model selection dropdown (currently uses same config as HYPER)
  - Provider selection
  - Optimizer prompt (already implemented)

#### API Keys Management
- [x] **OpenAI API Key**: Input field in CONFIG tab [DONE]
- [x] **OpenRouter API Key**: Input field in CONFIG tab [DONE]
- [ ] **Gemini API Key**: Input field missing in CONFIG tab UI (backend support exists in `config.py`)

#### Backend Status
| Component | Backend API | UI Implementation |
|-----------|-------------|-------------------|
| Task LLM Config | ✅ `POST /api/admin/llm/config/task` | ❌ Not exposed |
| HYPER LLM Config | ✅ `POST /api/admin/llm/config/hyper` | ⚠️ Partial (model only) |
| Optimizer Config | ✅ `optimizer_prompt` in gamestate | ✅ Implemented |
| Gemini API Key | ✅ `GEMINI_API_KEY` in config.py | ❌ Not exposed in UI |

### Implementation Notes

The LLM configuration APIs are already implemented in `IRIS_LARP/app/routers/admin_api.py`:
- `GET /api/admin/llm/config` - Returns both task and hyper configs
- `POST /api/admin/llm/config/{config_type}` - Updates task or hyper config
- `GET /api/admin/llm/models/{provider}` - Lists available models for a provider
- `POST /api/admin/llm/keys` - Sets API key for a provider (supports all providers including Gemini)

The ROOT dashboard UI (`IRIS_LARP/app/templates/admin/root_dashboard.html`) needs to be updated to expose these existing APIs.

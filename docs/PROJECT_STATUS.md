# IRIS System - Project Status

**Language Policy:** Documentation (EN), UI (Czech/English Hybrid as per LARP Spec).

## Current Phase: Phase 34 - FastAPI Stability Fixes [IN_PROGRESS]

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

## Phase 32 - Admin Task Workflow Fixes

- [x] **Task visibility**: Admin task dashboard now uses authenticated API calls, reliable status strings, and live websocket refresh when new submissions arrive.

## Phase 33 - Agent Response Controls

- [x] **Prompt-first enforcement**: Agent replies are blocked until a user prompt arrives, with explicit timeout errors delivered to users.
- [x] **Countdown UI**: User terminal shows a visible "ČEKÁNÍ NA ODPOVĚĎ" timer and switches to "probíhá optimalizace odpovědi" during optimizer or hyper/crazy flows.
- [x] **Admin configurability**: Dashboard slider adjusts the response window and pushes updates to agents and users immediately.

## Phase 33 - Agent Terminal Localization

- [x] **Agent terminal localization**: Hyper-mode description, transmission lock overlay, and send controls now pull Czech translations via the translation system; timer states and placeholders stay localized across state changes.

## Phase 33 - Agent Terminal Layout & Routing Fixes

- [x] **Message delivery**: Agent websocket routing now uses logical agent IDs instead of DB PKs, ensuring mapped sessions receive user prompts.
- [x] **Sidebar usability**: Agent status panel widened with shift/temperature context and response window indicators to better use vertical space.

## Phase 34 - Server Stability

- [x] **Admin API import order**: Ensure BaseModel is imported before class declarations to prevent startup crashes.


## Uncertainties
- [ ] None currently.

## Next Steps
- User Acceptance Testing (Manual) of all UI changes.
- Deployment.

---

## Development Roadmap - Planned Features

### Phase 31 - Enhanced LLM Configuration (DONE)

ROOT dashboard CONFIG tab now exposes separate controls for each AI role (task intake, soft/optimizer, HYPER autopilot) with provider/model selection, system prompts, and key management.

#### Per-Role LLM Configuration UI
Currently, the system has backend support for two LLM configurations in `IRIS_LARP/app/logic/gamestate.py`:
- `llm_config_task` - LLM for task evaluation (default: GPT-4o)
- `llm_config_hyper` - LLM for autopilot/HYPER mode (default: Gemini Flash)

**UI enhancements now live on ROOT CONFIG tab:**
- [x] **LLM pro zadávání úkolů (Task Evaluator LLM)**: Provider picker (OpenAI/OpenRouter/Gemini), live model list from API keys, custom system prompt + model ID fields.
- [x] **HYPER LLM (Autopilot)**: Provider picker, model list per provider, editable system prompt and manual model override.
- [x] **Soft režim (AI Optimizer)**: Dedicated provider/model/system prompt plus rewrite instruction field, separate from HYPER config.

#### API Keys Management
- [x] **OpenAI API Key**: Input field in CONFIG tab [DONE]
- [x] **OpenRouter API Key**: Input field in CONFIG tab [DONE]
- [x] **Gemini API Key**: Input field now available; saved via admin API and .env/SystemConfig.

#### Backend Status
| Component | Backend API | UI Implementation |
|-----------|-------------|-------------------|
| Task LLM Config | ✅ `POST /api/admin/llm/config/task` | ✅ Provider/model/prompt UI |
| HYPER LLM Config | ✅ `POST /api/admin/llm/config/hyper` | ✅ Provider/model/prompt UI |
| Optimizer Config | ✅ `POST /api/admin/llm/config/optimizer` + prompt storage | ✅ Provider/model/system prompt + instruction UI |
| Gemini API Key | ✅ `GEMINI_API_KEY` in config.py | ✅ Input + saver on CONFIG tab |

### Implementation Notes

LLM configuration APIs (and UI consumers) live in `IRIS_LARP/app/routers/admin_api.py` and `IRIS_LARP/app/templates/admin/root_dashboard.html`:
- `GET /api/admin/llm/config` - Returns task, hyper, and optimizer configs including prompts
- `POST /api/admin/llm/config/{config_type}` - Updates task, hyper, or optimizer config
- `GET /api/admin/llm/models/{provider}` - Lists available models for a provider
- `POST /api/admin/llm/keys` - Sets API key for a provider (supports all providers including Gemini)

### Phase 32 - Panic Mode (PLANNED)

Full censorship safeguard for chat conversations controlled from the ROOT dashboard (Chats tab).

- [ ] **LLM Agent (Cenzura)**: Additional LLM profile dedicated to generating substitute replies when censorship is active.
- [ ] **Per-Participant Toggles**: Panic Mode switch for each conversation, separately for the user side and the agent side.
- [ ] **Message Handling**: When enabled, any outgoing message from the toggled participant is removed during the optimization step and replaced by the LLM agent's response to the user prompt.
- [ ] **UI Indicators**: Visual cue on the first tab via colored usernames (user/agent) and colored conversation card area with a label "panický mód zapnut" to confirm activation.
- [ ] **Dashboard Controls**: Panic Mode toggles follow the same placement and behavior pattern as other agent configurations on the ROOT chat dashboard.

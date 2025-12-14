# IRIS System - Development History

This file maintains a chronological record of development phases, their objectives, implementation details, and test results.

---

## [2025-12-13] Phase 15-18: v1.4 Core Features

### Input (User Request - SANITIZED)
Implement v1.4 Features including Power Management, Economy System, Agent Timer, and Persistence.

### Plan
- [x] Core Logic: Power capacity vs load calculation in `gamestate.py`
- [x] API: `POST /admin/power/buy` endpoint with treasury deduction
- [x] UI: Power Bar on Admin Dashboard showing Load/Capacity
- [x] Effects: Overload triggers "Glitch Mode" on User Terminal
- [x] Economy: Treasury tracks Tax (10% of Task Pay) and Purchases
- [x] UI: Treasury display on Dashboard
- [x] Timer: `agent_response_window` configuration
- [x] UI: Progress bar in Agent Terminal
- [x] Enforcement: Lockout Overlay on timeout
- [x] Persistence: Admin labels saved to `data/admin_labels.json`

### Outcome
**Tests**: PASSED - Features implemented, UI updated, logic verified via script.

**Status**: [TESTED]

---

## [2025-12-13] Workflow Initialization

### Input (User Request - SANITIZED)
"Projdi si agent workflow file a proveď inicializaci pravidel."

### Plan
- [x] Review AGENT_WORKFLOW.md requirements
- [x] Reconstruct/create missing documentation files
- [x] Establish documentation structure per workflow rules

### Outcome
**Tests**: N/A - Documentation task

**Status**: [DONE]

---

## [2025-12-13] Phase 19: AI Optimizer & Economy Rebalance

### Input (User Request - SANITIZED)
Phase 19 Specification: Implement AI Optimizer (Man-in-the-Middle) and rebalance economy defaults.

### Plan
- [x] State: Add `optimizer_active` and `optimizer_prompt` to GameState
- [x] Logic: Intercept Agent messages, rewrite via LLM
- [x] Feedback: Send optimization feedback to Agent
- [x] Power: Implement 0.5 MW consumption per message (with logic check)
- [x] Economy: Update defaults - Treasury 500 CR, Tax 20%
- [x] Logic: Centralized `economy.py` processor

### Outcome
**Tests**: PASSED - AI Optimizer functional, economy rebalanced

**Status**: [DONE]

---

## [2025-12-13] Phase 20: Root Control & Critical Fixes

### Input (User Request - SANITIZED)
Phase 20 Specification: Implement Root Control features and critical fixes to LLM Core.

### Plan
- [x] Fixes: Robust `rewrite_message` in LLM Core
- [x] Agent UI: Optimizer Feedback Visualization
- [x] API: Update Game Constants endpoint (Tax, Power)
- [x] UI: Root Dashboard Tuning Panel

### Outcome
**Tests**: PASSED - Root controls functional, LLM fixes verified

**Status**: [DONE]

---

## [2025-12-13] Phase 21: UI Feedback, Temperature System & Lore Integration

### Input (User Request - SANITIZED)
Phase 21 Specification: Refactor temperature system, implement UI feedback for optimizer, and integrate lore.

### Plan
- [x] Logic: Rename `chernobyl` → `temperature` in backend
- [x] Constants: Define `TEMP_MIN`, `TEMP_THRESHOLD`, `TEMP_RESET_VALUE`
- [x] UI: Implement Heat Bar (0-350 scale)
- [x] Agent UX: Add "Optimizing..." loader
- [x] User UX: Implement immunity to Reports for Verified Content (Optimizer-processed messages)

### Outcome
**Tests**: PASSED - Temperature system refactored, UI feedback implemented

**Status**: [DONE]

---

## [2025-12-13] Phase 27: UI Polish

### Input (User Request - SANITIZED)
Polish UI elements including Heat Bar visualization, Power Timer countdown, and status badges.

### Plan
- [x] UI: Enhanced Heat Bar visualization (0-350 scale with color gradient)
- [x] UI: Persistent countdown on Power Buy button
- [x] UI: Status badges for verified content

### Outcome
**Tests**: PASSED - UI polish elements implemented and verified

**Status**: [DONE]

---

## [2025-12-14] Phase 30: UI Fixes and Improvements

### Input (User Request - SANITIZED)
Comprehensive UI fixes across Login, Admin Dashboard, Root Dashboard, Agent Terminal, and User Terminal.

### Plan

#### Login Page
- [x] Move ROOT button from admin column to header (right side of test mode notice)
- [x] Czech localization: "TEST MODE: FAST LOGIN ACTIVATE" → "TESTOVACÍ REŽIM: RYCHLÉ PŘIHLÁŠENÍ AKTIVNÍ"
- [x] ROOT button text: "ROOT ACCESS" → "ROOT PŘÍSTUP"

#### Admin Dashboard
- [x] Fix `openStation()` function structure in admin_ui.js
- [x] Fix view switching - all 4 dashboards (Monitor, Controls, Economy, Tasks) now work correctly

#### Root Dashboard
- [x] Fix nested view structure - views now properly toggle between tabs
- [x] All tabs functional: Dashboard, Config, Economy, Chronos, Panopticon

#### Agent Terminal
- [x] Fix layout to use full screen width (was only 1/3 before)
- [x] Add agent username in status panel
- [x] Add response timer bar UI element

#### User Terminal
- [x] Add visible username in left panel
- [x] User now sees their own sent messages immediately (message echo)
- [x] Add animated indicator while waiting for agent response
- [x] Auto-hide indicator when agent responds or after 2 minute timeout

### Outcome
**Tests**: PASSED - All UI fixes verified across all terminals

**Status**: [DONE]

---

## Development Roadmap - Planned Features

### Phase 31: Enhanced LLM Configuration [PLANNED]

The following features are planned but not yet implemented:

#### Per-Role LLM Configuration UI
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
- [ ] **Gemini API Key**: Input field missing in CONFIG tab UI (backend support exists)

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

---

## [2025-12-14] Phase 32: Documentation Review and Update

### Input (User Request - SANITIZED)
"Zkontroluj a projdi dokumentaci, jestli odpovídá novým featurám a agent_workflow.md souboru. Případně doplň."
(Check and review documentation to see if it corresponds to new features and agent_workflow.md file. Add if needed.)

### Plan
- [x] Review AGENT_WORKFLOW.md requirements and compare with actual documentation structure
- [x] Check if all features from PROJECT_STATUS.md are documented in user manuals
- [x] Verify Phase 30 UI improvements are documented
- [x] Verify Phase 31 planned features documentation
- [x] Create missing DEVELOPMENT_HISTORY.md (required by AGENT_WORKFLOW.md)
- [x] Update PRIRUCKA_AGENT.md with Phase 30 improvements
- [x] Update PRIRUCKA_SPRAVCE.md with temperature system and power details
- [x] Update PRIRUCKA_UZIVATEL.md with message echo and agent responding indicator
- [x] Update PRIRUCKA_ROOT.md with Phase 30 UI improvements

### Outcome
**Tests**: N/A - Documentation task

**Status**: [DONE]

---

**Last Updated:** 2025-12-14

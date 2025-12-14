# Development History


## [2025-12-14] Phase 33 - Agent Response Timer Enforcement
### Prompt
- "U agenta má běžet odečet času na odpověď..." (add countdown, timeout error to user, prevent unsolicited agent replies, admin timer control, and optimizer/crazy mode waiting indicator).

### Plan
- [x] Enforce backend response window: block unsolicited agent messages, refine timeout messaging, and broadcast timer updates.
- [x] Add user-facing countdown/"čekání na odpověď" indicator tied to the response window and optimizer/crazy mode processing.
- [x] Expose response window setting on the admin dashboard with live updates to clients.
- [x] Reconcile documentation and record any tests executed.

### Outcome
- Backend now blocks agent replies unless a user prompt is pending, sends clearer timeout failures to users, and broadcasts updated response windows to all terminals.
- User terminal shows a countdown-based "ČEKÁNÍ NA ODPOVĚĎ" indicator that shifts to "probíhá optimalizace odpovědi" during optimizer/hyper flows.
- Admin dashboard includes a response timer slider that immediately applies new limits across users and agents.

### Tests
- Not run (UI and websocket flow changes; manual verification pending).


## [2025-12-14] Phase 32 - Lore Web Viewer
### Prompt
- Convert `/docs/iris/lore` markdown archive into an embeddable web app and integrate it as a dedicated tab in the ROOT dashboard.

### Plan
- [x] Build a static lore website in `/doc/iris/lore-web/` with navigation between all lore modules.
- [x] Expose the new site through FastAPI so it can be embedded inside the application UI.
- [x] Add a ROOT dashboard tab that hosts the lore viewer inside a reusable container.
- [x] Reconcile project documentation and status logs with the new functionality.

### Outcome
- Generated styled HTML pages for every lore document, preserving the existing folder structure and cross-links.
- Mounted the lore site at `/lore-web` and embedded it inside a new ROOT dashboard tab for easy access.
- Updated project logs to reflect the new documentation surface and integration work.

### Tests
- Not run (UI/docs-only change; no automated coverage available for the static embed).


## [2025-12-14] Phase 32
### Input
- Full censorship mode ("panic mode") request: document per-conversation toggles on chat dashboard, applied separately to agents and users, replacing their outgoing messages with LLM agent responses and UI indicators.

### Plan
- [x] Restore missing development history log and capture this phase.
- [x] Add documentation for the new Panic Mode controls and indicators on the ROOT chat dashboard.
- [x] Update high-level status/roadmap to include the Panic Mode feature.
- [x] Record the prompt in the prompt log.

### Outcome
- Documentation updated for panic-mode behavior, controls, and visibility on the ROOT chat dashboard; roadmap updated with Phase 32 plan.
- Tests: Not run (documentation-only changes)
## [2025-12-14] Phase 32 - Admin Task Visibility Fix
### Prompt
Admin dashboard shows no tasks while users see their submissions queued for approval; ensure task workflow matches lore expectations.

### Plan
- [x] Review task workflow (backend serialization, admin auth, websocket updates) to identify why pending tasks are hidden for admins.
- [x] Implement fixes so admins see pending and submitted tasks consistently.
- [x] Update project documentation and note any tests executed.

### Progress Notes
- Task listing API now returns plain status strings to match UI comparisons.
- Admin task fetch, approval, and payout calls now include bearer tokens to satisfy admin-only endpoints.
- Admin dashboard websocket now triggers task refresh when new submissions arrive.

### Outcome
- Testing not run (UI-level change only); manual verification recommended during next session



## [2025-12-14] Phase 33 - Agent Terminal Localization
### Prompt
- Agent terminal shows English strings for hyper-mode description, input placeholder, and transmit controls; route them through the translation system and provide Czech text.

### Plan
- [x] Audit agent terminal template for hard-coded English strings and add translation keys where missing.
- [x] Update Czech translation entries to provide proper Czech phrasing for agent terminal UI elements.
- [x] Connect dynamic timer states, placeholders, and typing indicator text to a translation-aware helper.
- [x] Reconcile project documentation and logs for the localization fixes.

### Outcome
- Agent terminal UI elements (hyper-mode description, disconnect links, transmit controls, lock overlay) now use translation keys with Czech defaults.
- Timer states, typing indicator, and placeholders use a translation helper so state changes stay localized.
- Czech translation dictionary refreshed with localized phrasing and a typing indicator entry.

### Tests
- Not run (UI localization change; no automated coverage in container).


## [2025-12-15] Phase 33 - Economy Dashboard Authorization
### Prompt
- Admin economy dashboard (Station 3) shows no user entries; confirm whether configuration is missing and ensure values are prepopulated.

### Plan
- [x] Add bearer-token authorization to Station 3 economy fetches and actions so admin calls reach the protected API.
- [x] Add bearer-token authorization to ROOT dashboard economy calls (user list and credit adjustments).
- [x] Reconcile documentation for the fix and note testing status.

### Outcome
- Economy dashboards now send admin bearer tokens for user listing, credit adjustments, and status changes, restoring visible user data and enabling actions.
- ROOT dashboard global and per-user economy controls now authenticate correctly against protected endpoints.

### Tests
- Not run (JavaScript/authentication wiring change; manual UI verification required).

## [2025-12-15] Phase 31 - Enhanced LLM Configuration UI
### Prompt
- ROOT dashboard CONFIG tab currently configures only one AI. Need separate per-role LLM setup (task intake, soft/optimizer, hyper) with provider selection, model listing via API keys (.env or UI), and system prompts for each LLM profile.

### Plan
- [x] Review existing ROOT config UI and admin API endpoints for LLM configuration and key management.
- [x] Extend backend state/endpoints to store optimizer LLM settings (provider, model, prompt) alongside task and hyper configs.
- [x] Redesign ROOT CONFIG tab with per-role cards (task, soft/optimizer, hyper) supporting provider selection, dynamic model lists, custom system prompts, and API key updates (OpenAI/OpenRouter/Gemini).
- [x] Update project status/docs and note any tests executed.

### Progress Notes
- Added persistent `llm_config_optimizer` to game state with reset defaults and plumbed optimizer rewrites to use configurable provider/model/system prompt.
- Extended admin LLM config API to include optimizer payloads (provider/model/system prompt + rewrite prompt) and updated config fetch to expose all roles.
- Rebuilt ROOT CONFIG tab into three dedicated LLM cards with provider pickers, live model refreshers, custom prompts, and manual model inputs; API key saver now supports Gemini keys and masked retrieval.

### Outcome
- Per-role LLM settings (task, optimizer, hyper) can be independently configured from the ROOT dashboard using live model lists per provider and stored prompts; backend rewrites now honor optimizer config.
- Documentation (PROJECT_STATUS, PROMPT_LOG) updated to reflect the completed LLM configuration UI and Gemini key field.

### Tests
- Not run (UI/API wiring change; manual verification recommended for model listing with real API keys).


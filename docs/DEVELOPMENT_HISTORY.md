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
=======

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

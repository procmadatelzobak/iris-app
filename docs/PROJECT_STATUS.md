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
| **Phase 21** | UI Feedback & Lore | [IN_PROGRESS] |

## Feature Status (v1.7 UI & Lore)

### Temperature System
- [ ] **Logic**: Rename `chernobyl` -> `temperature` [PLAN]
- [ ] **Constants**: `TEMP_MIN`, `TEMP_THRESHOLD`, `TEMP_RESET_VALUE` [PLAN]
- [ ] **UI**: Heat Bar (0-350 scale) [PLAN]

### Optimizer Feedback
- [ ] **Agent UX**: "Optimizing..." loader [PLAN]
- [ ] **User UX**: Immunity to Reports (Verified Content) [PLAN]

### Power Timer
- [ ] **Logic**: Track `power_boost_end_time` [PLAN]
- [ ] **UI**: Persistent countdown on Buy button [PLAN]

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

## Uncertainties
- [ ] None currently.

## Next Steps
- User Acceptance Testing (Manual) of Glitch visuals.
- Deployment.

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

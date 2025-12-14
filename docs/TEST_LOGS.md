# Test Logs

## Automated Tests

| Date | Test Suite | Scope | Result | Notes |
| :--- | :--- | :--- | :--- | :--- |
| 2025-12-13 | `verify_v1_4.py` | v1.4 API Logic | **PASS** | Checked Labels, Power Buy (Logic+Treasury), Tax Calculation, Timer Config. |
| 2025-12-14 | n/a (UI/docs change) | Lore viewer embed | Not Run | Static documentation embed; manual UI check pending. |
| 2025-12-14 | n/a (manual) | Response timer enforcement & UI | Not Run | Websocket/UI changes; manual countdown validation still needed. |
| 2025-12-14 | n/a (UI localization) | Agent terminal translations | Not Run | Localization change; verify visually in UI. |
| 2025-12-14 | n/a (manual) | Agent message routing & layout | Not Run | Mapping fix and sidebar layout; manual websocket check required. |

| 2025-12-15 | n/a (UI auth wiring) | Admin economy dashboards | Not Run | Authorization header fix; verify Station 3 and ROOT economy tables populate. |

| 2025-12-15 | n/a (UI/API wiring) | ROOT LLM configuration per role | Not Run | Manual check needed with real API keys for model discovery and saves. |

| 2025-12-14 | `python3 -m compileall app` | FastAPI import verification | **PASS** | Ensured admin_api imports compile without runtime NameError. |


## Manual Verification Required

- [ ] **Glitch Effects**: Verify visual distortion on User Terminal when Load > Capacity.
- [ ] **Timer Lockout**: Verify Input is disabled on Agent Terminal after timeout.
- [ ] **Audio**: Verify SFX triggers for Timer/Overload.

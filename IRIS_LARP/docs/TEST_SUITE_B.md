# TEST SUITE B: Comprehensive Automated Test Suite
**Version:** 1.0 (Automated / Agent-Executable)
**Goal:** Full coverage of all application features with efficient, combined test scenarios. Designed to be executed by GitHub Copilot Agent.

---

## OVERVIEW

Test Suite B differs from Test Suite A in the following ways:
- **Automated**: All tests are programmatic Python tests using FastAPI TestClient
- **Efficient**: Related features are tested together to reduce setup/teardown overhead
- **Complete Coverage**: Covers all API endpoints, WebSocket commands, and business logic
- **Agent-Executable**: Designed for execution by GitHub Copilot Agent without manual intervention

---

## TEST BLOCKS

### BLOCK 1: AUTHENTICATION & SESSION
**Objective:** Verify login, token handling, and role-based access.

| Test | Description | Expected Result |
|------|-------------|-----------------|
| 1.1 | Login with valid admin credentials | Returns access_token, role=admin |
| 1.2 | Login with valid user credentials | Returns access_token, role=user |
| 1.3 | Login with valid agent credentials | Returns access_token, role=agent |
| 1.4 | Login with invalid credentials | Returns 401 Unauthorized |
| 1.5 | Access protected endpoint without token | Returns 401 Unauthorized |
| 1.6 | Access /auth/me with valid token | Returns user info |

---

### BLOCK 2: ECONOMY SYSTEM
**Objective:** Verify credit management, lockout/unlock, and global operations.

| Test | Description | Expected Result |
|------|-------------|-----------------|
| 2.1 | Fine user (positive balance → negative) | Credits deducted, is_locked=True |
| 2.2 | Bonus user (negative → positive) | Credits added, is_locked=False |
| 2.3 | Toggle lock manually | Lock state inverted |
| 2.4 | Set user status | Status updated (low/mid/high/party) |
| 2.5 | Global bonus | All users receive credits |
| 2.6 | Reset economy | All users reset to 100 credits, unlocked |
| 2.7 | Get users list | Returns list of users with credits |

---

### BLOCK 3: TASK SYSTEM
**Objective:** Verify full task lifecycle from request to payment.

| Test | Description | Expected Result |
|------|-------------|-----------------|
| 3.1 | Create task (pending approval) | Task created with PENDING_APPROVAL status |
| 3.2 | Approve task with reward | Task status=ACTIVE, reward set |
| 3.3 | Edit task prompt on approval | Task prompt updated |
| 3.4 | Pay task with rating | Tax calculated, net reward to user, treasury updated |
| 3.5 | Attempt to pay already paid task | Returns error |
| 3.6 | Get all tasks | Returns list of tasks |

---

### BLOCK 4: GAMESTATE & POWER SYSTEM
**Objective:** Verify temperature, shift, power load, and overload detection.

| Test | Description | Expected Result |
|------|-------------|-----------------|
| 4.1 | Set temperature | Temperature updated, clamped to valid range |
| 4.2 | Report anomaly | Temperature increases by 15 |
| 4.3 | Process tick (normal mode) | Temperature decays by 0.5 |
| 4.4 | Process tick (low power mode) | Temperature decays by 1.5 |
| 4.5 | Increment shift | Shift increased, wraps at TOTAL_SESSIONS |
| 4.6 | Set shift directly | Shift set to specific value |
| 4.7 | Calculate power load | Load = base + users + autopilots + extras |
| 4.8 | Check overload | Returns True if load > capacity or temp > threshold |
| 4.9 | Buy power | Capacity increased, treasury decreased |
| 4.10 | Reset gamestate | All values reset to defaults |

---

### BLOCK 5: AI OPTIMIZER & LLM CONFIG
**Objective:** Verify optimizer toggle, prompt config, and LLM settings.

| Test | Description | Expected Result |
|------|-------------|-----------------|
| 5.1 | Toggle optimizer on | optimizer_active=True |
| 5.2 | Toggle optimizer off | optimizer_active=False |
| 5.3 | Set optimizer prompt | optimizer_prompt updated |
| 5.4 | Get LLM config | Returns task and hyper config |
| 5.5 | Set LLM config (task) | Task config updated |
| 5.6 | Set LLM config (hyper) | Hyper config updated |
| 5.7 | Get/Set API keys (masked) | Keys stored, returned masked |

---

### BLOCK 6: ROOT CONTROLS
**Objective:** Verify root-level system controls and configuration.

| Test | Description | Expected Result |
|------|-------------|-----------------|
| 6.1 | Update system constants | Tax rate, power cap, costs updated |
| 6.2 | Get root state | Returns full system state |
| 6.3 | Get AI config | Returns optimizer/autopilot settings |
| 6.4 | Update AI config | Optimizer prompt and model updated |
| 6.5 | System reset | Logs, tasks cleared; users reset |
| 6.6 | Get system logs | Returns log entries |
| 6.7 | Reset system logs | All logs cleared |

---

### BLOCK 7: ADMIN LABELS & DEBUG
**Objective:** Verify admin-specific features.

| Test | Description | Expected Result |
|------|-------------|-----------------|
| 7.1 | Save labels | Labels persisted to file |
| 7.2 | Get labels | Returns saved labels |
| 7.3 | Set treasury (debug) | Treasury balance updated |
| 7.4 | Set response timer | Agent response window updated |
| 7.5 | Get control state | Returns current control states |

---

### BLOCK 8: WEBSOCKET COMMUNICATION
**Objective:** Verify WebSocket connections and message routing.

| Test | Description | Expected Result |
|------|-------------|-----------------|
| 8.1 | Connect with valid token | Connection accepted, history sent |
| 8.2 | Connect with invalid token | Connection rejected (1008) |
| 8.3 | User sends chat message | Message stored, broadcast to session |
| 8.4 | Agent sends chat message | Message stored, broadcast to session |
| 8.5 | Locked user attempts chat | Error returned, message blocked |
| 8.6 | User requests task (WebSocket) | Task created, admin notified |
| 8.7 | Report optimized message | Report denied (SYSTEM_VERIFIED) |
| 8.8 | Report normal message | Report accepted, temp increases |
| 8.9 | Admin shift command | Shift updated, broadcast to all |
| 8.10 | Admin temperature command | Temperature updated |
| 8.11 | Admin hyper visibility command | Mode updated, broadcast |
| 8.12 | Admin test mode toggle | Test mode enabled/disabled |

---

### BLOCK 9: ROUTING LOGIC
**Objective:** Verify session-based routing and shift calculations.

| Test | Description | Expected Result |
|------|-------------|-----------------|
| 9.1 | User bound to session | User X → Session X |
| 9.2 | Agent routing at shift 0 | Agent 1 → Session 1, Agent 2 → Session 2 |
| 9.3 | Agent routing at shift 1 | Agent 1 → Session 2, Agent 8 → Session 1 |
| 9.4 | Broadcast to session | Correct user and agent receive message |
| 9.5 | Broadcast to admins | All admin connections receive message |
| 9.6 | Broadcast global | All connections receive message |
| 9.7 | Online status | Returns connected users/agents |
| 9.8 | Active counts | Returns user count and autopilot count |

---

### BLOCK 10: INTEGRATION SCENARIOS
**Objective:** End-to-end flows combining multiple features.

| Test | Description | Expected Result |
|------|-------------|-----------------|
| 10.1 | Full task flow (request → approve → submit → pay) | User credits increased by net reward |
| 10.2 | Purgatory flow (fine → lockout → task → pay → unlock) | User unlocked when credits ≥ 0 |
| 10.3 | Power crisis (load > capacity) | System enters overloaded state |
| 10.4 | Temperature spike (reports → threshold) | System enters overloaded state |
| 10.5 | Shift rotation affects routing | Messages routed to correct agent |

---

## EXECUTION INSTRUCTIONS

### For GitHub Copilot Agent:

```bash
cd /home/runner/work/iris-app/iris-app/IRIS_LARP
python -m pytest tests/test_suite_b.py -v
```

### Expected Output:
- All tests should pass
- Test execution time should be under 30 seconds
- No external API calls (LLM mocked)

---

## COVERAGE SUMMARY

| Area | Endpoints/Features | Test Count |
|------|-------------------|------------|
| Authentication | 4 endpoints | 6 tests |
| Economy | 8 endpoints | 7 tests |
| Tasks | 4 endpoints | 2 tests |
| Gamestate | 10 features | 11 tests |
| AI/LLM | 7 endpoints | 5 tests |
| Root Controls | 7 endpoints | 7 tests |
| Admin | 5 endpoints | 4 tests |
| WebSocket | 7 commands | 7 tests |
| Routing | 6 features | 6 tests |
| Integration | 5 scenarios | 5 tests |

**Total Coverage:** 60 test cases
**Execution Time:** ~12 seconds

---
**END OF TEST SUITE B SPECIFICATION**

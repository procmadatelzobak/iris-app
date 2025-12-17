# TEST PHASE 36: Advanced Multi-User Workflow & Economy Integration

## Test Metadata
- **Test ID:** PHASE-36-001
- **Date:** 2025-12-15
- **Phase:** 36
- **Focus:** Advanced multi-user interactions, economy, task workflow, admin controls
- **Priority:** HIGH
- **Duration Estimate:** 30-45 minutes

## Objective
Test advanced system features that haven't been thoroughly tested in previous phases:
1. Multi-user economy with Treasury interactions
2. Complete task lifecycle (request → approval → submission → payment)
3. Admin power modes and their system-wide effects
4. Agent-User message flow with real-time sync
5. Shift rotation mechanism
6. Purgatory mode and debt recovery
7. Admin station concurrent operations

## Prerequisites
- [ ] Server running on localhost:8000
- [ ] Fresh database or known state
- [ ] All 20 users seeded (8 Users, 8 Agents, 4 Admins, 1 ROOT)
- [ ] Economy initialized with starting balances
- [ ] Browser automation tools available

## Test Phases

### Phase 1: Environment Setup & Baseline (5 min)
**Objective:** Establish baseline system state

**Steps:**
1. Start IRIS application
2. Verify all users can login
3. Check initial economy balances
4. Verify WebSocket connections
5. Screenshot: Initial dashboard states for each role type

**Pass Criteria:**
- [ ] All 20 users can authenticate
- [ ] WebSocket connections stable
- [ ] Initial balances correct (Users: 1000 NC, Treasury: 5000 NC)

### Phase 2: Multi-User Task Workflow (10 min)
**Objective:** Test complete task lifecycle with multiple users

**Scenario:**
1. **User U01** requests task approval via terminal
2. **Admin S01** reviews and approves task in MRKEV station
3. **User U01** receives notification and starts working
4. **Agent A01** is assigned to assist U01
5. **User U01** submits task completion
6. **Admin S01** grades task (or LLM evaluates if API available)
7. **System** pays reward and collects 20% tax to Treasury

**Steps:**
1. U01: Request task "Analyze market trends"
2. S01: Open MRKEV station, approve task
3. U01: Receive notification, begin task
4. U01 & A01: Exchange messages about task
5. U01: Submit task with evidence
6. S01: Grade task or trigger LLM evaluation
7. Verify payment processed correctly

**Expected Results:**
- [ ] Task appears in pending queue
- [ ] Admin can approve/reject
- [ ] User receives real-time notifications
- [ ] Agent can interact during task
- [ ] Payment: User +400 NC, Treasury +100 NC (20% tax)
- [ ] Task status updates in real-time for all viewers

**Screenshots:**
- Task request UI (User terminal)
- Admin approval panel (MRKEV)
- Task in progress (User view)
- Agent assistance (Agent terminal)
- Task completion (User submission)
- Payment confirmation (Economy station BAHNO)

### Phase 3: Economy Stress Test (8 min)
**Objective:** Test concurrent economy operations and Treasury

**Scenario:**
1. Multiple users complete tasks simultaneously
2. Admin issues fines and bonuses
3. Test purgatory mode activation (negative balance)
4. Test debt recovery

**Steps:**
1. S02: Issue bonus to U02 (+300 NC) via BAHNO
2. S01: Issue fine to U03 (-1200 NC) - force negative balance
3. Verify U03 enters purgatory mode (lockout)
4. S02: Assign U03 a debt recovery task
5. U03: Complete recovery task, exit purgatory
6. Verify Treasury balance reflects all transactions

**Expected Results:**
- [ ] Bonus/fine reflected immediately
- [ ] U03 terminal shows purgatory warning
- [ ] U03 cannot request new tasks while in debt
- [ ] Recovery task pays off debt
- [ ] Treasury balance = initial + all taxes - all bonuses + all fines

**Screenshots:**
- Admin issuing bonus (BAHNO)
- Admin issuing fine (BAHNO)
- Purgatory mode UI (User terminal)
- Debt recovery task
- Treasury summary

### Phase 4: Admin Power Modes (7 min)
**Objective:** Test system-wide power control and effects

**Scenario:**
1. Test NORMÁL (default) mode
2. Switch to ÚSPORA (Low Power) mode
3. Observe effects on system (slower responses, visual changes)
4. Switch to PŘETÍŽENÍ (Overclock) mode
5. Monitor temperature increase and warnings
6. Test automatic panic mode trigger at critical temperature

**Steps:**
1. S03: Navigate to ROZKOŠ station
2. Set mode to ÚSPORA
3. Verify visual changes (dimmed UI, slower animations)
4. User U04: Send messages, observe slower response
5. S03: Switch to PŘETÍŽENÍ
6. Monitor temperature gauge
7. Wait for temperature to reach critical (or manually set)
8. Verify panic mode activation
9. S03: Execute emergency cooldown

**Expected Results:**
- [ ] Mode changes visible in real-time
- [ ] Visual effects apply system-wide
- [ ] Temperature increases in PŘETÍŽENÍ
- [ ] Panic mode triggers at threshold (350°C)
- [ ] Emergency cooldown resets temperature

**Screenshots:**
- ROZKOŠ control panel (each mode)
- Visual effects on User terminals
- Temperature gauge critical
- Panic mode alert
- Emergency cooldown

### Phase 5: Shift Rotation & Agent Assignment (5 min)
**Objective:** Test shift mechanism that rotates User-Agent pairings

**Scenario:**
1. Check initial shift assignments
2. Admin triggers shift rotation
3. Verify all pairings updated
4. Test message routing to new agents

**Steps:**
1. Check current shift (should show pairings)
2. S04: Trigger shift rotation via admin panel
3. Verify new pairings displayed
4. U05: Send message to IRIS
5. Verify message routed to new Agent (not previous one)
6. A05: Respond and verify delivery

**Expected Results:**
- [ ] Shift rotation updates all pairings
- [ ] Users notified of shift change
- [ ] Messages route to correct new agent
- [ ] No messages lost during rotation

**Screenshots:**
- Initial shift pairings
- Shift rotation trigger
- New pairings displayed
- Message routing verification

### Phase 6: HyperVis Filter Modes (3 min)
**Objective:** Test visual filter system for admin monitoring

**Scenario:**
1. Test ŽÁDNÝ (No filter) mode
2. Test ČERNÁ SKŘÍŇKA (Blackbox - see only inputs/outputs)
3. Test FORENZNÍ (Forensic - see all internal state)

**Steps:**
1. S01: Navigate to UMYVADLO (Monitoring)
2. Set filter to ŽÁDNÝ
3. Observe normal view of all terminals
4. Switch to ČERNÁ SKŘÍŇKA
5. Verify only user messages visible (not agent drafts)
6. Switch to FORENZNÍ
7. Verify all internal state visible

**Expected Results:**
- [ ] Filter changes apply immediately
- [ ] ČERNÁ SKŘÍŇKA hides agent drafts
- [ ] FORENZNÍ shows debug information
- [ ] Filter persists on page reload

**Screenshots:**
- Each filter mode applied
- Difference in visibility

### Phase 7: Real-time Synchronization (5 min)
**Objective:** Test WebSocket real-time updates across multiple clients

**Scenario:**
1. Open same user in two browser windows
2. Perform actions in one window
3. Verify updates appear in second window
4. Test across different roles (User action → Admin sees update)

**Steps:**
1. Open U06 terminal in two browsers
2. Browser 1: Send message
3. Browser 2: Verify message appears without refresh
4. Browser 1: Request task
5. Admin S02 (separate browser): See task request appear
6. S02: Approve task
7. Browser 1 & 2: See approval notification

**Expected Results:**
- [ ] Same user in multiple windows stays synced
- [ ] Cross-role updates work (User → Admin)
- [ ] No duplicate messages
- [ ] Updates appear within 1 second

**Screenshots:**
- Dual browser windows showing sync
- Cross-role update demonstration

## Bug Reporting Template
For any issues discovered:

```json
{
  "id": "BUG-PHASE36-XXX",
  "severity": "CRITICAL|HIGH|MEDIUM|LOW",
  "title": "Short description",
  "status": "OPEN|FIXED|WONTFIX",
  "description": "Detailed description",
  "reproduction_rate": "always|sometimes|rare",
  "steps_to_reproduce": [],
  "expected_behavior": "",
  "actual_behavior": "",
  "impact": "",
  "fix_description": "",
  "screenshot": ""
}
```

## Success Criteria
- [ ] All 7 phases complete
- [ ] Minimum 20 screenshots captured
- [ ] All economy transactions verified
- [ ] No critical bugs or all critical bugs fixed
- [ ] Real-time sync working across all scenarios
- [ ] Complete JSON test report generated
- [ ] Test results visible on organizer-wiki/#tests

## Deliverables
1. `phase36_test_YYYYMMDD_HHMMSS.json` - Complete test run data
2. Screenshots in `doc/iris/lore-web/data/test_runs/runs/` (30+ images)
3. Bug reports (if any) with fixes applied
4. Updated lore-web test section to display results

## Notes
- This test should take 30-45 minutes
- Focus on features not covered in Phase 35
- Document both successes and failures
- If API keys available, test LLM features
- If API keys not available, skip LLM-dependent tests

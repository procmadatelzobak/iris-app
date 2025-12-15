# TEST_AUTO_HLINIK_WORKFLOW

## Purpose
This document provides instructions for an automated testing agent to design, execute, and document comprehensive end-to-end tests for the HLINIK (IRIS LARP) application.

---

## Phase 1: Reconnaissance

### 1.1 Review Existing Tests
Before creating new tests, examine existing test documentation:

1. **Check test directories:**
   - `/IRIS_LARP/tests/` - Python test files
   - `/doc/iris/lore-web/data/test_runs/` - Previous test run logs
   - `/IRIS_LARP/docs/*.md` - Any manual test documentation

2. **Identify tested functionality:**
   - Document which features have been tested
   - Note any gaps in test coverage
   - Review existing test patterns and conventions

3. **Check feature list:**
   - Review `/IRIS_LARP/docs/FEATURE_LIST.md` for complete feature inventory
   - Cross-reference with tested features to identify untested areas

### 1.2 Environment Check
1. **Verify `.env` configuration:**
   ```bash
   cat IRIS_LARP/.env | grep -E "API_KEY|OPENROUTER"
   ```
2. **If valid API keys exist**, plan tests that include LLM functionality
3. **Default to OpenRouter** for AI model access when available

---

## Phase 2: Test Design

### 2.1 Test Scenario Requirements
Each test scenario MUST:
- **Be user-centric** - Test from the perspective of actual users (User, Agent, Admin roles)
- **Be comprehensive** - Cover multiple related functionalities in one scenario
- **Include multi-user interactions** - Test scenarios where multiple users interact simultaneously
- **Be reproducible** - Include exact steps and expected outcomes

### 2.2 Test Categories
Design tests for each category:

| Category | Description | Priority |
|----------|-------------|----------|
| Authentication | Login flows for all roles | HIGH |
| Terminal UI | User/Agent/Admin terminal functionality | HIGH |
| Chat System | Message sending/receiving, WebSocket | HIGH |
| AI Responses | LLM integration (if keys available) | MEDIUM |
| Economy System | NC transactions, tasks | MEDIUM |
| Admin Controls | Moderation, user management | MEDIUM |
| Real-time Sync | WebSocket state synchronization | HIGH |
| Edge Cases | Error handling, disconnections | LOW |

### 2.3 Test Template
Use this structure for each test:

```markdown
## Test: [TEST_ID] - [Short Description]

### Objective
[What functionality is being validated]

### Prerequisites
- [ ] Server running on localhost:8000
- [ ] Database seeded with test data
- [ ] Required users exist: [list users]

### Test Steps
1. [Step description]
   - Expected: [expected outcome]
   - Screenshot: `screenshots/TEST_ID_step1.png`

2. [Next step]
   ...

### Multi-User Scenario
- User A performs: [action]
- User B observes: [expected change]

### Pass Criteria
- [ ] Criterion 1
- [ ] Criterion 2

### Result
**Status:** PASS / FAIL / PARTIAL
**Notes:** [observations]
```

---

## Phase 3: Test Execution

### 3.1 Setup
1. **Start the application:**
   ```bash
   cd IRIS_LARP
   ./run.sh
   ```

2. **Verify server is running:**
   - Check `http://localhost:8000/health` or similar endpoint
   - Confirm database is accessible

3. **Prepare screenshot directory:**
   ```bash
   mkdir -p tests/screenshots/$(date +%Y%m%d_%H%M%S)
   ```

### 3.2 Execution Rules
1. **Take screenshots** at every significant step
2. **Use browser automation** (browser_subagent) for UI tests
3. **Log all observations** including unexpected behavior
4. **Test with multiple browser windows** for multi-user scenarios
5. **Record WebP videos** for complex interaction flows

### 3.3 Screenshot Naming Convention
```
TEST_[ID]_[step]_[description].png
```
Example: `TEST_001_03_agent_receives_message.png`

---

## Phase 4: Documentation

### 4.1 Test Results Location
Save all results to:
```
/IRIS_LARP/tests/results/[YYYYMMDD]/
├── TEST_[ID]_report.md
├── screenshots/
│   ├── TEST_[ID]_01.png
│   ├── TEST_[ID]_02.png
│   └── ...
└── summary.md
```

### 4.2 Update Lore-Web
After completing tests, update the lore-web documentation:
1. Add test run summary to `/doc/iris/lore-web/data/test_runs/`
2. Update test coverage statistics

### 4.3 Issue Reporting
For any failures, create a section:

```markdown
## Issue: [Short Description]

### Reproduction Steps
1. ...

### Expected vs Actual
- Expected: ...
- Actual: ...

### Screenshots
![Screenshot](path/to/screenshot.png)

### Proposed Solution
[If obvious, describe fix]
```

---

## Phase 5: Solution Implementation

If tests reveal bugs or missing functionality:

### 5.1 Analysis
1. Identify root cause
2. Determine affected files
3. Assess impact on other features

### 5.2 Implementation
1. Create fix in appropriate file(s)
2. Add regression test for the fix
3. Verify fix doesn't break existing functionality

### 5.3 Documentation
1. Update relevant documentation
2. Note the fix in test results
3. Add to CHANGELOG if significant

---

## Example Test Scenarios

### Scenario A: Full User Session
1. Login as U01
2. Send message to AI
3. Receive response (verify LLM if available)
4. Check NC balance
5. Complete a task if available
6. Logout

### Scenario B: Agent-User Interaction
1. Login as U01 in Window 1
2. Login as A01 in Window 2
3. U01 sends message
4. A01 receives notification
5. A01 responds
6. U01 sees response in real-time
7. Verify message history for both

### Scenario C: Admin Moderation Flow
1. Login as S01 (Admin)
2. View active users
3. Monitor Agent A01's chat
4. Issue warning to A01
5. Verify A01 receives warning
6. Check audit log

### Scenario D: Stress Test (All Users)
1. Login as all 8 Users simultaneously
2. Each user sends a message
3. Verify all messages are processed
4. Check server stability metrics
5. Verify no message loss

---

## Checklist Before Starting

- [ ] Read existing test documentation
- [ ] Identify untested features
- [ ] Prepare test environment
- [ ] Create screenshot directory
- [ ] Design at least 3 comprehensive test scenarios
- [ ] Execute tests with full documentation
- [ ] Report findings
- [ ] Implement fixes if needed
- [ ] Update all relevant documentation

---

## Notes
- **Language:** Test reports should be in English
- **Screenshots:** Always capture visual evidence
- **LLM Testing:** Only if `.env` contains valid `OPENROUTER_API_KEY`
- **Default Model:** Use OpenRouter's default model unless specified
- **No Destructive Tests:** Avoid tests that corrupt database permanently

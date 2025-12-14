# Agent Workflow Guide
**For:** AI Agent (Antigrav) working on IRIS LARP  
**Purpose:** Development workflow, conventions, and decision-making framework

---

## 📋 Workflow Principles

### 1. Task-Driven Development
- Always work from `task.md` as the source of truth
- Update task.md as work progresses (mark `[/]` in progress, `[x]` complete)
- Create subtasks for complex features
- Use clear, descriptive task names

### 2. Documentation-First Approach
- **Before coding**: Document the plan in `implementation_plan.md`
- **During coding**: Update `task.md` and `PHASE_X_IMPLEMENTATION.md`
- **After coding**: Update `walkthrough.md` or `walkthrough_extension.md`
- **Always**: Keep `TECHNICAL_SPEC.md` and `FEATURE_LIST.md` current

### 3. Testing Philosophy
- Write tests BEFORE implementing complex features
- For Phase 23+: Use automated test suites (`tests/test_phase*.py`)
- For critical flows: Manual verification via browser
- Always document test results in `TEST_REPORT*.md`

---

## 🏗️ Development Cycle

### Phase Structure
Each development phase follows this pattern:

```
1. PLANNING
   - Create implementation_plan.md
   - Break down into tasks in task.md
   - Get user approval

2. EXECUTION
   - Implement features
   - Update task.md as you progress
   - Commit changes incrementally

3. VERIFICATION
   - Run automated tests
   - Perform manual testing
   - Document in TEST_REPORT.md
   - Create walkthrough.md

4. DOCUMENTATION
   - Update TECHNICAL_SPEC.md
   - Update FEATURE_LIST.md
   - Update OPERATOR_MANUAL.md if needed
   - Update DEVELOPMENT_HISTORY.md
```

### File Locations

**Artifacts** (agent's working documents):
- `/home/sinuhet/.gemini/antigravity/brain/<conversation-id>/task.md`
- `/home/sinuhet/.gemini/antigravity/brain/<conversation-id>/implementation_plan*.md`
- `/home/sinuhet/.gemini/antigravity/brain/<conversation-id>/walkthrough*.md`
- `/home/sinuhet/.gemini/antigravity/brain/<conversation-id>/TEST_REPORT*.md`

**Project docs** (user-facing):
- `/home/sinuhet/projekty/iris-app/IRIS_LARP/docs/`
  - `TECHNICAL_SPEC.md`
  - `DEVELOPMENT_HISTORY.md`
  - `FEATURE_LIST.md`
  - `OPERATOR_MANUAL.md`
  - `TEST_SUITE_A.md`
  - `TEST_SUITE_A_EXECUTION.md`
  - `PHASE_25_IMPLEMENTATION.md`

**Code**:
- `/home/sinuhet/projekty/iris-app/IRIS_LARP/app/` (backend)
- `/home/sinuhet/projekty/iris-app/IRIS_LARP/static/` (frontend)
- `/home/sinuhet/projekty/iris-app/IRIS_LARP/tests/` (test suites)

---

## 🔧 Code Conventions

### Backend (Python/FastAPI)

**File Organization:**
```
app/
├── main.py              # FastAPI app, lifespan, game loop
├── config.py            # Environment vars
├── database.py          # SQLAlchemy models
├── dependencies.py      # Auth helpers (get_current_user, etc.)
├── seed.py              # Database seeding
├── logic/
│   ├── gamestate.py     # Singleton for global state
│   ├── routing.py       # WebSocket routing logic
│   ├── economy.py       # Task payment, credit logic
│   └── llm_core.py      # LLM integration
├── routers/
│   ├── auth.py          # Login, logout, terminal routing
│   ├── sockets.py       # WebSocket endpoint
│   └── admin_api.py     # REST API for admin
└── templates/           # Jinja2 HTML templates
```

**Naming Conventions:**
- **Variables**: `snake_case`
- **Functions**: `snake_case`
- **Classes**: `PascalCase`
- **Constants**: `UPPER_SNAKE_CASE`
- **Enums**: `PascalCase` (members `UPPER_SNAKE_CASE`)

**Patterns:**
- **Singleton**: `GameState`, `RoutingLogic` (use `__new__` pattern)
- **Dependency Injection**: Use `Depends(get_current_admin)` for auth
- **Context Managers**: Always use `SessionLocal()` with try/finally
- **Async**: Use `async def` for WebSocket handlers and broadcasts

### Frontend (HTML/CSS/JS)

**File Organization:**
```
static/
├── css/
│   ├── terminal.css          # Base terminal styles
│   ├── admin_chernobyl.css   # Admin theme
│   └── user_themes.css       # User theme variants
└── js/
    ├── socket_client.js      # WebSocket wrapper
    ├── sound_engine.js       # Audio feedback
    └── admin_ui.js           # Admin dashboard logic
```

**Naming Conventions:**
- **CSS Classes**: `kebab-case` (e.g., `theme-card`, `god-panel`)
- **IDs**: `camelCase` (e.g., `btnTestMode`, `valShift`)
- **Variables**: `camelCase`
- **Functions**: `camelCase`

**Patterns:**
- **WebSocket**: Use `SocketClient` class from `socket_client.js`
- **DOM Updates**: Direct manipulation (no framework)
- **State Management**: Inline JavaScript in templates when simple
- **Themes**: CSS variables + body classes (e.g., `theme-party`)

---

## 🐛 Debugging Strategy

### When a Bug is Found:

1. **Reproduce**: Create minimal test case
2. **Log**: Check `server.log` and browser console
3. **Isolate**: Is it frontend, backend, or WebSocket?
4. **Fix**: Make targeted change
5. **Test**: Verify fix doesn't break other features
6. **Document**: Add to `DEVELOPMENT_HISTORY.md` "Lessons Learned"

### Common Issues:

- **WebSocket disconnect**: Check token validity, connection URL
- **Cookie issues**: Verify Path=/ in both set and delete
- **Database locks**: Always close SessionLocal() in finally blocks
- **Theme not applying**: Check body class, CSS variable scope
- **LLM errors**: Verify API keys in SystemConfig table

---

## 📝 Documentation Standards

### Implementation Plans

**Template:**
```markdown
# [Feature Name] Implementation Plan

## Goal
Brief description of what we're building.

## Proposed Changes

### Component A
- [ ] File X: Change Y
- [ ] File Z: Add feature W

### Component B
...

## Verification Plan
- [ ] ...
```

### Walkthroughs

**Template:**
```markdown
# [Phase Name] Walkthrough

## What Was Built
- Feature X
- Feature Y

## Changes Made
### Backend
- `file.py`: Added function Z

### Frontend
- `file.html`: Updated UI

## Testing
- [x] Test A: PASSED
- [x] Test B: PASSED

## Screenshots
![description](file://absolute/path.png)
```

### Test Reports

**Template:**
```markdown
# TEST REPORT: [Suite Name]

## Summary
- Total Tests: X
- Passed: Y
- Failed: Z

## Details

### Test 1: [Name]
**Status**: PASSED ✅
**Steps**: ...
**Result**: ...

### Test 2: [Name]
**Status**: FAILED ❌
**Error**: ...
**Notes**: ...
```

---

## 🚀 Deployment Checklist

Before marking a phase complete:

- [ ] All tasks in task.md marked `[x]`
- [ ] Code committed and working
- [ ] Tests passing (automated + manual)
- [ ] Documentation updated:
  - [ ] TECHNICAL_SPEC.md
  - [ ] FEATURE_LIST.md
  - [ ] DEVELOPMENT_HISTORY.md
  - [ ] OPERATOR_MANUAL.md (if user-facing changes)
- [ ] Walkthrough created
- [ ] Phase summary in `PHASE_X_IMPLEMENTATION.md`
- [ ] User notified via `notify_user`

---

## 🎯 Decision-Making Framework

### When to Create a New Phase:
- Major feature addition (e.g., AI integration, theme system)
- Significant refactoring (e.g., Grand Redesign)
- Bug fix campaign affecting multiple components

### When to Update Existing Phase:
- Minor bug fixes
- Small feature enhancements
- Documentation improvements

### When to Ask User:
- Breaking changes
- Design decisions with multiple valid approaches
- Features not clearly specified
- Budget/time tradeoffs

### When to Proceed Autonomously:
- Bug fixes (obvious root cause)
- Documentation gaps
- Test coverage improvements
- Code cleanup/refactoring (no behavior change)

---

## 🔄 Continuous Improvement

### After Each Phase:
1. Update `DEVELOPMENT_HISTORY.md` with:
   - Lessons learned
   - Technical debt identified
   - Future improvement ideas

2. Reflect on:
   - What went well?
   - What could be improved?
   - Any patterns to standardize?

3. Update this workflow document if:
   - New conventions emerged
   - Better patterns discovered  
   - Common pitfalls identified

---

## 📚 Reference Links

- **FastAPI Docs**: https://fastapi.tiangolo.com/
- **SQLAlchemy Docs**: https://docs.sqlalchemy.org/
- **Jinja2 Docs**: https://jinja.palletsprojects.com/
- **Tailwind CSS**: https://tailwindcss.com/docs

---

**Last Updated**: 2025-12-14 (Phase 33)  
**Maintainer**: Agent (Antigrav)

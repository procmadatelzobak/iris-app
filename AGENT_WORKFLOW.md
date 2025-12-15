# Agent Workflow & Rules (Consolidated v3.0)

**Primary Focus:** Development of "HLINÍK" application for IRIS LARP Project.
**Central Source of Truth:** [Organizer Wiki (Lore Web)](file:///home/sinuhet/projekty/iris-app/doc/iris/lore-web/wiki/index.html)

---

## 🌍 CENTRAL DOCUMENTATION (LORE WEB)
The **Lore Web (Organizer Wiki)** is the absolute master source for all game mechanics, role definitions, economy rules, and narrative context. 
It defines the **IRIS LARP Project**, of which the **HLINÍK application** (this repository) is a component.

**Location:** `/home/sinuhet/projekty/iris-app/doc/iris/lore-web/wiki/index.html`
**Key Sections:**
- **Roles:** Definitions of user/agent/admin archetypes.
- **Economy:** Rules for taxes, credits, and treasury.
- **System:** Documentation of backend mechanics.
- **Audit:** Compliance report (Code vs Design status).

**Usage Rules:**
1. **Game Mechanics:** Before implementing any game logic (economy, tasks, roles), **CHECK THE WIKI**. The Wiki defines how the game works. The Code must implement the Wiki's design.
2. **Roles & Context:** Use the Wiki to understand character archetypes and relations.
3. **Audit/Compliance:** Keep the "Audit" section of the Wiki updated if the Code deviates from the Design.

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
   - Check Lore Web for requirements
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
6. **Log**: Add entry to history/logs

### Common Issues:

- **WebSocket disconnect**: Check token validity, connection URL
- **Cookie issues**: Verify Path=/ in both set and delete
- **Database locks**: Always close SessionLocal() in finally blocks
- **Theme not applying**: Check body class, CSS variable scope
- **LLM errors**: Verify API keys in SystemConfig table

---

## 🚀 Deployment Checklist (Per Phase)

- [ ] All tasks in task.md marked `[x]`
- [ ] Code committed and working
- [ ] Tests passing (automated + manual)
- [ ] Documentation updated
- [ ] Walkthrough created
- [ ] User notified via `notify_user`

---

## 📝 Documentation Standards

### Implementation Plans (`implementation_plan.md`)
Describe goal, proposed changes (file by file), and verification plan.

### Walkthroughs (`walkthrough.md`)
Show what was built, changes made, testing results, and **SCREENSHOTS**.

### Test Reports (`TEST_REPORT.md`)
Summarize passed/failed tests with details on failures.

---

**Last Updated:** Phase 37 (Visualization & Stabilization)
**Maintainer:** Agent (Antigrav)

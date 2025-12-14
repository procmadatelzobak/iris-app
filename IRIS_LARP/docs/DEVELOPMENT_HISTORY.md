# IRIS LARP - Development History
**Project**: Interactive Role-playing Information System  
**Timeline**: November 2024 - December 2024  
**Current Phase**: 33

---

## Table of Contents
1. [Project Genesis](#project-genesis)
2. [Phase Timeline](#phase-timeline)
3. [Key Milestones](#key-milestones)
4. [Technical Evolution](#technical-evolution)
5. [Design Decisions](#design-decisions)

---

## 1. Project Genesis

**Concept**: A sophisticated LARP management system that facilitates communication between Players (Users), Game Operators (Agents), and Game Masters (Admins) through terminal-style interfaces with AI assistance.

**Core Innovation**: Dynamic session routing with "shift" mechanics, allowing Agents to be reassigned to different Users mid-game, creating uncertainty and emergent gameplay.

**Inspiration**: Retro computer terminals, espionage communication systems, Soviet-era control panels.

---

## 2. Phase Timeline

### Phase 1-5: Foundation (Early Development)
**Status**: Historical  
**Focus**: Basic MVP, authentication, routing

- FastAPI setup
- SQLite database schema
- JWT authentication
- Basic chat system
- Initial user/agent terminals

### Phase 6-10: Core Features
**Focus**: WebSocket integration, admin dashboard

- **Phase 6**: WebSocket real-time communication
- **Phase 7**: Admin monitoring dashboard
- **Phase 8**: Task system implementation
- **Phase 9**: Economy system (credits, lockout)
- **Phase 10**: Czech localization

### Phase 11-15: AI Integration
**Focus**: LLM features, automation

- **Phase 11**: OpenAI integration
- **Phase 12**: Message optimizer (Agent tool)
- **Phase 13**: Autopilot system
- **Phase 14**: LLM configuration UI
- **Phase 15**: Multi-provider support (OpenRouter)

### Phase 16-20: Polish & UX
**Focus**: Visual design, feedback systems

- **Phase 16**: Sound effects (typing, receive, send)
- **Phase 17**: Glitch visual effects (overload state)
- **Phase 18**: Agent terminal redesign
- **Phase 19**: User terminal refinements
- **Phase 20**: Admin dashboard tabs

### Phase 21: Admin Hub Redesign
**Features**:
- Station selection hub (Monitor, Control, Economy, Tasks)
- System log viewer
- Tabbed navigation
- Root controls for physics constants

### Phase 22: Advanced Controls
**Features**:
- Hyper Visibility modes (Normal/Blackbox/Forensic)
- Chernobyl mode variants (Normal/Low Power/Overclock)
- Power consumption system
- Agent response timer

### Phase 23: Complex Flows
**Features**:
- **AI Optimizer Confirm Flow**: Agents preview optimized text before sending
- **Task Editing**: Admins modify task prompts during approval
- **System Reset**: ROOT button to wipe logs and reset economy
- **Economic Lockout UI**: Red overlay when User is locked

**Testing**: Automated test suite (`test_phase23_complex.py`)

### Phase 24: Grand Redesign (User Phase 23)
**Theme Overhaul**:
- **Admin**: "Chernobyl Console" aesthetic (retro-industrial, greens, Czech labels)
- **Users**: 4 theme variants (Low/Mid/High/Party)
  - Party mode includes animated bubbles
- **Agents**: "Retro-Functional" monochrome style

**Features**:
- Editable admin labels
- Network graph (Canvas API)
- Status level economy controls
- Theme switching via WebSocket

**Challenges**: Browser session persistence issues during testing

### Phase 25: ROOT Console & Documentation (CURRENT)
**Focus**: Developer tools, comprehensive documentation, test coverage

**Sprint 1: ROOT Dashboard**
- ✅ CONFIG tab with Test Mode toggle
- ✅ Developer Mode UI (quick login buttons)
- ✅ AI configuration panel (Optimizer prompt, Autopilot model)
- ✅ System information display

**Sprint 2: Backend API**
- ✅ `/api/admin/root/ai_config` endpoints
- ✅ Integration with gamestate

**Sprint 3: Documentation** (In Progress)
- ✅ Technical Specification
- ✅ Development History (this document)
- ⏳ Test Plan
- ⏳ Operator Manual updates

**Sprint 4: Test Suite A**
- ⏳ End-to-end test execution
- ⏳ Gap analysis and fixes

### Phase 30: UI Fixes & Documentation Viewer
**Focus**: Bug fixes and context-aware documentation

**Bug Fixes**:
- ✅ Fixed "Rewrite Reality" (Edit Mode) toggle not turning off
- ✅ Fixed unresponsive admin dashboard controls (sliders, mode switches)
- ✅ Added visual feedback for mode button states

**Features**:
- ✅ In-app documentation viewer with Markdown rendering
- ✅ Role-based styling (User green, Agent pink, Admin gold)
- ✅ MANUÁL and SYSTEM DOCS buttons in all terminals

### Phase 31: System Hardening & State Persistence
**Focus**: Reliability, security, and deployment readiness

**State Persistence**:
- ✅ `export_state()` / `import_state()` methods in GameState
- ✅ Auto-save on shutdown to `data/gamestate_dump.json`
- ✅ Auto-restore on startup

**Error Handling**:
- ✅ Game loop wrapped in try-except (never crashes)
- ✅ 5-second pause on error to prevent log flood

**Security**:
- ✅ SECRET_KEY validation in config
- ✅ Production mode blocks default key

**Documentation**:
- ✅ DEPLOYMENT.md created with single-worker requirement

### Phase 32: Advanced Task Lifecycle & Economy (CURRENT)
**Focus**: Complete task system with LLM generation and grading

**LLM Task Generation**:
- ✅ `generate_task_description()` in llm_core.py
- ✅ Auto-generates task based on user status level
- ✅ Fallback to default prompt if LLM unavailable

**Grading System**:
- ✅ `/tasks/grade` endpoint with rating_modifier (0.0/0.5/1.0/2.0)
- ✅ Admin grading modal with split view (prompt | submission)
- ✅ 4 rating buttons: ⛔0%, ⚠️50%, ✅100%, 🌟200%

**Economy Integration**:
- ✅ Reward calculated: `reward_offered * rating_modifier`
- ✅ Tax deducted and added to treasury
- ✅ ChatLog and SystemLog entries created

**Root Configuration**:
- ✅ Economy tab for reward amounts per status level
- ✅ `update_reward_config()` method in GameState

### Phase 33: Automated E2E Test Suite A (CURRENT)
**Focus**: Playwright-based automated testing

**Test Infrastructure**:
- ✅ `tests/e2e/conftest.py` with server fixture
- ✅ pytest-playwright integration
- ✅ Clean DB seeding before tests

**Test Coverage**:
- ✅ Block 0-7 of TEST_SUITE_A.md
- ✅ Login flows, task lifecycle, optimizer
- ✅ Purgatory mode (debt/redemption)
- ✅ UI assertions (toasts, overlays, buttons)

**Run Scripts**:
- ✅ `run_suite_a.sh` (headed + CI modes)

---

## 3. Key Milestones

### Milestone 1: First Functional Chat (Phase 6)
**Date**: ~November 2024  
**Achievement**: WebSocket-based real-time communication between User and Agent

### Milestone 2: AI Integration (Phase 12)
**Date**: ~Mid-November 2024  
**Achievement**: First LLM-powered message rewriting

### Milestone 3: Economy System (Phase 9)
**Date**: ~Late November 2024  
**Achievement**: Credit-based task system with lockout mechanism

### Milestone 4: Purgatory Mode (Phase 25)
**Date**: December 13, 2024  
**Achievement**: Debt lockout allows task access but blocks chat

### Milestone 5: Test Mode & ROOT Console (Phase 25)
**Date**: December 14, 2025  
**Achievement**: Developer-friendly testing tools with comprehensive system configuration

---

## 4. Technical Evolution

### 4.1 Architecture Decisions

**Why FastAPI?**
- Modern Python async framework
- Built-in WebSocket support
- Automatic OpenAPI documentation
- Type hints with Pydantic validation

**Why SQLite?**
- Simple deployment (no separate DB server)
- Sufficient for 8-16 concurrent users
- Easy backup (single file)
- Good for LARP event duration (hours, not years)

**Why Vanilla JavaScript?**
- No build step required
- Direct browser debugging
- Faster iteration during development
- Fits retro/terminal aesthetic

### 4.2 Design Patterns

**Singleton GameState**:
- Single source of truth for global state
- Avoids database overhead for frequently-changing values (shift, temperature)
- Thread-safe via Python's inherent single-threaded execution

**Routing Logic Singleton**:
- Centralized WebSocket connection management
- Session-to-connection mapping
- Broadcast utilities

**Dependency Injection (FastAPI)**:
- Clean separation of auth logic
- Reusable `get_current_admin`, `get_current_user_cookie`
- Easy testing with overrides

### 4.3 Technology Choices Over Time

| Phase | Technology Added | Reason |
|-------|------------------|--------|
| 1     | FastAPI + SQLAlchemy | Rapid prototyping |
| 6     | WebSockets | Real-time chat requirement |
| 11    | OpenAI API | Message optimization feature |
| 15    | OpenRouter | Cost-effective autopilot (free models) |
| 16    | Web Audio API | Sound feedback for immersion |
| 20    | Tailwind CSS | Rapid UI iteration |
| 24    | Canvas API | Network graph visualization |

---

## 5. Design Decisions

### 5.1 Session Routing

**Problem**: How to assign 8 Agents to 8 Users dynamically?

**Rejected Solutions**:
- Manual assignment (too slow)
- Random assignment (no control)
- Fixed pairing (no flexibility)

**Chosen Solution**: **Shift-based rotation**
- Formula: `AgentSession = (AgentID - 1 + Shift) % 8 + 1`
- Allows mid-game reassignment
- Predictable but not obvious to players
- Single control (shift offset) affects all mappings

### 5.2 AI Optimizer Flow

**Problem**: How to give Agents control over AI-rewritten messages?

**Rejected Solutions**:
- Auto-send optimized text (no agency)
- Always show both versions (clutter)

**Chosen Solution**: **Preview → Confirm/Reject**
- Agent sees original + rewritten
- Explicit opt-in per message
- Input locked during preview (prevents accidental send)
- Immunity to Reports as bonus for using AI

### 5.3 Purgatory vs Full Lockout

**Problem**: Users with negative credits blocked from gameplay.

**Rejected Solutions**:
- Allow chat and tasks (no consequence)
- Full lockout (frustrating, no recovery path)

**Chosen Solution**: **Purgatory Mode**
- Block chat (punishment)
- Allow tasks (redemption path)
- Overlay explains situation
- Automatic unlock when credits > 0

### 5.4 Test Mode Implementation

**Problem**: Testing requires logging in/out as different users repeatedly.

**Rejected Solutions**:
- Store multiple users in browser (complex)
- Auto-login based on URL param (security risk)

**Chosen Solution**: **ROOT-controlled toggle**
- Only accessible by ultimate admin
- Shows quick-login buttons when enabled
- Auto-fills seeded passwords via JS
- Clear visual indicator (yellow warning banner)

### 5.5 Theme System

**Problem**: How to visually distinguish user status/wealth?

**Rejected Solutions**:
- Different terminals per level (maintenance nightmare)
- Server-side CSS generation (performance)

**Chosen Solution**: **CSS Variables + Body Classes**
- Single `user_terminal.html` template
- `<body class="theme-{status_level}">`
- CSS variables define colors per theme
- WebSocket message triggers class change
- Bubble animation injected via JS for Party mode

---

## 6. Lessons Learned

### 6.1 What Worked Well

✅ **FastAPI's async support**: Made WebSocket handling elegant  
✅ **Singleton pattern**: Simple and effective for game state  
✅ **CSS theming**: Easy to maintain, performant  
✅ **Jinja2 templates**: Good balance of logic and presentation  
✅ **Test-driven for complex flows**: Phase 23 test suite caught many bugs

### 6.2 Challenges

⚠️ **Browser session persistence**: Cookie handling across logins was tricky  
⚠️ **WebSocket edge cases**: Disconnect/reconnect handling required iteration  
⚠️ **LLM cost**: Autopilot can get expensive; added free model support  
⚠️ **Database migrations**: SQLite doesn't support ALTER easily; relied on reset during dev  
⚠️ **Visual testing**: Automated browser tests are flaky; manual verification critical

### 6.3 Technical Debt

- **No database migrations**: Using seed + manual schema updates
- **Frontend state management**: Vanilla JS gets messy at scale
- **Error handling**: Could be more comprehensive (especially WebSocket errors)
- **Logging**: Console-based; should use Python logging module
- **Tests**: More unit tests needed (currently heavy on integration tests)

---

## 7. Future Considerations

### Potential Enhancements
- **Multi-event support**: Save/load different game states
- **Replay mode**: View historical chats for debriefing
- **Agent handoff**: Mid-shift Agent replacement mechanism
- **Advanced AI**: Context-aware responses based on game phase
- **Mobile optimization**: Touch-friendly interface for tablets

### Architecture Improvements
- **Redis for session state**: Better scalability
- **PostgreSQL migration**: More robust for production
- **Separate WebSocket server**: Horizontal scaling
- **Frontend framework**: React/Vue for complex state management

---

## 8. Contributors & Credits

**Development Team**: (Names/credits as appropriate)

**Special Thanks**:
- FastAPI community
- OpenRouter for free tier
- Tailwind CSS team
- Testing volunteers

---

**Document Version**: Phase 31.0  
**Last Updated**: 2025-12-14  
**Status**: Living Document

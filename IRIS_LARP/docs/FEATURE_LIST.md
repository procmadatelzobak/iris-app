# IRIS LARP - Complete Feature List
**Version:** Phase 31.0  
**Last Updated:** 2025-12-14

---

## Table of Contents
1. [Core Features](#core-features)
2. [User Features](#user-features)
3. [Agent Features](#agent-features)
4. [Admin Features](#admin-features)
5. [ROOT Features](#root-features)
6. [AI Features](#ai-features)
7. [UI/UX Features](#uiux-features)

---

## 1. Core Features

### Authentication & Authorization
- ✅ JWT-based authentication
- ✅ HTTP-only cookie sessions
- ✅ Role-based access control (User/Agent/Admin/Root)
- ✅ Automatic terminal routing based on role
- ✅ Secure logout with cookie cleanup

### Real-Time Communication
- ✅ WebSocket-based instant messaging
- ✅ Session-based chat (8 isolated channels)
- ✅ Dynamic agent routing via global shift offset
- ✅ Message history persistence
- ✅ Typing indicators (User & Agent mirroring)

### Economy System
- ✅ Credit-based user economy (default: 100 credits)
- ✅ Task-based rewards
- ✅ Configurable tax rate (default: 20%)
- ✅ Treasury management (admin-controlled)
- ✅ **Purgatory Mode**: Automatic lockout when credits < 0
- ✅ Auto-unlock when credits restored

### Task System
- ✅ User task requests (WebSocket)
- ✅ Admin task approval with custom descriptions
- ✅ Task status tracking (Pending/Active/Completed/Paid/Rejected)
- ✅ Configurable task rewards
- ✅ Task submission and payment flow
- ✅ Task editing during approval
- ✅ Rating-based payment (0-100%)

---

## 2. User Features

### Terminal Interface
- ✅ Retro terminal aesthetic
- ✅ **4 Theme Variants**: Low (basic), Mid (nature), High (luxury), Party (chaos)
- ✅ CRT scan-line effects
- ✅ Dynamic theme switching via WebSocket
- ✅ Logout button

### Communication
- ✅ Send/receive messages to/from assigned agent
- ✅ Real-time message updates
- ✅ **Report System**: Flag inappropriate agent messages
  - ✅ Report immunity for AI-optimized messages
- ✅ Typing indicator broadcast

### Status Display
- ✅ Credit balance indicator
- ✅ Task status display (None/Pending/Active)
- ✅ System overload warnings (visual glitch effects)

### Task Management
- ✅ "Request New Task" button
- ✅ Task description display when active
- ✅ Task submission textarea
- ✅ Submit button with confirmation

### Purgatory Mode (Debt Lockout)
- ✅ **Chat Blocked**: Red overlay on chat panel when locked
- ✅ **Tasks Allowed**: Can still request & submit tasks
- ✅ Automatic unlock when balance restored
- ✅ Clear messaging ("COMMUNICATION OFFLINE", "DEBT RECOVERY REQUIRED")

### Party Mode (Status: Party)
- ✅ Pink/rainbow color scheme
- ✅ Animated bubbles background
- ✅ Dynamic visual effects

---

## 3. Agent Features

### Terminal Interface
- ✅ Retro-functional monochrome design
- ✅ Session ID indicator
- ✅ Global shift display
- ✅ Logout button

### Communication
- ✅ Send/receive messages to/from assigned user
- ✅ Message history (filtered by visibility mode)
- ✅ Typing indicator broadcast
- ✅ **Typing Sync**: Real-time input mirroring across devices

### AI Tools
- ✅ **Message Optimizer**:
  - Preview optimized version before sending
  - Confirm/Reject workflow
  - Locks input during optimization
  - Grants report immunity
- ✅ **Autopilot Mode**:
  - AI auto-responds to users
  - Toggle ON/OFF per agent
  - Maintains conversation context
  - Uses configurable LLM model

### Status Display
- ✅ **Response Timer**: Yellow progress bar (configurable deadline)
- ✅ **Session ID**: Shows which user the agent is assigned to
- ✅ **Shift Offset**: Displays current routing shift
- ✅ Autopilot indicator (ON/OFF state)

### Visibility Modes
- ✅ **NORMAL**: Full chat history visible
- ✅ **BLACKBOX**: No history, blind responses
- ✅ **FORENSIC**: Enhanced view (reserved for future)
- ✅ **EPHEMERAL**: (reserved for future)

---

## 4. Admin Features

### Dashboard Structure
- ✅ **Hub View**: 4-station selection (Monitor/Control/Economy/Tasks)
- ✅ **Chernobyl Console Theme**: Retro-industrial aesthetic
- ✅ **Editable Labels**: Customize Czech "nonsense" labels
- ✅ **Navigation Tabs**: Switch between stations
- ✅ Logout button

### Station 1: Monitor (Panopticon)
- ✅ **Overview Tab**: Split view (Sessions + Mini Log)
- ✅ **Chats Tab**: Live chat grid (8 sessions)
- ✅ **System Logs Tab**: Filterable event log
- ✅ Real-time message updates
- ✅ Color-coded log events (ACTION/ROOT/REPORT/TASK)
- ✅ "Reset Log" button

### Station 2: Controls
- ✅ **Agency Operation Mode**: Normal/Low Power/Overclock
- ✅ **Visibility Protocols**: Control agent history visibility
- ✅ **Temperature Meter**: Manual override (slider 0-350+)
- ✅ **Shift Execution**: ">> EXECUTE SHIFT >>" button
- ✅ **AI Optimizer**: Toggle ON/OFF, custom prompt
- ✅ **Agent Response Timer**: Configure deadline (seconds)

### Station 3: Economy
- ✅ User credit grid display
- ✅ **Fine/Bonus**: Grant or deduct credits
- ✅ **Lock/Unlock**: Manual user lockout toggle
- ✅ **Status Level Buttons**: Set theme (L/M/H/P)
- ✅ Real-time balance updates

### Station 4: Tasks
- ✅ Pending tasks list
- ✅ **Approve**: Edit description & set reward
- ✅ **Pay**: Rate completion (0-100%) and pay reward
- ✅ **Reject**: Deny task
- ✅ Task history view

### System Controls
- ✅ **Global Broadcast**: Send message to all users
- ✅ **System Reset**: Wipe logs, reset credits, clear tasks
- ✅ **Force Shift**: Increment routing offset

### Network Graph
- ✅ Canvas-based visualization of User-Agent connections
- ✅ Updates on shift changes

---

## 5. ROOT Features

### ROOT Dashboard
- ✅ Dedicated elite admin interface
- ✅ Gold/black color scheme
- ✅ **5 Tabs**: Dashboard, CONFIG, Economy, Chronos, Panopticon

### CONFIG Tab (Developer Tools)
- ✅ **Test Mode Toggle**: Enable/disable quick login buttons
  - Shows all user buttons on login screen
  - Auto-fills seeded passwords
  - One-click login for testing
- ✅ **AI Configuration**:
  - Optimizer prompt customization
  - Autopilot model selection
  - Save/load config via API
- ✅ **System Information**: Version, user count, database type

### Dashboard Tab
- ✅ **System Status**: Shift offset, online users, temperature
- ✅ **Physics Constants**: Tax rate, power capacity tuning
- ✅ **Executive Protocols**:
  - Force shift
  - Global broadcast
  - System reset (NUKE)
  - Reload UI
- ✅ **System Log Stream**: Real-time log viewer

### Economy Tab
- ✅ **Global Economy**:
  - Stimulus packages (+100, +1000)
  - Taxation (-100)
  - Reset all credits
- ✅ **Individual Editor**: Per-user credit/status management

### Chronos Tab (Time Manipulation)
- ✅ Current shift display (large)
- ✅ **Jump to Shift**: Set specific shift value
- ✅ **Temperature Override**: Slider (0-200%)

### Panopticon Tab
- ✅ 8x8 grid of all sessions
- ✅ Raw chat view
- ✅ User status indicators

---

## 6. AI Features

### LLM Integration
- ✅ **Multi-Provider Support**:
  - OpenAI (GPT-4o, GPT-4o-mini)
  - OpenRouter (Gemini, various models)
  - Gemini (Direct API)
- ✅ **Dynamic API Key Management**: Store keys in database
- ⚠️ **Two LLM Configs** (Backend):
  - Task Evaluator (default: GPT-4o) - API exists, UI not exposed
  - Hyper/Autopilot (default: Gemini Flash) - Partial UI (model only)

### ROOT Dashboard AI Configuration (CONFIG Tab)
- ✅ **Optimizer Prompt**: Customizable prompt for message rewriting
- ⚠️ **Autopilot Model Selection**: Only model name, no provider selection
- ❌ **Task Evaluator LLM Config**: Not exposed in ROOT UI
- ❌ **Per-Role LLM Provider Selection**: Not implemented in UI
- ✅ **OpenAI API Key**: Input field available
- ✅ **OpenRouter API Key**: Input field available
- ❌ **Gemini API Key**: Backend support exists, UI input missing

### Message Optimizer
- ✅ Rewrites agent messages in custom tone/style
- ✅ Preview-Confirm-Reject workflow
- ✅ Configurable system prompt (ROOT/Admin)
- ✅ Grants report immunity
- ⚠️ Uses hardcoded model (no separate config from HYPER)

### Autopilot
- ✅ AI-driven automatic responses
- ✅ Maintains per-session context
- ⚠️ Configurable model selection (partial - model only, not provider)
- ✅ Toggle per agent

---

## 7. UI/UX Features

### Visual Design
- ✅ **Retro Terminal Aesthetic**: Monospace fonts, green/amber text
- ✅ **CRT Effects**: Scan lines, overlays
- ✅ **Theme System**: CSS variables for easy customization
- ✅ **Responsive Layout**: Flexbox-based design

### Feedback Systems
- ✅ **Sound Effects**:
  - Typing sounds
  - Message send/receive tones
  - Error beeps
- ✅ **Visual Indicators**:
  - Glitch effects on overload
  - Progress bars (timer, temperature)
  - Status badges (locked, active)
- ✅ **Toast Notifications**: Context-specific alerts

### Animations
- ✅ **Party Bubbles**: Animated .png bubbles for Party theme
- ✅ **Glitch Effects**: Zalgo text, screen shake on overload
- ✅ **Fade Transitions**: Smooth tab/view switching
- ✅ **Pulse Effects**: Attention-grabbing indicators

### Accessibility
- ✅ **High Contrast**: Clear text against backgrounds
- ✅ **Status Indicators**: Multiple cues (color + text + icons)
- ✅ **Keyboard Navigation**: Tab-friendly forms

### Localization
- ✅ **Czech Language**: All UI elements translated
- ✅ **Editable Labels**: Admin can customize Czech "nonsense" terms
- ✅ **Consistent Terminology**: Unified vocabulary across terminals

---

## 8. Developer Features

### Test Mode
- ✅ Quick login buttons (ROOT-controlled toggle)
- ✅ Auto-fill seeded passwords
- ✅ One-click user/agent/admin switching
- ✅ Visual indicator when active

### Debugging Tools
- ✅ System logs (database + console)
- ✅ ROOT panopticon (all sessions visible)
- ✅ Network graph visualization
- ✅ Browser console integration

### Deployment
- ✅ `install.sh`: Automated setup
- ✅ `run.sh`: One-command startup
- ✅ SQLite (single-file database)
- ✅ No external dependencies (Docker-free)

---

## 9. Power & Performance

### Power System
- ✅ **Load Calculation**: Base + per-user + per-autopilot + features
- ✅ **Capacity Management**: Configurable power cap
- ✅ **Overload Detection**: Load > Cap triggers glitches
- ✅ **Visual Feedback**: Admin power bar, user glitch effects

### Temperature System
- ✅ **Range**: 20-1000 (threshold at 350)
- ✅ **Decay Modes**:
  - Normal: -0.5/s
  - Low Power: -1.5/s
  - Overclock: +0.1/s
- ✅ **Overload Trigger**: Temp > 350 activates glitches
- ✅ **Manual Override**: ROOT/Admin slider control

### Performance Optimizations
- ✅ **Singleton Pattern**: GameState, Routing Logic
- ✅ **Broadcast Optimization**: Only send on state change
- ✅ **Session Management**: Efficient WebSocket connection pooling

### State Persistence (Phase 31)
- ✅ **GameState Export/Import**: Serialize and restore critical state
- ✅ **Auto-Save on Shutdown**: State saved to `data/gamestate_dump.json`
- ✅ **Auto-Restore on Startup**: State loaded from JSON file
- ✅ **Error Recovery**: Game loop continues after exceptions

### Security (Phase 31)
- ✅ **SECRET_KEY Validation**: Warning in dev, error in production
- ✅ **Production Mode Check**: `IRIS_ENV=production` requires secure key

### Documentation (Phase 31)
- ✅ **In-App Manuals**: Markdown viewer with role-based styling
- ✅ **DEPLOYMENT.md**: Single-worker requirement documented

---

## Feature Status Legend
- ✅ **Implemented & Tested**
- ⚠️ **Partial Implementation** (Backend exists, UI incomplete)
- 🔄 **In Progress**
- ❌ **Planned, Not Started** / **Missing**

---

**Total Features**: 160+  
**Last Major Update**: Phase 31 (System Hardening, State Persistence)
